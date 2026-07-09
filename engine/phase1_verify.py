#!/usr/bin/env python3
"""Phase 1 Verification Script for PersonaLock"""

def verify_phase1():
    results = []
    
    # 1. Verify memory_vault imports
    print("\n=== PHASE 1 VERIFICATION ===\n")
    
    try:
        from modules.memory_vault.memory_manager import MemoryManager
        from modules.memory_vault.neo4j_client import Neo4jClient
        from modules.memory_vault.chroma_store import ChromaStore
        results.append(("modules/memory_vault/ imports", "EXISTS [OK]"))
    except ImportError as e:
        results.append(("modules/memory_vault/ imports", f"MISSING [X] - {e}"))

    # 2. Verify personality_engine imports
    try:
        from modules.personality_engine.profile import PersonalityProfile
        from modules.personality_engine.renderer import render_personality_to_prompt
        from modules.personality_engine import api
        results.append(("modules/personality_engine/ imports", "EXISTS [OK]"))
    except ImportError as e:
        results.append(("modules/personality_engine/ imports", f"MISSING [X] - {e}"))

    # 3. Verify config has memory and personality sections (check file directly)
    try:
        with open("assistant_config.yml", "r", encoding="utf-8") as f:
            config_content = f.read()
        has_memory = "memory:" in config_content
        has_personality = "personality:" in config_content
        if has_memory and has_personality:
            results.append(("assistant_config.yml memory/personality sections", "EXISTS [OK]"))
        else:
            missing = []
            if not has_memory: missing.append("memory:")
            if not has_personality: missing.append("personality:")
            results.append(("assistant_config.yml memory/personality sections", f"PARTIAL [!] - missing: {missing}"))
    except Exception as e:
        results.append(("assistant_config.yml memory/personality sections", f"MISSING [X] - {e}"))

    # 4. Verify dependencies in pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        has_neo4j = "neo4j" in content
        has_chromadb = "chromadb" in content
        if has_neo4j and has_chromadb:
            results.append(("neo4j/chromadb in pyproject.toml", "EXISTS [OK]"))
        else:
            missing = []
            if not has_neo4j: missing.append("neo4j")
            if not has_chromadb: missing.append("chromadb")
            results.append(("neo4j/chromadb in pyproject.toml", f"PARTIAL [!] - missing: {missing}"))
    except Exception as e:
        results.append(("neo4j/chromadb in pyproject.toml", f"MISSING [X] - {e}"))

    # 5. Verify integration stubs in base_assistant
    try:
        with open("modules/base_assistant.py", "r", encoding="utf-8") as f:
            content = f.read()
        has_memory_init = "self.memory_manager" in content and "MemoryManager" in content
        has_personality_init = "self.personality_profile" in content and "PersonalityProfile" in content
        has_personality_prompt = "_build_messages_with_personality" in content
        
        if has_memory_init:
            results.append(("MemoryManager initialized in PlainAssistant.__init__", "EXISTS [OK]"))
        else:
            results.append(("MemoryManager initialized in PlainAssistant.__init__", "MISSING [X]"))
            
        if has_personality_init and has_personality_prompt:
            results.append(("Personality loading wired into prompt construction", "EXISTS [OK]"))
        else:
            results.append(("Personality loading wired into prompt construction", "PARTIAL [!]"))
    except Exception as e:
        results.append(("Integration stubs in base_assistant", f"MISSING [X] - {e}"))

    # Print results
    print("-" * 60)
    for item, status in results:
        print(f"  {item}: {status}")
    print("-" * 60)
    
    # Summary
    all_good = all("EXISTS [OK]" in status for _, status in results)
    if all_good:
        print("\n*** PHASE 1 COMPLETE - All items verified! ***")
    else:
        print("\n*** PHASE 1 INCOMPLETE - Some items need attention ***")
    
    return all_good

if __name__ == "__main__":
    verify_phase1()
