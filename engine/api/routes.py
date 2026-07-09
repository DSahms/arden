"""PersonaLock FastAPI Application - Phase 1

Endpoints:
- POST /chat - Main conversation endpoint with memory
- GET /health - System health check
- GET /persona/current - Current persona info
- GET /memory/recent - Recent conversations
"""
import os
import time
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import PersonaLock components
from llm.inference import get_completion
from memory.memory_vault import MemoryVault
from memory.embeddings import EmbeddingManager
from core.personality_engine import PersonalityEngine

# Global instances (initialized on startup)
memory_vault: Optional[MemoryVault] = None
_embedding_manager: Optional[EmbeddingManager] = None
personality_engine: Optional[PersonalityEngine] = None


def get_embedding_manager() -> Optional[EmbeddingManager]:
    """Lazy initialization of EmbeddingManager to avoid startup hang."""
    global _embedding_manager
    if _embedding_manager is None:
        try:
            _embedding_manager = EmbeddingManager()
            if not _embedding_manager.is_connected():
                logger.warning("EmbeddingManager (ChromaDB) not properly connected")
                _embedding_manager = None
        except Exception as e:
            logger.warning(f"EmbeddingManager initialization failed: {e}")
            _embedding_manager = None
    return _embedding_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global memory_vault, personality_engine
    
    logger.info("Starting PersonaLock API...")
    
    # Initialize PersonalityEngine (always works - uses defaults)
    personality_engine = PersonalityEngine()
    logger.info(f"PersonalityEngine initialized with persona: {personality_engine.get_active_persona().name}")
    
    # Initialize MemoryVault (Neo4j) - graceful degradation if unavailable
    try:
        memory_vault = MemoryVault()
        if memory_vault.is_connected():
            logger.info("MemoryVault (Neo4j) connected successfully")
        else:
            logger.warning("MemoryVault (Neo4j) connection failed - continuing without persistent memory")
            memory_vault = None
    except Exception as e:
        logger.warning(f"MemoryVault initialization failed: {e} - continuing without persistent memory")
        memory_vault = None
    
    # EmbeddingManager (ChromaDB) - lazy initialization to avoid startup hang
    # Will be initialized on first use via get_embedding_manager()
    logger.info("EmbeddingManager will be initialized lazily on first use")
    
    logger.info("PersonaLock API ready")
    
    yield
    
    # Cleanup
    logger.info("Shutting down PersonaLock API...")
    if memory_vault:
        memory_vault.close()


app = FastAPI(
    title="PersonaLock API",
    description="Local-first AI companion with persistent memory and stable personality",
    version="0.1.0",
    lifespan=lifespan
)


# ============================================
# Request/Response Models
# ============================================

class ChatRequest(BaseModel):
    message: str
    user_id: str


class ChatResponse(BaseModel):
    response: str
    processing_time_ms: int


class HealthStatus(BaseModel):
    status: str
    neo4j: str
    chromadb: str
    llm: str
    details: Dict[str, Any] = {}


class PersonaInfo(BaseModel):
    name: str
    traits: Dict[str, float]
    description: str


class ConversationRecord(BaseModel):
    uid: str
    user_message: str
    assistant_response: str
    timestamp: str
    metadata: Dict[str, Any] = {}


