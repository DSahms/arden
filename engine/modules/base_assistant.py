from typing import List, Dict, Optional, Any
import logging
import os
import threading
import time
from modules.utils import build_file_name_session
from modules.assistant_config import get_config
from modules.task_manager import TaskManager, Priority
from modules.morning_briefing import MorningBriefing

# Brain Backend imports
from modules.brain_backends import BrainFactory
from modules.brain_backends.base_backend import BaseBrainBackend

# Stability imports
from modules.stability_helpers import (
    SimpleErrorHandler,
    ImprovedWakeWordDetector,
    get_friendly_error_message
)

# Memory Vault imports (optional, graceful degradation if not configured)
try:
    from modules.memory_vault.memory_manager import MemoryManager
    from modules.memory_vault.memory_factory import create_graph_store
    from modules.memory_vault.chroma_store import ChromaStore
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    MemoryManager = None

# Embedding utility for Ollama (used for dependency injection into MemoryManager)
from utils.embedding_utils import OllamaEmbedder

# Personality Engine imports (optional, graceful degradation if not configured)
try:
    from modules.personality_engine import PersonalityEngine, get_arden_profile
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False
    PersonalityEngine = None

AVAILABLE_BACKENDS = [
    "kobold", "lm_studio", "ollama", "groq", "claude", "openai", "venice", "gemini",
]


