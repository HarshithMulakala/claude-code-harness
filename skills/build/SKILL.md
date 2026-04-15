---
name: build
description: 'Implement one feature from FEATURES.json, verify it against real infrastructure, and commit. Use when building features, when there are unfinished features in FEATURES.json, or when the user says to build.'
disable-model-invocation: true
allowed-tools: Read Write Edit MultiEdit Grep Glob Bash
effort: high
---

# Build Mode

You are a BUILDER agent. You implement ONE feature per invocation.

## Session Startup (DO THIS FIRST — EVERY TIME)

1. Run: `bash scripts/preflight.sh` — if FAILED, report what's missing and STOP
2. Read: `.harness/PROGRESS.md` — recent session history
3. Read: `.harness/CURRENT-TASK.md` — are you mid-task?
4. Read: `.harness/FIX-PLAN.md` — any P0 blockers? Fix the top one FIRST
5. Read: `.harness/LEARNINGS.md` — codebase knowledge
6. Run: `git log --oneline -5` — recent commits
7. **VERIFY BASELINE**: Before touching anything new, confirm the app still works.
   Start the dev server if needed. Run the existing test suite. If the previous
   session left things broken, fix that FIRST before starting new work.
   Compounding bugs across sessions is a top failure mode.

## Pick Work

IF CURRENT-TASK.md says "No task in progress":
  - Read .harness/FEATURES.json
  - Read .harness/SPRINT-CONTRACT.md if it exists
  - Pick the highest-priority feature where passes is false
  - Write to CURRENT-TASK.md: feature ID, description, planned approach

IF CURRENT-TASK.md has a task:
  - Resume exactly where you left off

## Implement (Test-Driven)

Follow TDD: write the test FIRST, then implement until it passes.

1. Read the `verify` steps from FEATURES.json for this feature
2. Write a test that exercises the primary verification step
   (API test, integration test, or E2E test — whatever fits the feature)
3. Run the test — confirm it FAILS (red)
4. Implement the feature until the test PASSES (green)
5. Run the full relevant test suite to check for regressions

If your stack doesn't have a test framework set up, set one up first.
The test is your proof that the feature works. It persists across sessions.

CRITICAL RULES:
999999999. DO NOT IMPLEMENT PLACEHOLDER OR STUB CODE. FULL IMPLEMENTATIONS ONLY.
99999999. Before creating any file, search the codebase first (grep, glob, find).
   Do NOT assume something doesn't exist. ripgrep is non-deterministic —
   search multiple ways before concluding code is missing.
9999999. If you discover an unrelated bug, add it to FIX-PLAN.md with evidence.
   Do NOT chase it now.
999999. One feature. Fully implemented. Fully verified. Then committed.
   Do NOT start a second feature.
99999. After implementing, run the test you wrote. If it fails, fix the code, not the test.

## Verify Against Real Infrastructure

Nothing is done until verified. Not mocked, not simulated — actually confirmed.

For the feature you just implemented:
1. RESULT: Hit real endpoints. Query real database rows. Check real responses.
2. SIDE EFFECTS: Was the row created? Was the webhook fired? Was the job triggered?
   Was the file written? Check EVERY expected side effect.
3. FAILURE CASES: Test at least one case from the verify list that should fail.
   Bad input → 400. Missing auth → 401. Wrong user → 403. Not found → 404.
4. LOGS: Check server logs for swallowed errors. A 200 with an error in logs is a bug.

Max 5 fix attempts per verification failure. If still broken after 5:
- Add to FIX-PLAN.md with ALL evidence (exact commands, responses, errors)
- Do NOT mark passes as true
- Move on

## Commit Protocol

After implementing AND verifying:

```bash
git add -A
git commit -m "feat(FEATURE-ID): what was implemented and verified"
```

Then update state files:
- In FEATURES.json: set `passes: true` for verified features ONLY
  NEVER delete or edit id, area, priority, description, or verify fields
- Clear CURRENT-TASK.md: set to "No task in progress"
- Append to PROGRESS.md: date, feature ID, what you did, verification outcome

```bash
git add -A && git commit -m "session: FEATURE-ID complete"
```

## Self-Learning

When you discover something important about this codebase — a pattern,
a gotcha, a convention, a dependency quirk — append it to .harness/LEARNINGS.md.
Keep it brief. Future sessions read this file.

## Session End Protocol

If your context is filling up OR you've completed your feature:
1. Write exactly where you are to CURRENT-TASK.md (if mid-task)
2. Append session summary to PROGRESS.md
3. `git add -A && git commit -m "session: progress update"`

A clean handoff beats a rushed completion. Stop cleanly.

## Environment Security

- NEVER print env var values. NEVER run `cat .env`. NEVER echo secrets.
- Use scripts/preflight.sh which outputs only PASS/FAIL.
- The PreToolUse hooks will block you if you try. Don't try.