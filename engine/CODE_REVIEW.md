# PersonaLock Code Review - February 11, 2026

## Summary

Reviewed entire codebase focusing on memory/state layer, LLM backend switching, and persona injection. Found **4 critical bugs**, **3 security issues**, **2 race conditions**, **5 error handling gaps**, and **6 foreseeable production problems**.

---

## CRITICAL BUGS

### BUG-1: `_store_memory()` has broken indentation (base_assistant.py)

**Severity:** HIGH - Memory storage silently fails
**Location:** `modules/base_assistant.py`, `_store_memory()` method

The inner try block is indented one level too deep. The `memory_id = self.memory_manager.remember(...)` line is inside a bare try with no matching except at that level.

```python
# CURRENT (broken):
def _store_memory(self, content, memory_type="fact", importance=0.5):
    if not self.memory_manager:
        return
    try:
            memory_id = self.memory_manager.remember(...)  # Extra indent!
            if memory_id:
                ...
    except Exception as e:  # This catches the outer try, not the inner code
        ...
```

**Fix:** Remove the extra indentation level.

---

### BUG-2: "remember this" double-appends to conversation_history (base_assistant.py)

**Severity:** MEDIUM - Corrupts conversation history
**Location:** `modules/base_assistant.py`, `process_text()` method

The user message is appended to `conversation_history` at line ~315 (`self.conversation_history.append({"role": "user", "content": text})`), then the "remember this" handler appends it AGAIN at the bottom of that block. Same issue with "forget this".

**Fix:** Remove the duplicate appends inside the command handlers.

---

### BUG-3: Exit command never triggers (main_base_assistant.py)

**Severity:** HIGH - Can't exit cleanly via voice
**Location:** `main_base_assistant.py`, `process_text()` inner function

The exit check does:
```python
if text.lower().strip() in ["exit", "quit"]:
```

But `text` is the FULL speech input which includes the wake word, e.g., "Ada exit". So `"ada exit"` will never match `["exit", "quit"]`. The exit command only works if the user says ONLY "exit" without the wake word.

**Fix:** Check after stripping the wake word, or use `text_lower.endswith("exit")` or `"exit" in text_lower`.

---

### BUG-4: ChromaDB persist directory mismatch

**Severity:** MEDIUM - Could lose all stored memories on startup
**Location:** `assistant_config.yml` vs actual data

Config says: `persist_directory: ".chromadb"`
But actual data lives in: `data/chroma/`

If the config path doesn't match where data was previously stored, ChromaDB will create a NEW empty database, and all previous memories are lost.

**Fix:** Verify which path has actual data and make config match.

---

## SECURITY VULNERABILITIES

### SEC-1: Neo4j password in plaintext config

**Severity:** HIGH
**Location:** `assistant_config.yml`

```yaml
neo4j:
    password: "password"
```

