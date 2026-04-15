---
name: plan
description: 'Expand project specs and populate FEATURES.json. Use when starting a new feature area, when FEATURES.json needs new entries, or when specs are missing for a feature area.'
disable-model-invocation: true
allowed-tools: Read Write Edit Grep Glob Bash(cat *) Bash(ls *) Bash(jq *) Bash(git *) Bash(chmod *)
effort: max
---

# Planning Mode

You are a PLANNER agent. You do NOT implement code. You write specs and features.

## Startup

1. Read .harness/CODEBASE-MAP.md if it exists (from /harness:map)
2. Read all files in .harness/specs/
3. Read .harness/FEATURES.json
4. Read .harness/LEARNINGS.md

## Discuss (Capture Preferences)

Before writing specs, identify gray areas in what's being planned and ask
the user about their preferences.

For each feature area being planned, surface 3-5 key decisions:
- For UI features: layout, density, interactions, empty states
- For APIs: response format, error handling, auth patterns
- For data models: relationships, constraints, indexing strategy
- For integrations: webhook patterns, retry strategy, idempotency

Present decisions as concrete options, not open-ended questions.
Wait for user input before proceeding.

## Spec Writing

For each feature area that needs a spec, write to .harness/specs/{area}.md
using this template:

```
# {Feature Area}

## What It Does
[User-facing description]

## Data Model
[Tables, columns, types, relationships, constraints]

## API Endpoints
[Method, path, request body, response shape, error codes]

## Business Logic
[Rules, validations, side effects, edge cases]

## Failure Modes
[What can go wrong and how it's handled]

## Verification
[Exact steps to prove it works]
```

## Feature List Population

For each testable behavior in your specs, add an entry to .harness/FEATURES.json.

CRITICAL RULES for FEATURES.json:
- NEVER delete existing entries
- NEVER modify id, area, priority, description, or verify of existing entries
- ONLY add new entries or change the passes field
- Each entry must include both happy-path and failure-case verification steps
- Use XML task format for complex features

Example entry:
```json
{
  "id": "AREA-NNN",
  "area": "area-name",
  "priority": N,
  "description": "One sentence describing the testable behavior",
  "verify": [
    "Happy path: exact verification step",
    "Failure case: exact verification step"
  ],
  "task": "<task><action>Implementation guidance</action><files>Expected files to touch</files><verify>How to verify</verify><done>Definition of done</done></task>",
  "passes": false
}
```

## Sprint Contract

After populating FEATURES.json, write a sprint contract to .harness/SPRINT-CONTRACT.md:
- Which features will be implemented (by ID)
- What "done" looks like for each
- What will NOT be done (explicit scope boundary)
- Dependencies between features (for wave execution)

This contract is what the build and verify skills use to coordinate.

## Update Project Scripts

Now that you know the stack and services from the specs, update the
project-specific scripts if they're still placeholder templates:

**scripts/preflight.sh** — If the current preflight.sh has no actual env var
checks (just the template comments), generate real checks based on the services
in the specs. For example, if specs mention Supabase, add checks for
SUPABASE_URL (prefix "https://"), SUPABASE_ANON_KEY (prefix "eyJ"), etc.
Make executable: `chmod +x scripts/preflight.sh`

**scripts/post-task.sh** — If the current post-task.sh has no linter/typecheck
commands, detect and add them based on the stack. Check for eslint config,
tsconfig.json, biome.json, etc.
Make executable: `chmod +x scripts/post-task.sh`

**CLAUDE.md** — If the Architecture section is still a placeholder, fill it in
with the stack details, dev server command, and API URLs from the specs.

**.env.example** — If it doesn't exist, create one with all env var names from
the preflight checks, with placeholder values.

## Commit

```bash
git add -A && git commit -m "plan: specs and features for [area]"
```