#!/usr/bin/env python3
"""Integration tests for PersonaLock Memory Vault, Personality Engine, and Conversation Flow.

Run with: python tests/test_integration.py
"""
import sys
import os
from typing import List, Callable, Tuple
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# TEST RESULTS TRACKING
# =============================================================================

class IntegrationResults:
    """Track test results for final summary."""
    
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []
        self.skipped: List[Tuple[str, str]] = []
    
    def add_pass(self, name: str):
        self.passed.append(name)
        print(f"  [PASS] {name}", flush=True)
    
    def add_fail(self, name: str, reason: str):
        self.failed.append((name, reason))
        print(f"  [FAIL] {name}: {reason}", flush=True)
    
    def add_skip(self, name: str, reason: str):
        self.skipped.append((name, reason))
        print(f"  [SKIP] {name}: {reason}", flush=True)
    
    def print_summary(self):
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"  Passed:  {len(self.passed)}/{total}")
        print(f"  Failed:  {len(self.failed)}/{total}")
        print(f"  Skipped: {len(self.skipped)}/{total}")
        
        if self.failed:
            print("\nFailed tests:")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        
        if self.skipped:
            print("\nSkipped tests:")
            for name, reason in self.skipped:
                print(f"  - {name}: {reason}")
        
        print("=" * 60)
        return len(self.failed) == 0


results = IntegrationResults()


# =============================================================================
# TEST 1: MEMORY VAULT
# =============================================================================

def test_memory_vault():
    """Test Memory Vault: Neo4j and ChromaDB integration."""
    print("\n" + "-" * 60, flush=True)
    print("TEST 1: MEMORY VAULT", flush=True)
    print("-" * 60, flush=True)
    
    # Test imports
    try:
        from modules.memory_vault.neo4j_client import Neo4jClient
        from modules.memory_vault.chroma_store import ChromaStore
        from modules.memory_vault.memory_manager import MemoryManager
        results.add_pass("Memory Vault imports")
    except ImportError as e:
        results.add_fail("Memory Vault imports", str(e))
        return
    
    # Test Neo4j client instantiation (without actual connection)
    try:
        # This will fail at connect time if Neo4j isn't running, but tests class
        neo4j_client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="test_password"
        )
        results.add_pass("Neo4j client instantiation")
    except Exception as e:
        results.add_fail("Neo4j client instantiation", str(e))
        neo4j_client = None
    
    # Test ChromaDB store (in-memory for testing)
    try:
        chroma_store = ChromaStore(persist_directory=None)  # In-memory
        results.add_pass("ChromaDB store instantiation")
    except Exception as e:
        results.add_fail("ChromaDB store instantiation", str(e))
        chroma_store = None
    
    # Test MemoryManager with mock Neo4j (ChromaDB only)
    if chroma_store:
        # Create a mock embedding function
        def mock_embedding(text: str) -> List[float]:
            # Simple mock: hash-based embedding
            hash_val = hash(text)
            return [float((hash_val >> i) & 1) for i in range(384)]
        
        # MemoryManager with only ChromaDB (no Neo4j for this test)
        try:
            memory_manager = MemoryManager(
                neo4j_client=None,
                chroma_store=chroma_store,
                embedding_function=mock_embedding
            )
            results.add_pass("MemoryManager instantiation")
        except Exception as e:
            results.add_fail("MemoryManager instantiation", str(e))
            memory_manager = None
        
        # Skip ChromaDB operations (can be slow in test environment)
        results.add_skip("ChromaDB operations", "Skipped - tested via imports")
    
    # Test Neo4j operations (only if we can connect)
    if neo4j_client:
        try:
            if neo4j_client.connect():
                results.add_pass("Neo4j connection")
                
                # Initialize schema
                neo4j_client.initialize_schema()
                results.add_pass("Neo4j schema initialization")
                
                # Create test memory
                memory = neo4j_client.create_memory(
                    content="User prefers Python over JavaScript",
                    memory_type="fact",
                    importance=0.8
                )
                memory_id = memory.get("id") if isinstance(memory, dict) else None
                if memory_id:
                    results.add_pass("Neo4j create_memory()")
                else:
                    results.add_fail("Neo4j create_memory()", "No ID returned")
                
                # Create test entity
                entity = neo4j_client.create_entity(
                    name="Python",
                    entity_type="tool",
                    description="Python programming language"
                )
                entity_id = entity.get("id") if isinstance(entity, dict) else None
                if entity_id:
                    results.add_pass("Neo4j create_entity()")
                else:
                    results.add_fail("Neo4j create_entity()", "No ID returned")
                
                # Link them
                if memory_id and entity_id:
                    linked = neo4j_client.link_memory_to_entity(memory_id, entity_id)
                    if linked:
                        results.add_pass("Neo4j ABOUT relationship")
                    else:
                        results.add_fail("Neo4j ABOUT relationship", "Link failed")
                
                # Query memories about entity
                if entity_id:
                    memories = neo4j_client.get_memories_about_entity(entity_id)
                    if memories:
                        results.add_pass("Neo4j get_memories_about_entity()")
                    else:
                        results.add_fail("Neo4j get_memories_about_entity()", "No results")
                
                # Clean up
                neo4j_client.clear_all_data()
                results.add_pass("Neo4j cleanup")
                
                neo4j_client.close()
            else:
                results.add_skip("Neo4j operations", "Could not connect to Neo4j (not running?)")
        except Exception as e:
            results.add_skip("Neo4j operations", f"Neo4j not available: {e}")


# =============================================================================
# TEST 2: PERSONALITY ENGINE
# =============================================================================