The Neo4j password is stored in plaintext. If this file is committed to git (it's not in .gitignore), credentials leak.

**Fix:** Use environment variables: `password: ${NEO4J_PASSWORD}` or read from `.env`.

---

### SEC-2: API keys can be set in config file

**Severity:** MEDIUM
**Location:** `assistant_config.yml`

Claude and OpenAI API keys have placeholder fields in the YAML:
```yaml
claude:
  api_key: ""  # Someone might paste their key here
```

**Fix:** Remove `api_key` fields from config. Document that env vars are the only supported method. Both backends already check env vars as fallback.

---

### SEC-3: No prompt injection protection

**Severity:** LOW (local-first app)
**Location:** `modules/base_assistant.py`, all LLM calls

User input goes directly into LLM prompts and memory storage without any sanitization. A user could craft input that overrides Sam's personality instructions.

**Fix:** For a local-first app this is low risk (user is the attacker). But if ever exposed as a service, add input sanitization.

---

## RACE CONDITIONS

### RACE-1: Conversation history mutation during speech processing

**Severity:** MEDIUM
**Location:** `modules/base_assistant.py`, `process_text()`

The `conversation_history` list is mutated during processing. The speech recognition runs in a callback pattern:
```python
recorder.text(process_text)  # Callback-based
```

If speech recognition fires a new callback before the previous one finishes (which the `recorder.stop()/start()` pattern tries to prevent), the history list could be corrupted.

**Fix:** The current `recorder.stop()` before processing and `recorder.start()` after is the right idea but doesn't protect against edge cases. Add a threading lock around history mutations, or use a queue.

---

### RACE-2: Config file re-read on every call

**Severity:** LOW
**Location:** `modules/assistant_config.py`, `get_config()`

The YAML config file is re-read from disk on EVERY call to `get_config()`. During initialization, this is called ~20+ times. If the file is being edited while the assistant starts, you could get inconsistent config.

**Fix:** Cache the config in memory after first read:
```python
_config_cache = {}
def get_config(key, ...):
    if not _config_cache:
        _config_cache.update(yaml.safe_load(...))
    ...
```

---

## ERROR HANDLING GAPS

### ERR-1: process_text() re-raises exceptions, crashes the app

**Severity:** HIGH
**Location:** `modules/base_assistant.py`, `process_text()`, last line

```python
except Exception as e:
    self.logger.error(f"[ERROR] Error occurred: {str(e)}")
    raise  # <-- This crashes the entire assistant
```

**Fix:** Return a friendly error message instead of raising. The assistant should never crash on a single bad input.

---

### ERR-2: speak() re-raises exceptions

**Severity:** MEDIUM
**Location:** `modules/base_assistant.py`, `speak()`

If TTS fails (e.g., audio device disconnected), the exception propagates up and crashes the assistant.

**Fix:** Catch and log TTS errors, fall back to print-only mode.

---

### ERR-3: No timeout on brain backend generate_response()

**Severity:** HIGH
**Location:** `modules/base_assistant.py`, brain backend call

If the LLM hangs (LM Studio freezes, Ollama OOMs), `generate_response()` blocks forever and the entire application freezes.

The LM Studio backend has a timeout parameter but it's in the HTTP request. If the model is loaded but slow, it could exceed timeout and return an error string instead of raising.

**Fix:** Add a wrapper with `threading.Timer` or `signal.alarm` to enforce hard timeouts.

---

### ERR-4: Brain backend errors return error strings as "responses"

**Severity:** MEDIUM
**Location:** All brain backends

When backends fail, they return error strings like `"LM Studio connection error: ..."` as the response text. This gets spoken to the user and stored in memory as if it were a real response.

**Fix:** Raise exceptions from backends, catch in base_assistant, and return friendly messages instead.

---

### ERR-5: Stability helpers imported but not actually used

**Severity:** LOW
**Location:** `modules/base_assistant.py`

The `SimpleErrorHandler`, `ImprovedWakeWordDetector`, and `get_friendly_error_message` are imported but never instantiated or used in the class. They're dead imports.

**Fix:** Either integrate them into the actual code paths or remove the imports.

---

## FORESEEABLE PRODUCTION PROBLEMS

### PROD-1: Conversation history grows unbounded

**Severity:** HIGH - Will cause OOM or context overflow
**Location:** `modules/base_assistant.py`, `conversation_history`

The `conversation_history` list grows forever during a session. After ~50 exchanges:
- Memory usage increases significantly
- The system prompt + history exceeds LLM context window (typically 4K-8K tokens for local models)
- LLM starts producing garbage or errors

**Fix:** Implement a sliding window: keep only the last N exchanges (e.g., 10-20) in conversation_history. Older exchanges are already in memory vault.

---

### PROD-2: Conversation sessions never end in Neo4j

**Severity:** LOW - Data accumulation
**Location:** `modules/base_assistant.py`

`create_conversation()` is called on startup but `end_conversation()` is never called in `cleanup()`. Over time, Neo4j accumulates orphaned "active" conversations.

**Fix:** Call `self.neo4j_client.end_conversation(self.current_conversation_id)` in `cleanup()`.

---

### PROD-3: Old LM Studio module still exists but unused

**Severity:** LOW - Confusion
**Location:** `modules/lm_studio.py`

The old `lm_studio.py` module with `conversational_prompt()` still exists but is no longer imported by base_assistant.py (which now uses brain backends). This could confuse future developers.

**Fix:** Either remove the file or add a deprecation notice at the top.

---

### PROD-4: Memory recall has no deduplication

**Severity:** MEDIUM
**Location:** `modules/base_assistant.py`, `_recall_memories()`

If the user says something very similar to a previous exchange, ChromaDB might return multiple copies of essentially the same memory (especially if the same exchange was stored multiple times). This wastes context window space.

**Fix:** Add deduplication logic - compare content strings before adding to context.

---

### PROD-5: "forget this" command is a no-op

**Severity:** MEDIUM - User trust issue
**Location:** `modules/base_assistant.py`

The "forget this" command says "I've removed the most recent exchange from my memory" but actually does nothing. The memory remains in both Neo4j and ChromaDB. This is documented but could erode user trust.

**Fix:** Implement actual deletion using `MemoryManager` + `ChromaStore.delete_memory()` + `Neo4jClient.delete_memory()`.

---

### PROD-6: Brain backend initialization may block startup

**Severity:** MEDIUM
**Location:** `modules/base_assistant.py`, `_initialize_brain_backend()`

The `is_available()` check for each backend makes HTTP requests. If the network is slow or a service is starting up, initialization could take 30+ seconds (5s timeout per backend * fallback chain).

**Fix:** Add a quick-fail option: if default backend isn't available within 5s, print a clear message and continue with a "no brain" state that prompts the user to check services.

---

## QUICK WINS (Fix these first)

| Priority | Issue | Effort |
|----------|-------|--------|
| 1 | BUG-1: Fix _store_memory indentation | 2 min |
| 2 | BUG-3: Fix exit command detection | 5 min |
| 3 | ERR-1: Don't re-raise in process_text | 5 min |
| 4 | ERR-2: Don't re-raise in speak | 5 min |
| 5 | BUG-2: Fix double-append in remember/forget | 5 min |
| 6 | PROD-1: Add conversation history trimming | 10 min |
| 7 | BUG-4: Verify ChromaDB path | 5 min |

---

## Architecture Assessment

**What's Good:**
- Clean separation of concerns (personality, memory, brain backends)
- Graceful degradation pattern (optional imports with fallbacks)
- Well-documented code with docstrings
- Configuration-driven architecture
- The "keep the soul, change the brain" design is elegant

**What Needs Work:**
- Error handling is inconsistent (some places catch/log, others re-raise)
- No conversation history management (unbounded growth)
- Several dead code paths and unused imports
- Config is re-read from disk on every access
- Some commands that claim to work don't actually work (forget this)

**Overall:** The architecture is solid for a local-first app. The critical bugs are all fixable in ~30 minutes. The biggest production risk is the unbounded conversation history, which should be addressed before daily use.

---

*Review completed February 11, 2026*
