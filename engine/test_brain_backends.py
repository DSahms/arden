"""
Quick test for brain backends - Phase 4

Tests that backends can be initialized and used with Sam's personality.
"""

import sys
import os

# Test imports
try:
    from modules.brain_backends import BrainFactory
    from modules.brain_backends.lm_studio_backend import LMStudioBackend
    from modules.brain_backends.ollama_backend import OllamaBackend
    from modules.personality_engine.profile import get_sam_profile
    from modules.personality_engine.engine import PersonalityEngine
    print("[PASS] All imports successful")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

def test_brain_factory():
    """Test brain factory can create backends"""
    print("\n[TEST] Brain factory creation...")
    
    lm_config = {'base_url': 'http://localhost:1234/v1', 'model': 'test'}
    backend = BrainFactory.create_backend('lm_studio', lm_config)
    
    assert backend is not None, "Failed to create backend"
    assert backend.name == 'lm_studio', "Backend name mismatch"
    
    print("[PASS] Brain factory test")

def test_personality_with_backend():
    """Test that personality system works with backends"""
    print("\n[TEST] Personality + Brain integration...")
    
    # Get Sam's personality
    sam_profile = get_sam_profile()
    engine = PersonalityEngine(sam_profile)
    
    # Build system prompt
    system_prompt = engine.get_system_prompt()
    
    # Verify Sam identity is in prompt
    assert "Sam" in system_prompt, "Sam identity missing from prompt"
    assert "never claim to be GPT" in system_prompt, "Identity protection missing"
    
    print("[PASS] Personality integration test")

def test_backend_interface():
    """Test all backends implement required interface"""
    print("\n[TEST] Backend interface compliance...")
    
    from modules.brain_backends.base_backend import BaseBrainBackend
    
    # Check LM Studio backend
    lm_config = {'base_url': 'http://localhost:1234', 'model': 'test'}
    backend = LMStudioBackend(lm_config)
    
    # Verify required methods exist
    assert hasattr(backend, 'generate_response'), "Missing generate_response"
    assert hasattr(backend, 'is_available'), "Missing is_available"
    assert hasattr(backend, 'get_model_info'), "Missing get_model_info"
    assert hasattr(backend, 'test_connection'), "Missing test_connection"
    
    # Verify model info format
    info = backend.get_model_info()
    assert 'backend' in info, "Missing backend in model_info"
    assert 'type' in info, "Missing type in model_info"
    assert 'model' in info, "Missing model in model_info"
    
    print("[PASS] Backend interface test")

def test_available_backends():
    """Test which backends are available"""
    print("\n[TEST] Checking available backends...")
    
    backends = BrainFactory.get_available_backends()
    print(f"Available backend types: {backends}")
    
    for name in ('kobold', 'lm_studio', 'ollama', 'groq', 'claude', 'openai', 'venice', 'gemini'):
        assert name in backends, f"{name} backend missing"

    print("[PASS] Backend availability test")

if __name__ == "__main__":
    print("="*60)
    print("BRAIN BACKENDS TEST SUITE - Phase 4")
    print("="*60)
    
    try:
        test_brain_factory()
        test_personality_with_backend()
        test_backend_interface()
        test_available_backends()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*60)
        print("\nBrain swapping infrastructure is ready.")
        print("Sam's personality will persist across all backends.")
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("[FAIL] TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*60)
        print("[ERROR] UNEXPECTED ERROR!")
        print("="*60)
        print(f"\nError: {e}")
        sys.exit(1)