# ============================================
# Endpoints
# ============================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main conversation endpoint.
    
    Flow:
    1. Load persona system prompt from PersonalityEngine
    2. Query ChromaDB for relevant memories using user's message
    3. Build context from retrieved memories
    4. Call get_completion() with user_message, system_prompt, conversation_history
    5. Store the exchange in Neo4j via MemoryVault
    6. Store embedding in ChromaDB via EmbeddingManager
    7. Return the response
    """
    start_time = time.time()
    
    try:
        # Step 1 & 2: Get memory context from ChromaDB
        memory_context = ""
        embedding_mgr = get_embedding_manager()
        if embedding_mgr:
            try:
                memory_context = embedding_mgr.get_relevant_context(
                    query=request.message,
                    user_id=request.user_id,
                    max_results=3
                )
                logger.debug(f"Retrieved memory context: {len(memory_context)} chars")
            except Exception as e:
                logger.warning(f"Failed to retrieve memory context: {e}")
        
        # Step 3: Build system prompt with persona and memory context
        system_prompt = personality_engine.get_system_prompt(memory_context=memory_context)
        
        # Step 4: Get conversation history from Neo4j (optional)
        conversation_history = []
        if memory_vault:
            try:
                conversation_history = memory_vault.get_conversation_history(
                    user_id=request.user_id,
                    limit=5  # Last 5 exchanges
                )
            except Exception as e:
                logger.warning(f"Failed to retrieve conversation history: {e}")
        
        # Step 5: Call LLM
        try:
            response_text = get_completion(
                user_message=request.message,
                system_prompt=system_prompt,
                conversation_history=conversation_history if conversation_history else None
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
        
        # Step 6: Store in Neo4j
        if memory_vault:
            try:
                memory_vault.store_conversation(
                    user_id=request.user_id,
                    user_message=request.message,
                    assistant_response=response_text
                )
            except Exception as e:
                logger.warning(f"Failed to store conversation in Neo4j: {e}")
        
        # Step 7: Store embedding in ChromaDB
        if embedding_mgr:
            try:
                embedding_mgr.store_conversation(
                    user_id=request.user_id,
                    user_message=request.message,
                    assistant_response=response_text
                )
            except Exception as e:
                logger.warning(f"Failed to store embedding in ChromaDB: {e}")
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ChatResponse(
            response=response_text,
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Check health of all system components.
    
    - Check Neo4j connection
    - Check ChromaDB connection
    - Check LLM availability (simple test completion)
    """
    status = "healthy"
    details = {}
    
    # Check Neo4j
    neo4j_status = "disconnected"
    if memory_vault:
        try:
            if memory_vault.is_connected():
                neo4j_status = "connected"
                details["neo4j_uri"] = memory_vault.uri
        except Exception as e:
            neo4j_status = f"error: {str(e)}"
            status = "degraded"
    else:
        neo4j_status = "not_initialized"
        status = "degraded"
    
    # Check ChromaDB
    chromadb_status = "disconnected"
    embedding_mgr = get_embedding_manager()
    if embedding_mgr:
        try:
            if embedding_mgr.is_connected():
                chromadb_status = "connected"
                details["chromadb_documents"] = embedding_mgr.count()
        except Exception as e:
            chromadb_status = f"error: {str(e)}"
            status = "degraded"
    else:
        chromadb_status = "not_initialized"
        status = "degraded"
    
    # Check LLM
    llm_status = "unknown"
    try:
        # Simple test completion
        test_response = get_completion(
            user_message="Say 'ok' and nothing else.",
            system_prompt="You are a test. Respond with only 'ok'.",
            max_tokens=10
        )
        if test_response:
            llm_status = "operational"
            details["llm_provider"] = os.environ.get("LLM_PROVIDER", "unknown")
            details["llm_model"] = os.environ.get("LLM_MODEL", "unknown")
    except Exception as e:
        llm_status = f"error: {str(e)}"
        status = "unhealthy"
    
    return HealthStatus(
        status=status,
        neo4j=neo4j_status,
        chromadb=chromadb_status,
        llm=llm_status,
        details=details
    )


@app.get("/persona/current", response_model=PersonaInfo)
async def get_current_persona():
    """Return the currently loaded persona name and traits."""
    info = personality_engine.get_persona_info()
    return PersonaInfo(
        name=info["name"],
        traits=info["traits"],
        description=info["description"]
    )


@app.get("/memory/recent", response_model=List[ConversationRecord])
async def get_recent_memory(limit: int = 10, user_id: Optional[str] = None):
    """Return recent conversations from Neo4j."""
    if not memory_vault:
        raise HTTPException(
            status_code=503,
            detail="Memory vault (Neo4j) not available"
        )
    
    try:
        conversations = memory_vault.get_recent_conversations(
            user_id=user_id,
            limit=limit
        )
        return [
            ConversationRecord(
                uid=conv["uid"],
                user_message=conv["user_message"],
                assistant_response=conv["assistant_response"],
                timestamp=conv["timestamp"],
                metadata=conv.get("metadata", {})
            )
            for conv in conversations
        ]
    except Exception as e:
        logger.error(f"Failed to retrieve recent memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Additional utility endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "PersonaLock API",
        "version": "0.1.0",
        "status": "running",
        "persona": personality_engine.get_active_persona().name if personality_engine else "unknown"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
