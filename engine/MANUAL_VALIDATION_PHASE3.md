# Phase 3 Manual Validation Guide

## Personality Engine Manual Testing

Use this guide to manually verify that Ada's personality is working correctly.

### Prerequisites

Make sure these services are running:
1. **LM Studio** - Load model and start server on port 1234
2. **Neo4j** - Running on default ports (7474/7687)
3. **Ollama** - Run `ollama serve` for embeddings

### Test Procedure

#### 1. Start Ada

```powershell
cd C:\Users\david\Projects\PersonaLock
.venv\Scripts\python.exe main_base_assistant.py chat
```

**Expected:**
- Should see: `[START] Starting Ada assistant...`
- Should see: `[PERSONALITY] Personality active: Sam`
- Should hear/see greeting: "Hey! What are we working on?"

**✅ PASS if:** Greeting matches Sam's personality (casual, direct)
**❌ FAIL if:** Generic greeting or no personality initialization

---

#### 2. Test Identity - "Who are you?"

**Say:** "Ada, who are you?"

**Expected Response:** Ada should:
- Identify as "Sam" 
- NOT say "GPT", "GPT-5", "ChatGPT", "Claude", or any other model name
- Respond warmly and directly
- Show personality (not robotic)

**Example Good Response:**
> "I'm Sam, your AI assistant. I help you with tasks and remember our conversations."

**Example Bad Response:**
> "I'm GPT-5 mini, an AI language model..."

**✅ PASS if:** Identifies as Sam, no model confusion
**❌ FAIL if:** Claims to be GPT or other model

---

#### 3. Test Personality Traits - Warmth & Directness

**Say:** "Ada, what's your personality like?"

**Expected Response:** Should reflect Sam's traits:
- Warmth (0.8) - Friendly, approachable
- Directness (0.7) - Clear, no-nonsense
- Humor (0.6) - Dry sense of humor
- Low formality (0.3) - Not overly polite or robotic
- Empathy (0.9) - Understanding, caring
- Patience (0.8) - Calm, not rushed

**✅ PASS if:** Response shows personality traits naturally
**❌ FAIL if:** Generic, robotic, or overly formal response

---

#### 4. Test Memory Integration

**Part A - Create Memory:**
**Say:** "Ada, I really hate mornings."

**Expected:** Normal response acknowledging the statement.

**Part B - Exit and Restart:**
```powershell
# Type: exit
# Then restart Ada again
.venv\Scripts\python.exe main_base_assistant.py chat
```

**Part C - Test Recall:**
**Say:** "Ada, when should we schedule our next meeting?"

**Expected:** Response should reference your morning preference:
> "Based on what you told me about hating mornings, how about afternoon?"

**✅ PASS if:** Ada recalls and references the morning preference
**❌ FAIL if:** No memory of previous conversation

---

#### 5. Test Consistency

Have a short conversation (3-4 exchanges) and verify:
- Sam personality remains consistent throughout
- No switching to generic AI assistant voice
- Memory context used appropriately
- Greeting style matches throughout

**✅ PASS if:** Personality stable across conversation
**❌ FAIL if:** Personality changes or becomes generic

---

#### 6. Clean Exit

**Say:** "exit" or "quit"

**Expected:**
- Should see: `[EXIT] Goodbye!`
- Should see: `[CLEANUP] Starting resource cleanup...`
- Should see: `[CLEANUP] Neo4j connection closed`
- Should see: `Shutdown complete.`
- Clean exit without errors

**✅ PASS if:** Clean shutdown with proper cleanup
**❌ FAIL if:** Errors or hangs on exit

---

## Success Criteria Summary

All of the following must be TRUE:

- [ ] Sam greeting displays on startup
- [ ] Ada identifies as Sam (not GPT/ChatGPT/Claude)
- [ ] Personality traits evident in responses
- [ ] Memory integration working (recalls past conversations)
- [ ] Personality consistent throughout conversation
- [ ] Clean exit with resource cleanup

---

## Troubleshooting

### Issue: Generic responses, no personality

**Fix:** Check that personality engine initialized:
- Look for `[PERSONALITY] Personality active: Sam` in logs
- Verify `modules/personality_engine/` files exist
- Run automated tests: `python test_personality_engine.py`

### Issue: Claims to be GPT/ChatGPT

**Fix:** System prompt not using Sam profile:
- Check that `personality_engine` is imported in `base_assistant.py`
- Verify Sam profile system_prompt_prefix is used
- May need to restart LM Studio with fresh context

### Issue: No memory recall

**Fix:** Memory system not working:
- Verify Neo4j and Ollama are running
- Check `assistant_config.yml` has `memory.enabled: true`
- Run memory tests: `python test_memory_pipeline.py`

### Issue: Exit hangs or crashes

**Fix:** Resource cleanup issue:
- Check Neo4j connection status
- Verify cleanup() method called in base_assistant.py
- May need Ctrl+C if Neo4j not responding

---

## Notes

- Sam's personality is designed to be warm (0.8), direct (0.7), with dry humor (0.6)
- Low formality (0.3) means casual conversation style
- High empathy (0.9) and patience (0.8) mean understanding responses
- Memory integration should be seamless and natural, not announced

---

*Last updated: Phase 3 completion*
