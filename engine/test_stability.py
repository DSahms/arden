"""
Quick stability test - Phase 5

Tests error handling and wake word detection improvements.
"""

import sys
from modules.stability_helpers import (
    SimpleErrorHandler,
    ImprovedWakeWordDetector,
    get_friendly_error_message
)
import logging

def test_wake_word_detection():
    """Test improved wake word detection"""
    print("\n[TEST] Wake word detection...")
    
    detector = ImprovedWakeWordDetector(
        wake_word="ada",
        alternatives=["hey ada", "ada please", "sam"],
        fuzzy_threshold=0.75
    )
    
    # Test exact match
    detected, phrase = detector.detect("ada help me")
    assert detected == True, "Should detect 'ada'"
    
    # Test alternative
    detected, phrase = detector.detect("hey ada what time is it")
    assert detected == True, "Should detect 'hey ada'"
    
    # Test no match
    detected, phrase = detector.detect("hello there")
    assert detected == False, "Should not detect wake word"
    
    # Test fuzzy match (similar to ada)
    detected, phrase = detector.detect("add a task")  # 'add' is similar to 'ada'
    assert detected == True, "Should fuzzy match similar words"
    
    print("[PASS] Wake word detection test")

def test_error_handler():
    """Test error handler"""
    print("\n[TEST] Error handler...")
    
    logger = logging.getLogger("test")
    handler = SimpleErrorHandler(logger)
    
    # Test safe call with success
    def success_func():
        return "success"
    
    result = handler.safe_call(success_func, fallback_value="fallback")
    assert result == "success", "Should return function result"
    
    # Test safe call with failure
    def fail_func():
        raise ValueError("test error")
    
    result = handler.safe_call(fail_func, fallback_value="fallback")
    assert result == "fallback", "Should return fallback on error"
    
    print("[PASS] Error handler test")

def test_friendly_messages():
    """Test user-friendly error messages"""
    print("\n[TEST] Friendly error messages...")
    
    msg = get_friendly_error_message('brain_backend_failed')
    assert len(msg) > 0, "Should return a message"
    assert "trouble" in msg.lower() or "different" in msg.lower(), "Should be friendly"
    
    msg = get_friendly_error_message('unknown')
    assert len(msg) > 0, "Should have fallback message"
    
    print("[PASS] Friendly messages test")

def test_wake_word_command_extraction():
    """Test extracting command after wake word"""
    print("\n[TEST] Command extraction...")
    
    detector = ImprovedWakeWordDetector(wake_word="ada")
    
    command = detector.extract_command("ada help me with this", "ada")
    assert "help me" in command, "Should extract command after wake word"
    
    command = detector.extract_command("hey ada what time is it", "hey ada")
    assert "what time" in command, "Should extract command after phrase"
    
    print("[PASS] Command extraction test")

if __name__ == "__main__":
    print("="*60)
    print("STABILITY TEST SUITE - Phase 5")
    print("="*60)
    
    try:
        test_wake_word_detection()
        test_error_handler()
        test_friendly_messages()
        test_wake_word_command_extraction()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL STABILITY TESTS PASSED!")
        print("="*60)
        print("\nStability improvements ready:")
        print("- Error handling infrastructure in place")
        print("- Improved wake word detection with fuzzy matching")
        print("- User-friendly error messages")
        print("- Graceful degradation support")
        
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
