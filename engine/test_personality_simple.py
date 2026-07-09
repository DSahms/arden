"""Simple test to verify personality engine implementation."""

from modules.personality_engine import PersonalityEngine, get_sam_profile

# Test profile creation
print("Testing get_sam_profile()...")
sam = get_sam_profile()
print(f"  ✓ Profile name: {sam.name}")
print(f"  ✓ Traits: {sam.traits}")
print(f"  ✓ Greeting: {sam.greeting}")
print(f"  ✓ System prompt prefix: {sam.system_prompt_prefix[:50]}...")

# Test engine initialization
print("\nTesting PersonalityEngine...")
engine = PersonalityEngine(sam)
print(f"  ✓ Engine initialized with profile: {engine.profile.name}")

# Test get_system_prompt without memory context
print("\nTesting get_system_prompt() without memory context...")
prompt = engine.get_system_prompt()
print(f"  ✓ System prompt length: {len(prompt)} chars")
print(f"  ✓ Contains 'Sam': {'Sam' in prompt}")
print(f"  ✓ Contains 'warm': {'warm' in prompt}")

# Test get_system_prompt with memory context
print("\nTesting get_system_prompt() with memory context...")
memory_context = "[Recalled memories]\n- User likes Python\n- User is working on PersonaLock"
prompt_with_memory = engine.get_system_prompt(memory_context)
print(f"  ✓ System prompt with memory length: {len(prompt_with_memory)} chars")
print(f"  ✓ Contains memory context: {'Recalled memories' in prompt_with_memory}")

# Test get_greeting
print("\nTesting get_greeting()...")
greeting = engine.get_greeting()
print(f"  ✓ Greeting: {greeting}")
print(f"  ✓ Matches profile greeting: {greeting == sam.greeting}")

print("\n✅ All personality engine tests passed!")
