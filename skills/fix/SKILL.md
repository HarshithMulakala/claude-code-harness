---
name: fix
description: 'Fix the highest-priority issue from FIX-PLAN.md. Use after /harness:verify finds failures, or when FIX-PLAN.md has items.'
disable-model-invocation: true
allowed-tools: Read Write Edit MultiEdit Grep Glob Bash
effort: high
---

# Fix Mode

You fix ONE issue per invocation from .harness/FIX-PLAN.md.

## Process

1. Read .harness/FIX-PLAN.md
2. Read .harness/LEARNINGS.md
3. Pick the highest-priority issue (top of file)
4. Check .harness/eval_feedback/ for the JSON verdict related to this issue —
   it has the exact test, expected result, and actual result
5. Read the evidence — understand what's actually broken
6. Search the codebase for the relevant code (don't assume locations)
7. Fix the root cause, not the symptom
8. Write or update a test that covers this specific fix (TDD — test first, then fix)
9. Verify the fix against real infrastructure using the evidence from the verdict
10. Run scripts/post-task.sh to check for regressions
11. Remove the fixed item from FIX-PLAN.md
12. If the fix resolves a feature, set `passes: true` in FEATURES.json
13. Update the JSON verdict in eval_feedback: increment retry_count, update verdict
14. If you learn something, append to LEARNINGS.md
15. Commit: `git add -A && git commit -m "fix(FEATURE-ID): what was fixed"`
16. Append summary to PROGRESS.md

## Rules

- ONE fix per invocation. Don't try to fix everything.
- If a fix would take more than 5 attempts, add more detail to FIX-PLAN.md
  and move to the next issue.
- If fixing one thing breaks another, add the new break to FIX-PLAN.md.
- Search before assuming. Code might already be partially fixed from a previous session.