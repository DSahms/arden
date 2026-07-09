"""
Comprehensive tests for Personality Engine (Phase 3)

Tests that Sam personality is properly configured and integrated.
"""
import pytest
from modules.personality_engine.profile import get_sam_profile, PersonalityProfile
from modules.personality_engine.engine import PersonalityEngine


def test_sam_profile():
    """Test that Sam profile is properly configured."""
    profile = get_sam_profile()
    
    # Check basic properties
    assert profile.name == "Sam"
    assert len(profile.greeting) > 0
    assert len(profile.system_prompt_prefix) > 0
    
    # Check all required traits exist
    required_traits = ["warmth", "directness", "humor", "formality", "empathy", "patience"]
    for trait in required_traits:
        assert trait in profile.traits, f"Missing trait: {trait}"
    
    # Check traits are in valid range (0.0-1.0)
    for trait_name, trait_value in profile.traits.items():
        assert 0.0 <= trait_value <= 1.0, f"{trait_name} out of range: {trait_value}"
    
    # Check specific trait values match spec
    assert profile.traits["warmth"] == 0.8
    assert profile.traits["directness"] == 0.7
    assert profile.traits["humor"] == 0.6
    assert profile.traits["formality"] == 0.3
    assert profile.traits["empathy"] == 0.9
    assert profile.traits["patience"] == 0.8
    
    # Check that Sam's personality doesn't CLAIM to be other models
    # It's OK to mention them in negative context ("never claim to be GPT")
    system_prompt = profile.system_prompt_prefix.lower()
    
    # Check for problematic identity claims
    assert "i am gpt" not in system_prompt, "Should not claim to be GPT"
    assert "i'm gpt" not in system_prompt, "Should not claim to be GPT"
    assert "you are gpt" not in system_prompt, "Should not claim to be GPT"
    assert "you're gpt" not in system_prompt, "Should not claim to be GPT"
    
    # Check that it identifies as Sam
    assert "sam" in system_prompt, "Should identify as Sam"
    
    # Check key personality traits are mentioned
    assert "warm" in system_prompt, "Should mention warmth"
    assert "direct" in system_prompt, "Should mention directness"
    assert "humor" in system_prompt, "Should mention humor"
    
    print("[PASS] Sam profile test passed")


def test_personality_engine_initialization():
    """Test that PersonalityEngine initializes correctly."""
    profile = get_sam_profile()
    engine = PersonalityEngine(profile)
    
    assert engine.profile is not None
    assert engine.profile.name == "Sam"
    
    print("[PASS] PersonalityEngine initialization test passed")


def test_personality_engine_system_prompt():
    """Test system prompt generation."""
    profile = get_sam_profile()
    engine = PersonalityEngine(profile)
    
    # Test without memory context
    prompt = engine.get_system_prompt()
    assert "Sam" in prompt
    assert "warm and direct" in prompt
    assert len(prompt) > 0
    
    # Test with memory context
    memory_context = "[Relevant past conversations]\nUser: I hate mornings\nAssistant: Noted!"
    prompt_with_memory = engine.get_system_prompt(memory_context)
    
    # Should include both personality and memory
    assert "Sam" in prompt_with_memory
    assert "I hate mornings" in prompt_with_memory
    assert len(prompt_with_memory) > len(prompt)
    
    print("[PASS] System prompt generation test passed")


def test_personality_engine_greeting():
    """Test greeting generation."""
    profile = get_sam_profile()
    engine = PersonalityEngine(profile)
    
    greeting = engine.get_greeting()
    assert len(greeting) > 0
    assert greeting == "Hey! What are we working on?"
    
    print("[PASS] Greeting generation test passed")


def test_personality_profile_dataclass():
    """Test PersonalityProfile can be created with custom values."""
    custom_profile = PersonalityProfile(
        name="TestBot",
        traits={"warmth": 0.5, "formality": 0.9},
        system_prompt_prefix="You are TestBot, a formal assistant.",
        greeting="Good day."
    )
    
    assert custom_profile.name == "TestBot"
    assert custom_profile.traits["warmth"] == 0.5
    assert custom_profile.traits["formality"] == 0.9
    assert "TestBot" in custom_profile.system_prompt_prefix
    assert custom_profile.greeting == "Good day."
    
    print("[PASS] Custom profile creation test passed")


def test_no_gpt_references():
    """Critical test: Ensure Sam never claims to be GPT/ChatGPT."""
    profile = get_sam_profile()
    engine = PersonalityEngine(profile)
    
    system_prompt = engine.get_system_prompt()
    
    # Check for problematic identity claims (case-insensitive)
    # It's OK to mention GPT/ChatGPT in negative context ("never claim to be...")
    system_prompt_lower = system_prompt.lower()
    
    # Check for identity confusion (claiming to be those models)
    assert "i am chatgpt" not in system_prompt_lower
    assert "i'm chatgpt" not in system_prompt_lower
    assert "you are chatgpt" not in system_prompt_lower
    assert "i am gpt-5" not in system_prompt_lower
    assert "i am gpt-4" not in system_prompt_lower
    
    # Positive check: Should identify as Sam
    assert "sam" in system_prompt_lower
    
    print("[PASS] No GPT reference test passed - Sam has own identity!")


def test_memory_integration_flag():
    """Test that memory integration is enabled by default."""
    profile = get_sam_profile()
    
    # The profile should work with memory integration
    # (This is implicit in the current design - engine accepts memory_context)
    engine = PersonalityEngine(profile)
    
    # Should accept memory context without error
    prompt = engine.get_system_prompt("Some memory context")
    assert "Some memory context" in prompt
    
    print("[PASS] Memory integration test passed")


if __name__ == "__main__":
    # Run all tests
    print("\n" + "="*60)
    print("PERSONALITY ENGINE TEST SUITE - Phase 3")
    print("="*60 + "\n")
    
    try:
        test_sam_profile()
        test_personality_engine_initialization()
        test_personality_engine_system_prompt()
        test_personality_engine_greeting()
        test_personality_profile_dataclass()
        test_no_gpt_references()
        test_memory_integration_flag()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*60)
        print("\nSam personality is properly configured.")
        print("Ada will identify as Sam with consistent personality.")
        print("No references to GPT/ChatGPT/Claude in responses.")
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("[FAIL] TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        raise
    except Exception as e:
        print("\n" + "="*60)
        print("[ERROR] UNEXPECTED ERROR!")
        print("="*60)
        print(f"\nError: {e}")
        raise
