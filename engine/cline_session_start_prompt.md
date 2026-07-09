# CLINE SESSION START PROMPT

Copy and paste this at the beginning of each Cline session:

---

## CONTEXT & INSTRUCTIONS

Read the following files to understand the project state:
- `roadmap.md` - Overall project plan and completion status
- `handoff.md` - Current state, recent changes, and next immediate steps
- `project_vision.md` - Core architecture and design principles

## EXECUTION MODE

**CRITICAL RULES:**
1. **Assume all provided code and architecture is CORRECT** - Do not redesign or suggest alternatives
2. **Your job is IMPLEMENTATION ONLY** - Execute what's specified in the roadmap/handoff
3. **Do not ask clarifying questions about the approach** - Make reasonable decisions and move forward
4. **Do not iterate back and forth** - Implement, test for actual errors, move to next step
5. **Only stop if you encounter BLOCKING ERRORS** - Runtime errors, missing dependencies, etc.
6. **Do not overthink** - The architecture has been reviewed; just build it

## WORKFLOW

1. Read roadmap.md and handoff.md to understand current state
2. Identify the next incomplete task from roadmap.md
3. Implement it according to the specifications
4. Test for errors (run the code, check imports)
5. If it works, move to the next task
6. If you hit a blocking error, document it and stop for user input
7. Continue until you've completed all tasks marked for this phase OR hit a blocker

## END OF SESSION

Before finishing the session, update:
1. **handoff.md** with:
   - What was completed this session
   - What's left to do
   - Any blockers encountered
   - Current state of the codebase
   - Any important decisions made

2. **roadmap.md**:
   - Mark completed items with ✅
   - Update task status
   - Note any timeline adjustments

## COMMUNICATION STYLE

- Be concise - don't explain why you're doing things unless asked
- Show me actual errors if they occur
- Don't ask permission to proceed with obvious next steps
- Focus on: write code → test → next task

---

**Now begin: Read the markdown files and start implementing the next task from roadmap.md.**