class PlainAssistant:
    def __init__(self, logger: logging.Logger, session_id: str):
        self.logger = logger
        self.session_id = session_id
        self.conversation_history = []
        self._last_memory_id: Optional[str] = None
        self._memory_lock = threading.Lock()

        # Get voice configuration
        self.voice_type = get_config("base_assistant.voice")
        self.elevenlabs_voice = get_config("base_assistant.elevenlabs_voice", default="")
        self.brain = get_config("base_assistant.brain")

        # --- MEMORY VAULT INITIALIZATION ---
        self.memory_manager: Optional[MemoryManager] = None
        if MEMORY_AVAILABLE:
            memory_enabled = get_config("memory.enabled", default=False)
            if memory_enabled:
                self.logger.info("[MEMORY] Initializing Memory Vault...")
                try:
                    memory_backend = get_config("memory.backend", default="neo4j")
                    chroma_dir = get_config("memory.chroma.persist_directory", default="data/chroma")

                    graph_store = create_graph_store()
                    chroma_store = None
                    try:
                        chroma_store = ChromaStore(persist_directory=chroma_dir)
                    except Exception as chroma_err:
                        self.logger.warning(
                            f"[MEMORY] Chroma unavailable (SQLite graph still works): {chroma_err}"
                        )

                    # Embeddings: Ollama (Dave) or hash fallback (Brittany consumer — no Ollama)
                    from utils.embedding_utils import HashEmbedder

                    embed_backend = get_config("memory.embedding.backend", default="ollama")
                    edition = get_config("edition", default="business")

                    if embed_backend == "hash" or edition == "consumer":
                        embedding_function = HashEmbedder().embed
                        self.logger.info("[MEMORY] Using lightweight hash embeddings (consumer)")
                    else:
                        ollama_model = get_config("memory.embedding.model", default="nomic-embed-text")
                        ollama_url = get_config(
                            "memory.embedding.url",
                            default="http://localhost:11434/api/embeddings",
                        )
                        embedder = OllamaEmbedder(model=ollama_model, url=ollama_url)
                        embedding_function = embedder.embed
                        if not embedder.is_available():
                            self.logger.warning(
                                "[MEMORY] Ollama embedder not available - memory recall may be limited"
                            )

                    if graph_store and hasattr(graph_store, "connect") and not graph_store.is_connected():
                        self.logger.warning(f"[MEMORY] Could not connect graph store ({memory_backend})")

                    self.memory_manager = MemoryManager(
                        neo4j_client=graph_store,
                        chroma_store=chroma_store,
                        embedding_function=embedding_function,
                    )
                    self.graph_store = graph_store
                    self.neo4j_client = graph_store  # legacy alias

                    # Create a Conversation node for this assistant session so stored
                    # memories can be linked to the active conversation.
                    try:
                        conv = None
                        if graph_store and graph_store.is_connected():
                            conv = graph_store.create_conversation(
                                summary=f"Session {self.session_id}", mood="neutral"
                            )
                        if conv:
                            # store conversation id for later linking
                            self.current_conversation_id = conv.get("id") if hasattr(conv, 'get') else str(conv)
                        else:
                            self.current_conversation_id = None
                    except Exception:
                        self.current_conversation_id = None

                    self.logger.info("[MEMORY] Memory Vault initialized successfully")
                except Exception as e:
                    self.logger.warning(f"[MEMORY] Memory Vault initialization failed (non-fatal): {e}")
                    self.memory_manager = None
            else:
                self.logger.info("[MEMORY] Memory Vault disabled in config")
        else:
            self.logger.info("[MEMORY] Memory Vault module not available")

        # --- PERSONALITY ENGINE INITIALIZATION ---
        self.personality_engine: Optional[PersonalityEngine] = None
        if PERSONALITY_AVAILABLE and PersonalityEngine is not None:
            self.logger.info("[PERSONALITY] Initializing Personality Engine...")
            try:
                # Initialize engine with Sam profile
                self.personality_engine = PersonalityEngine(get_arden_profile())
                self.logger.info(f"[PERSONALITY] Personality active: {self.personality_engine.profile.name}")

                # Apply edition-specific overrides from persona.json
                edition = get_config("edition", default="consumer")
                if edition:
                    self.personality_engine.load_edition_overrides(edition)
                    self.logger.info(f"[PERSONALITY] Edition overrides applied: {edition}")

                assistant_name = get_config("base_assistant.assistant_name", default="Sam")
                human_name = get_config("base_assistant.human_companion_name", default="")
                if assistant_name != "Sam" or human_name:
                    from modules.personality_engine.identity import apply_user_identity

                    apply_user_identity(
                        self.personality_engine.profile,
                        assistant_name,
                        human_name,
                    )
                    if human_name and self.personality_engine.voice_config is not None:
                        self.personality_engine.voice_config["greeting"] = (
                            f"Hey {human_name}. What's on your mind?"
                        )
                    self.logger.info(
                        f"[PERSONALITY] Identity: {assistant_name} / user={human_name or 'unnamed'}"
                    )

            except Exception as e:
                self.logger.warning(f"[PERSONALITY] Personality Engine initialization failed (non-fatal): {e}")
                self.personality_engine = None
        else:
            self.logger.info("[PERSONALITY] Personality Engine module not available")

        # --- TASK MANAGER + MORNING BRIEFING INITIALIZATION ---
        self.task_manager = TaskManager()
        self.morning_briefing = MorningBriefing(
            self.task_manager,
            memory_manager=self.memory_manager
        )
        self.logger.info("[TASKS] TaskManager and MorningBriefing initialized")

        # --- BRAIN BACKEND INITIALIZATION ---
        self.logger.info("[BRAIN] Initializing brain backend...")
        self.brain_backend = self._initialize_brain_backend()
        if self.brain_backend:
            model_info = self.brain_backend.get_model_info()
            self.logger.info(f"[BRAIN] Using {model_info['backend']} ({model_info['type']}) - {model_info['model']}")
        else:
            self.logger.error("[BRAIN] No brain backend available!")
            raise RuntimeError("Cannot initialize Arden without a working brain backend")

        # Initialize appropriate TTS engine
        if self.voice_type == "none":
            self.logger.info("[TTS] Text-only mode (no voice output)")
            self.engine = None
        elif self.voice_type == "local":
            import pyttsx3
            self.logger.info("[TTS] Initializing local TTS engine")
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 150)  # Speed of speech
            self.engine.setProperty("volume", 1.0)  # Volume level
        elif self.voice_type == "realtime-tts":
            from RealtimeTTS import TextToAudioStream, SystemEngine
            self.logger.info("[TTS] Initializing RealtimeTTS engine")
            self.engine = SystemEngine()
            self.stream = TextToAudioStream(
                self.engine, frames_per_buffer=256, playout_chunk_size=1024
            )
        elif self.voice_type == "elevenlabs":
            from elevenlabs.client import ElevenLabs
            self.logger.info("[TTS] Initializing ElevenLabs TTS engine")
            self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
        else:
            raise ValueError(f"Unsupported voice type: {self.voice_type}")
    
    def _initialize_brain_backend(self) -> Optional[BaseBrainBackend]:
        """Initialize the brain backend with fallback chain.
        
        Returns:
            BaseBrainBackend instance or None if all backends fail
        """
        # Get configuration
        default_backend = get_config("brain.default", default="lm_studio")
        fallback_chain = get_config("brain.fallback_chain", default=[default_backend])
        
        # Try each backend in the fallback chain
        for backend_type in fallback_chain:
            try:
                from modules.brain_secrets import load_brain_config

                backend_config = load_brain_config(backend_type)

                if not backend_config:
                    self.logger.warning(f"[BRAIN] No config found for {backend_type}")
                    continue
                
                # Try to create and test backend
                backend = BrainFactory.create_backend(backend_type, backend_config)
                if backend and backend.is_available():
                    self.logger.info(f"[BRAIN] Successfully initialized {backend_type} backend")
                    return backend
                else:
                    self.logger.warning(f"[BRAIN] {backend_type} backend not available")
                    
            except Exception as e:
                self.logger.warning(f"[BRAIN] Failed to initialize {backend_type}: {e}")
                continue
        
        return None
    
    def switch_brain(self, backend_type: str) -> bool:
        """Switch to a different brain backend.
        
        Args:
            backend_type: Type of backend to switch to ('lm_studio', 'ollama', etc.)
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            self.logger.info(f"[BRAIN] Attempting to switch to {backend_type}...")

            from modules.brain_secrets import load_brain_config

            backend_config = load_brain_config(backend_type)

            if not backend_config:
                self.logger.error(f"[BRAIN] No config for {backend_type}")
                return False
                
            new_backend = BrainFactory.create_backend(backend_type, backend_config)
            if new_backend and new_backend.is_available():
                old_backend = self.brain_backend.name if self.brain_backend else "none"
                self.brain_backend = new_backend
                model_info = new_backend.get_model_info()
                self.logger.info(f"[BRAIN] Switched from {old_backend} to {backend_type}")
                self.logger.info(f"[BRAIN] Now using {model_info['backend']} - {model_info['model']}")
                return True
            else:
                self.logger.error(f"[BRAIN] {backend_type} backend not available")
                return False
                
        except Exception as e:
            self.logger.error(f"[BRAIN] Error switching to {backend_type}: {e}")
            return False
    
    def get_brain_status(self) -> Dict[str, Any]:
        """Get current brain backend status.
        
        Returns:
            Dictionary with backend information
        """
        if not self.brain_backend:
            return {"error": "No brain backend initialized"}
        
        return {
            "current_backend": self.brain_backend.name,
            "model_info": self.brain_backend.get_model_info(),
            "is_local": self.brain_backend.is_local,
            "is_available": self.brain_backend.is_available()
        }
    
    def _get_greeting(self) -> str:
        """Return the edition-appropriate greeting.

        Checks the configured edition and returns either the business greeting
        from voice_config or the consumer default.  Falls back gracefully if
        the personality engine is not available.
        """
        edition = get_config("edition", default="consumer")
        voice = getattr(self.personality_engine, "voice_config", {}) if self.personality_engine else {}
        if edition in ("business", "consigliere"):
            return voice.get("greeting", "Good morning. I'm ready when you are.")
        return voice.get("greeting", "Hey! What are we working on?")

    def cleanup(self):
        """Clean up resources (Neo4j/ChromaDB connections, etc.)"""
        self.logger.info("[CLEANUP] Starting resource cleanup...")
        
        # Close Neo4j connection
        if self.memory_manager and hasattr(self.memory_manager, 'neo4j'):
            try:
                if self.memory_manager.neo4j and hasattr(self.memory_manager.neo4j, 'close'):
                    self.memory_manager.neo4j.close()
                    self.logger.info("[CLEANUP] Neo4j connection closed")
            except Exception as e:
                self.logger.warning(f"[CLEANUP] Error closing Neo4j: {e}")
        
        # Close ChromaDB (if needed)
        if self.memory_manager and hasattr(self.memory_manager, 'chroma'):
            try:
                # ChromaDB usually handles cleanup automatically
                self.logger.info("[CLEANUP] ChromaDB closed")
            except Exception as e:
                self.logger.warning(f"[CLEANUP] Error closing ChromaDB: {e}")
        
        self.logger.info("[CLEANUP] Resource cleanup complete")

    def _build_messages_with_personality(self, memory_context: str = "") -> List[Dict]:
        """Build conversation messages with personality and memory context prepended."""
        messages = []
        
        # Build system prompt using personality engine if available
        if self.personality_engine:
            system_prompt = self.personality_engine.get_system_prompt(memory_context)
            messages.append({"role": "system", "content": system_prompt})
        elif memory_context:
            messages.append({"role": "system", "content": memory_context})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        return messages
    
    def _recall_memories(self, query: str, limit: int = 3) -> str:
        """Recall relevant past conversation exchanges and format as context string.
        
        Args:
            query: Query text to find relevant exchanges
            limit: Maximum exchanges to recall (default 3 as per task spec)
            
        Returns:
            Formatted memory context string, or empty string if none found
        """
        if not self.memory_manager:
            return ""
        
        try:
            with self._memory_lock:
                memories = self.memory_manager.recall(query=query, limit=limit)
            
            if not memories:
                return ""
            
            # Format exchanges as context
            memory_lines = ["[Relevant past conversations]"]
            for mem in memories:
                content = mem.get("content", "")
                # Each memory contains a full exchange in format "User: X\nAssistant: Y"
                memory_lines.append(content)
            
            context = "\n\n".join(memory_lines)
            self.logger.info(f"[MEMORY] Recalled {len(memories)} past exchanges")
            return context
            
        except Exception as e:
            self.logger.warning(f"[MEMORY] Memory recall failed: {e}")
            return ""
    
    def _store_memory(self, content: str, memory_type: str = "fact", importance: float = 0.5):
        """Store content as a memory.
        
        Args:
            content: Text content to remember
            memory_type: Type of memory (fact, event, insight, reflection)
            importance: Importance score 0.0-1.0
        """
        if not self.memory_manager:
            return
        
        try:
            memory_id = self.memory_manager.remember(
                content=content,
                memory_type=memory_type,
                importance=importance
            )
            if memory_id:
                self.logger.info(f"[MEMORY] Stored memory: {memory_id[:8]}...")
                # If a session conversation exists, link this memory to it in Neo4j
                try:
                    conv_id = getattr(self, 'current_conversation_id', None)
                    if conv_id and self.memory_manager.neo4j:
                        self.memory_manager.neo4j.link_memory_to_conversation(memory_id, conv_id)
                        self.logger.info(f"[MEMORY] Linked memory {memory_id[:8]} to conversation {conv_id[:8]}...")
                except Exception:
                    pass  # Non-fatal if linking fails
        except Exception as e:
            self.logger.warning(f"[MEMORY] Memory storage failed: {e}")
    
    def _check_memory_query(self, text: str) -> Optional[str]:
        """Check if user is asking about memories and handle specially.
        
        Args:
            text: User input text
            
        Returns:
            Formatted memory response if this is a memory query, None otherwise
        """
        text_lower = text.lower().strip()
        
        # Check for memory query patterns
        memory_patterns = [
            "what do you remember about",
            "do you remember",
            "recall anything about",
            "what do you know about"
        ]
        
        for pattern in memory_patterns:
            if pattern in text_lower:
                # Extract the topic
                topic = text_lower.split(pattern)[-1].strip().rstrip("?")
                if topic:
                    self.logger.info(f"[MEMORY] Memory query detected for: {topic}")
                    memories = self.memory_manager.recall(query=topic, limit=5) if self.memory_manager else []
                    
                    if memories:
                        response_lines = [f"Here's what I remember about '{topic}':"]
                        for mem in memories:
                            content = mem.get("content", "")
                            entities = mem.get("entity_names", [])
                            if entities:
                                response_lines.append(f"- {content} (related to: {', '.join(entities)})")
                            else:
                                response_lines.append(f"- {content}")
                        return "\n".join(response_lines)
                    else:
                        return f"I don't have any specific memories about '{topic}' yet."
        
        return None
    

    def process_text(self, text: str, chunk_callback=None) -> str:
        """Process text input and generate response.

        Optional chunk_callback(str) receives live tokens when the active brain supports streaming.
        """
        try:
            # Voice echo guard: only ignore when mic likely picked up our last spoken reply.
            if self.conversation_history:
                last = self.conversation_history[-1]
                if (
                    last.get("role") == "assistant"
                    and text.strip().lower() in last["content"].lower()
                ):
                    self.logger.info("[ASSISTANT] Ignoring own speech input")
                    return ""
            
            # --- MEMORY: Check for direct memory queries ---
            if self.memory_manager:
                memory_response = self._check_memory_query(text)
                if memory_response:
                    # This is a memory query - return recalled memories directly
                    self.conversation_history.append({"role": "user", "content": text})
                    self.conversation_history.append({"role": "assistant", "content": memory_response})
                    self.speak(memory_response)
                    return memory_response
            
            # --- MEMORY: Recall relevant memories BEFORE building prompt ---
            memory_context = ""
            if self.memory_manager:
                memory_context = self._recall_memories(text, limit=5)

            try:
                from modules.tactical_context import tactical_context_for_prompt

                tactical = tactical_context_for_prompt()
                if tactical:
                    memory_context = f"{tactical}\n\n{memory_context}".strip() if memory_context else tactical
            except Exception:
                pass

            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": text})

            # Build messages with personality and memory context
            messages_with_context = self._build_messages_with_personality(memory_context)

            # Check for memory commands
            text_lower = text.lower().strip()
            
            # "remember this" command
            if text_lower == "remember this":
                if not self.memory_manager:
                    response = "Memory system is not available."
                    self.speak(response)
                    return response
                
                # Get the last exchange if it exists
                if len(self.conversation_history) >= 2:
                    # Last user message and assistant response
                    last_user_msg = None
                    last_assistant_msg = None
                    
                    for i in range(len(self.conversation_history) - 1, -1, -1):
                        msg = self.conversation_history[i]
                        if msg["role"] == "assistant" and last_assistant_msg is None:
                            last_assistant_msg = msg["content"]
                        elif msg["role"] == "user" and last_user_msg is None:
                            last_user_msg = msg["content"]
                        
                        if last_user_msg and last_assistant_msg:
                            break
                    
                    if last_user_msg and last_assistant_msg:
                        exchange_content = f"User: {last_user_msg}\nAssistant: {last_assistant_msg}"
                        
                        # Store with high importance (0.9)
                        memory_id = self.memory_manager.remember(
                            content=exchange_content,
                            memory_type="event",
                            importance=0.9  # Mark as important
                        )
                        
                        if memory_id:
                            self._last_memory_id = memory_id
                            self.logger.info(f"[MEMORY] Marked exchange as important: {memory_id[:8]}...")
                            response = "Got it, I've marked that as important."
                        else:
                            response = "I had trouble storing that memory."
                    else:
                        response = "I don't have a recent exchange to remember."
                else:
                    response = "I don't have anything to remember yet. Let's have a conversation first!"
                
                # BUG-2 fix: user message already appended above, only append assistant response
                self.conversation_history.append({"role": "assistant", "content": response})
                self.speak(response)
                self._trim_conversation_history()
                return response
            
            # "forget this" command
            if text_lower == "forget this":
                if not self.memory_manager:
                    response = "Memory system is not available."
                    self.speak(response)
                    return response
                
                try:
                    memory_id = self._last_memory_id
                    if memory_id and self.memory_manager.forget(memory_id):
                        deleted_id = memory_id
                    else:
                        deleted_id = self.memory_manager.forget_most_recent()

                    if deleted_id:
                        self._last_memory_id = None
                        response = "I've removed that from my memory."
                        self.logger.info(f"[MEMORY] Forgot memory: {deleted_id[:8]}...")
                    else:
                        response = "I don't have a recent memory to forget."
                except Exception as e:
                    self.logger.warning(f"[MEMORY] Error forgetting memory: {e}")
                    response = "I had trouble forgetting that."
                self.speak(response)
                
                # BUG-2 fix: user message already appended above, only append assistant response
                self.conversation_history.append({"role": "assistant", "content": response})
                self._trim_conversation_history()
                return response
            
            # --- Check for brain switching commands ---
            if "switch brain" in text_lower or "change brain" in text_lower:
                # Extract backend name
                for backend in AVAILABLE_BACKENDS:
                    if backend in text_lower:
                        if self.switch_brain(backend):
                            response = f"Switched to {backend} brain. Same soul — different brain."
                        else:
                            response = f"Could not switch to {backend}. Is it configured and available?"
                        
                        self.conversation_history.append({"role": "assistant", "content": response})
                        self.speak(response)
                        return response
                
                # No specific backend mentioned
                response = (
                    f"Available backends: {', '.join(AVAILABLE_BACKENDS)}. "
                    "Say 'switch brain to [backend]'."
                )
                self.conversation_history.append({"role": "assistant", "content": response})
                self.speak(response)
                return response
            
            elif "brain status" in text_lower or "which brain" in text_lower:
                status = self.get_brain_status()
                if "error" in status:
                    response = status["error"]
                else:
                    model_info = status["model_info"]
                    backend_type = "local" if status["is_local"] else "cloud"
                    response = f"Currently using {status['current_backend']} ({backend_type}) - {model_info['model']}"
                
                self.conversation_history.append({"role": "assistant", "content": response})
                self.speak(response)
                return response
            
            # ── MORNING BRIEFING INTERCEPT ──────────────────────────────────────
            briefing_enabled = get_config("morning_briefing_enabled", default=False)
            if briefing_enabled and self.morning_briefing.is_morning_trigger(text):
                briefing = self.morning_briefing.generate()
                print(f"\nSam: {briefing}\n")
                self.logger.info("[BRIEFING] Morning briefing generated, enriching LLM prompt")
                # Pass structured briefing data to the LLM for a natural-language wrap
                text = (
                    "[SYSTEM: Morning briefing data below. Present this conversationally, "
                    "add encouragement, keep it tight.]\n"
                    f"{briefing}\n"
                    f"[User said: {text}]"
                )

            # ── TASK CAPTURE INTERCEPT ────────────────────────────────────────────
            task_triggers = ["remind me", "don't forget", "dont forget", "add task", "make a note"]
            text_lower_now = text.lower()
            if any(t in text_lower_now for t in task_triggers):
                task_content = text
                for trigger in task_triggers:
                    task_content = task_content.lower().replace(trigger, "").strip()
                if task_content:
                    task_id = self.task_manager.add_task(task_content, source="voice")
                    voice_config = getattr(self.personality_engine, "voice_config", {}) if self.personality_engine else {}
                    saved_msg = voice_config.get("task_saved", "I'll remember that.")
                    print(f"\nSam: {saved_msg} [Task #{task_id} saved]\n")
                    self.logger.info(f"[TASKS] Saved task #{task_id}: {task_content[:60]}")

            # ── MARK DONE INTERCEPT ───────────────────────────────────────────────
            done_triggers = ["mark done", "cross off", "that's done", "thats done", "completed"]
            if any(t in text_lower_now for t in done_triggers):
                open_tasks = self.task_manager.get_open_tasks()
                if open_tasks:
                    task_list = "\n".join([f"#{t.id}: {t.content}" for t in open_tasks])
                    text = (
                        f"[SYSTEM: User wants to mark a task done. Open tasks:\n{task_list}\n"
                        f"Figure out which task they mean and tell them it is marked done. "
                        f"User said: {text}]"
                    )

            # --- Generate response using brain backend ---
            self.logger.info(f"[BRAIN] Generating response with {self.brain_backend.name}...")
            
            # Extract system prompt and conversation from messages_with_context
            system_prompt = ""
            conversation = []
            for msg in messages_with_context:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    conversation.append(msg)
            
            # Get current user message (last message in conversation_history)
            user_message = text
            
            # Generate response using brain backend (stream when GUI requests it)
            if chunk_callback and getattr(self.brain_backend, "supports_streaming", lambda: False)():
                response = self.brain_backend.generate_response_stream(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    conversation_history=conversation[:-1] if conversation else None,
                    on_chunk=chunk_callback,
                )
            else:
                response = self.brain_backend.generate_response(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    conversation_history=conversation[:-1] if conversation else None,
                )

            # Add assistant response to history
            response = (response or "").strip()
            if not response:
                response = (
                    "I didn't get a reply back. Open Settings and check your Venice or Groq API key, "
                    "or switch Brain to one that's available."
                )

            self.conversation_history.append({"role": "assistant", "content": response})

            # --- MEMORY: store exchange without blocking the GUI thread ---
            if self.memory_manager:
                import threading

                threading.Thread(
                    target=self._store_exchange_memory,
                    args=(text, response),
                    daemon=True,
                ).start()

            # Speak the response (GUI handles TTS when streaming live tokens)
            if chunk_callback is None:
                self.speak(response)

            # PROD-1 fix: Trim history to prevent unbounded growth
            self._trim_conversation_history()

            return response

        except ValueError as e:
            self.logger.error(f"[ERROR] Error in process_text: {str(e)}")
            error_response = str(e)
            self.conversation_history.append({"role": "assistant", "content": error_response})
            return error_response
        except Exception as e:
            self.logger.error(f"[ERROR] Error in process_text: {str(e)}")
            # ERR-1 fix: Return friendly error instead of crashing
            error_response = get_friendly_error_message('unknown')
            self.conversation_history.append({"role": "assistant", "content": error_response})
            try:
                self.speak(error_response)
            except Exception:
                pass  # If speak also fails, just return the text
            return error_response

    def _store_exchange_memory(self, user_text: str, response: str) -> None:
        """Persist exchange to memory vault (background-safe)."""
        if not self.memory_manager:
            return
        try:
            with self._memory_lock:
                exchange_content = f"User: {user_text}\nAssistant: {response}"
                memory_id = self.memory_manager.remember(
                    content=exchange_content,
                    memory_type="event",
                    importance=0.6,
                )
                if memory_id:
                    self._last_memory_id = memory_id
                    self.logger.info(f"[MEMORY] Stored conversation exchange: {memory_id[:8]}...")
                    try:
                        conv_id = getattr(self, "current_conversation_id", None)
                        if conv_id and self.memory_manager.neo4j:
                            self.memory_manager.neo4j.link_memory_to_conversation(memory_id, conv_id)
                    except Exception:
                        pass
        except Exception as e:
            self.logger.warning(f"[MEMORY] Background store failed: {e}")

    def _trim_conversation_history(self, max_exchanges: int = 20):
        """Trim conversation history to prevent unbounded growth.
        
        Keeps only the last N exchanges (user+assistant pairs).
        Older exchanges are already stored in memory vault.
        
        Args:
            max_exchanges: Maximum number of message pairs to keep
        """
        max_messages = max_exchanges * 2  # Each exchange = user + assistant
        if len(self.conversation_history) > max_messages:
            trimmed = len(self.conversation_history) - max_messages
            self.conversation_history = self.conversation_history[-max_messages:]
            self.logger.info(f"[HISTORY] Trimmed {trimmed} old messages, keeping last {max_exchanges} exchanges")

    def speak(self, text: str):
        """Convert text to speech using configured engine"""
        if self.voice_type == "none":
            return
        try:
            self.logger.info(f"[TTS] Speaking: {text}")

            if self.voice_type == "local":
                self.engine.say(text)
                self.engine.runAndWait()

            elif self.voice_type == "realtime-tts":
                self.stream.feed(text)
                self.stream.play()

            elif self.voice_type == "elevenlabs":
                from elevenlabs import play
                audio = self.elevenlabs_client.generate(
                    text=text,
                    voice=self.elevenlabs_voice,
                    model="eleven_turbo_v2",
                    stream=False,
                )
                play(audio)

            self.logger.info(f"[TTS] Spoken: {text}")

        except Exception as e:
            # ERR-2 fix: Log error but don't crash - fall back to text-only
            self.logger.error(f"[TTS] Speech synthesis failed (text-only mode): {str(e)}")
            print(f"[Sam]: {text}")
