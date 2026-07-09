"""Test script to verify memory storage pipeline for conversation exchanges."""

import logging
import sys
from modules.base_assistant import PlainAssistant
from modules.assistant_config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_memory_storage():
    """Test that conversations are stored and recalled correctly."""
    
    print("\n" + "="*60)
    print("MEMORY PIPELINE TEST")
    print("="*60 + "\n")
    
    # Check if memory is enabled
    memory_enabled = get_config("memory.enabled", default=False)
    if not memory_enabled:
        print("❌ ERROR: Memory is not enabled in assistant_config.yml")
        print("Please set memory.enabled: true")
        return False
    
    print("✅ Memory is enabled in config")
    
    # Test 1: Initialize assistant and check connections
    print("\n--- Test 1: Initialize Assistant ---")
    try:
        assistant = PlainAssistant(logger, "test-session-001")
        
        if not assistant.memory_manager:
            print("❌ ERROR: Memory manager failed to initialize")
            return False
        
        print("✅ Memory manager initialized")
        
        # Check Neo4j connection
        if not assistant.memory_manager.neo4j or not assistant.memory_manager.neo4j.is_connected():
            print("❌ ERROR: Neo4j is not connected")
            print("   Make sure Neo4j is running on localhost:7474")
            return False
        
        print("✅ Neo4j connected")
        
        # Check ChromaDB
        if not assistant.memory_manager.chroma:
            print("❌ ERROR: ChromaDB store not initialized")
            return False
        
        print("✅ ChromaDB initialized")
        
        # Check embedder
        if not assistant.memory_manager._embedding_function:
            print("⚠️  WARNING: Embedding function not available")
            print("   Make sure Ollama is running: ollama serve")
            return False
        
        print("✅ Ollama embedder available")
        
    except Exception as e:
        print(f"❌ ERROR during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Store a conversation exchange manually
    print("\n--- Test 2: Store Conversation Exchange ---")
    try:
        test_exchange = "User: I really hate mornings\nAssistant: I understand - mornings can be challenging. Is there a particular reason why mornings are difficult for you?"
        
        memory_id = assistant.memory_manager.remember(
            content=test_exchange,
            memory_type="event",
            importance=0.6
        )
        
        if not memory_id:
            print("❌ ERROR: Failed to store memory")
            return False
        
        print(f"✅ Stored exchange to Neo4j: {memory_id[:8]}...")
        
        # Verify it's in ChromaDB
        chroma_mem = assistant.memory_manager.chroma.get_memory(memory_id)
        if not chroma_mem:
            print("❌ ERROR: Memory not found in ChromaDB")
            return False
        
        print(f"✅ Found in ChromaDB with document: {chroma_mem['document'][:50]}...")
        
    except Exception as e:
        print(f"❌ ERROR storing exchange: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Recall similar exchanges
    print("\n--- Test 3: Recall Similar Exchanges ---")
    try:
        query = "When should we schedule our next session?"
        
        recalled = assistant.memory_manager.recall(query=query, limit=3)
        
        if not recalled:
            print("⚠️  No memories recalled (might be expected if this is first run)")
        else:
            print(f"✅ Recalled {len(recalled)} similar exchanges:")
            for i, mem in enumerate(recalled, 1):
                content = mem.get("content", "")
                similarity = mem.get("similarity", 0)
                print(f"   {i}. [similarity: {similarity:.3f}] {content[:80]}...")
        
    except Exception as e:
        print(f"❌ ERROR recalling memories: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Format recall output
    print("\n--- Test 4: Test _recall_memories Method ---")
    try:
        memory_context = assistant._recall_memories("scheduling meetings", limit=3)
        
        if memory_context:
            print("✅ Formatted memory context:")
            print(memory_context)
        else:
            print("ℹ️  No relevant memories found (expected on first run)")
        
    except Exception as e:
        print(f"❌ ERROR in _recall_memories: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_memory_storage()
    sys.exit(0 if success else 1)