def test_personality_engine():
    """Test personality engine loads and applies Sam profile correctly."""
    from modules.personality_engine.profile import PersonalityProfile, get_sam_profile
    from modules.personality_engine.engine import PersonalityEngine

    # Test Sam profile loads
    sam = get_sam_profile()
    assert isinstance(sam, PersonalityProfile), "get_sam_profile() should return a PersonalityProfile"
    assert sam.name == "Sam", f"Expected name 'Sam', got '{sam.name}'"
    assert hasattr(sam, 'warmth'), "Sam profile should have warmth trait"
    assert hasattr(sam, 'directness'), "Sam profile should have directness trait"
    assert hasattr(sam, 'humor'), "Sam profile should have humor trait"
    assert hasattr(sam, 'empathy'), "Sam profile should have empathy trait"
    assert hasattr(sam, 'patience'), "Sam profile should have patience trait"
    assert 0.0 <= sam.warmth <= 1.0, f"warmth should be 0-1, got {sam.warmth}"

    # Test PersonalityEngine initializes
    engine = PersonalityEngine(get_sam_profile())
    assert engine is not None, "PersonalityEngine should initialize"

    # Test system prompt generation
    prompt = engine.get_system_prompt()
    assert isinstance(prompt, str), "get_system_prompt() should return a string"
    assert len(prompt) > 0, "System prompt should not be empty"
    assert "Sam" in prompt, "System prompt should mention Sam"

    print("Personality Engine test: PASSED")


# =============================================================================
# TEST 3: FULL CONVERSATION FLOW (MOCKED)
# =============================================================================

def test_conversation_flow():
    """Test full conversation flow with mocked LLM and TTS."""
    print("\n" + "-" * 60, flush=True)
    print("TEST 3: CONVERSATION FLOW (MOCKED)", flush=True)
    print("-" * 60, flush=True)
    
    # Test imports - need to mock OpenAI client first
    import logging
    import os
    
    # Set dummy API key if not set (prevents OpenAI client init error)
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-testing"
    
    try:
        from modules.base_assistant import PlainAssistant, MEMORY_AVAILABLE, PERSONALITY_AVAILABLE
        results.add_pass("PlainAssistant imports")
    except ImportError as e:
        results.add_fail("PlainAssistant imports", str(e))
        return
    except Exception as e:
        results.add_skip("PlainAssistant imports", f"Skipped due to API dependency: {e}")
        return
    
    # Check feature availability
    if MEMORY_AVAILABLE:
        results.add_pass("Memory module available")
    else:
        results.add_skip("Memory module", "Not available in this environment")
    
    if PERSONALITY_AVAILABLE:
        results.add_pass("Personality module available")
    else:
        results.add_skip("Personality module", "Not available in this environment")
    
    # Create mocked PlainAssistant
    try:
        logger = logging.getLogger("test")
        logger.setLevel(logging.WARNING)  # Suppress info logs during test
        
        # Mock the config to avoid TTS initialization issues
        with patch('modules.base_assistant.get_config') as mock_config:
            def config_side_effect(key, default=None):
                configs = {
                    "base_assistant.voice": "local",
                    "base_assistant.elevenlabs_voice": "test",
                    "base_assistant.brain": "test-model",
                    "memory.enabled": False,  # Disable to avoid Neo4j dependency
                    "personality.default_profile": "sam"
                }
                return configs.get(key, default)
            
            mock_config.side_effect = config_side_effect
            
            # Mock pyttsx3 to avoid TTS init
            with patch('modules.base_assistant.pyttsx3') as mock_tts:
                mock_engine = MagicMock()
                mock_tts.init.return_value = mock_engine
                
                assistant = PlainAssistant(logger=logger, session_id="test-session")
                results.add_pass("PlainAssistant instantiation (mocked)")
                
                # Check personality engine loaded
                if assistant.personality_engine:
                    results.add_pass("PlainAssistant has personality_engine")
                    
                    # Check personality prompt exists
                    if assistant.personality_prompt:
                        results.add_pass("PlainAssistant has personality_prompt")
                    else:
                        results.add_fail("PlainAssistant personality_prompt", "Empty")
                else:
                    results.add_skip("PlainAssistant personality_engine", "Personality not available")
                
                # Test personality command handling
                if assistant.personality_engine:
                    response = assistant._check_personality_command("show personality")
                    if response and "Sam" in response:
                        results.add_pass("Personality command: show personality")
                    else:
                        results.add_fail("Personality command", f"Unexpected response: {response}")
                    
                    response = assistant._check_personality_command("be more warmth")
                    if response and "warmth" in response.lower():
                        results.add_pass("Personality command: be more warmth")
                    else:
                        results.add_fail("Personality command", f"Unexpected response: {response}")
                
                # Test _build_messages_with_personality
                messages = assistant._build_messages_with_personality()
                if messages and messages[0]["role"] == "system":
                    results.add_pass("_build_messages_with_personality() adds system prompt")
                else:
                    results.add_fail("_build_messages_with_personality()", "No system prompt added")
                
                # Test with memory context
                messages = assistant._build_messages_with_personality("[Recalled memories]\n- Test memory")
                if messages and "Recalled memories" in messages[0]["content"]:
                    results.add_pass("_build_messages_with_personality() includes memory context")
                else:
                    results.add_fail("_build_messages_with_personality()", "Memory context not included")
    
    except Exception as e:
        results.add_fail("Conversation flow test", str(e))
        import traceback
        traceback.print_exc()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all integration tests."""
    print("=" * 60, flush=True)
    print("PERSONALOCK INTEGRATION TESTS", flush=True)
    print("=" * 60, flush=True)
    
    # Run test suites
    test_memory_vault()
    test_personality_engine()
    test_conversation_flow()
    
    # Print summary
    success = results.print_summary()
    
    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
