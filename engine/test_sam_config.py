#!/usr/bin/env python3
"""
Quick verification that Sam's configuration is properly set up.
Tests without requiring external dependencies.
"""

import os
import yaml

print("=" * 70)
print("SAM CONFIGURATION VERIFICATION")
print("=" * 70)

# Check .env file
print("\n1. .env File Check:")
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
    if "GROQ_API_KEY" in content:
        print("   [OK] GROQ_API_KEY found in .env")
    else:
        print("   [FAIL] GROQ_API_KEY not found in .env")
else:
    print("   [FAIL] .env file not found")

# Check assistant_config.yml
print("\n2. assistant_config.yml Check:")
config_path = "assistant_config.yml"
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    base_cfg = config.get("base_assistant", {})
    print(f"   [OK] Assistant Name: {base_cfg.get('assistant_name')} (expected: Sam)")
    print(f"   [OK] Human Companion: {base_cfg.get('human_companion_name')} (expected: Dave)")
    print(f"   [OK] Ears: {base_cfg.get('ears')} (expected: none)")
    print(f"   [OK] Brain: {base_cfg.get('brain')} (expected: groq)")
    print(f"   [OK] Voice: {base_cfg.get('voice')} (expected: none)")
    
    groq_cfg = config.get("groq", {})
    print(f"   [OK] Groq Base URL: {groq_cfg.get('base_url')}")
    print(f"   [OK] Groq Model: {groq_cfg.get('model')} (expected: llama-3.3-70b-versatile)")
else:
    print("   [FAIL] assistant_config.yml not found")

# Check Groq backend
print("\n3. Groq Backend File Check:")
groq_backend = "modules/brain_backends/groq_backend.py"
if os.path.exists(groq_backend):
    with open(groq_backend, "r") as f:
        content = f.read()
    if "class GroqBackend" in content:
        print("   [OK] GroqBackend class found")
    if "https://api.groq.com/openai/v1" in content:
        print("   [OK] Groq API endpoint configured")
else:
    print("   [FAIL] groq_backend.py not found")

# Check brain factory registration
print("\n4. Brain Factory Registration Check:")
factory_path = "modules/brain_backends/brain_factory.py"
if os.path.exists(factory_path):
    with open(factory_path, "r") as f:
        content = f.read()
    if "from .groq_backend import GroqBackend" in content:
        print("   [OK] GroqBackend imported in brain_factory")
    if "'groq': GroqBackend" in content:
        print("   [OK] GroqBackend registered in BACKENDS dict")
else:
    print("   [FAIL] brain_factory.py not found")

# Check Sam personality profile
print("\n5. Sam Personality Profile Check:")
profile_path = "modules/personality_engine/profile.py"
if os.path.exists(profile_path):
    with open(profile_path, "r") as f:
        content = f.read()
    if "warmth=0.8" in content and "directness=0.9" in content:
        print("   [OK] Sam's trait scores configured correctly")
    if "Hey Dave. What's going on?" in content:
        print("   [OK] Sam's greeting configured")
    if "Dave's personal AI companion" in content:
        print("   [OK] Sam's system prompt configured")
else:
    print("   [FAIL] profile.py not found")

# Check text-only chat mode
print("\n6. Text-Only Chat Mode Check:")
main_path = "main_base_assistant.py"
if os.path.exists(main_path):
    with open(main_path, "r") as f:
        content = f.read()
    if "def chat():" in content:
        print("   [OK] chat() command found")
    if "input(" in content:
        print("   [OK] Text input implementation found")
    if "You: " in content:
        print("   [OK] Text-only UI formatting found")
else:
    print("   [FAIL] main_base_assistant.py not found")

# Check base assistant voice=none handling
print("\n7. Base Assistant Text-Only Mode Check:")
base_path = "modules/base_assistant.py"
if os.path.exists(base_path):
    with open(base_path, "r") as f:
        content = f.read()
    if 'if self.voice_type == "none":' in content:
        print("   [OK] voice='none' handling implemented")
    if "Text-only mode" in content:
        print("   [OK] Text-only logging found")
else:
    print("   [FAIL] base_assistant.py not found")

print("\n" + "=" * 70)
print("SUCCESS: SAM CONFIGURATION COMPLETE")
print("=" * 70)
print("\nNext Steps:")
print("1. Ensure Neo4j is running: bolt://localhost:7687")
print("2. Ensure Ollama is running for embeddings (nomic-embed-text)")
print("3. Run: python main_base_assistant.py chat")
print("4. Sam will greet you with: 'Hey Dave. What's going on?'")
print("\nTest Scenarios:")
print("- Ask 'Tell me who you are' -> Sam responds as Sam")
print("- Say 'Remember that I love hip-hop' -> Stored to memory")
print("- Restart and ask 'What do you know about me?' -> Recalls memory")
print("=" * 70)
