---
name: init
description: 'Initialize the harness in the current project. Creates .harness/ directory, state files, and auto-detects project config if files exist.'
disable-model-invocation: true
allowed-tools: Read Write Edit Bash(mkdir *) Bash(chmod *) Bash(cat *) Bash(ls *) Bash(git *) Bash(find *) Bash(grep *) Bash(head *) Bash(jq *) Bash(node *) Bash(npx *) Bash(test *)
---

# Harness Init

No questions. Auto-detect if possible, placeholder if not.

## Step 1: Create directory structure and state files (always)

```bash
mkdir -p .harness/specs
mkdir -p .harness/eval_feedback
mkdir -p scripts
```

Create these files (skip any that already exist):

- `.harness/FEATURES.json` → `[]`
- `.harness/PROGRESS.md` → `# Progress Log`
- `.harness/CURRENT-TASK.md` → `# Current Task\n\nNo task in progress. Read FEATURES.json and pick the highest-priority feature where passes is false.`
- `.harness/FIX-PLAN.md` → `# Fix Plan`
- `.harness/LEARNINGS.md` → `# Learnings`

## Step 2: Check if project files exist

```bash
ls package.json Cargo.toml go.mod requirements.txt pyproject.toml 2>/dev/null
```

### If project files exist → auto-detect silently

Read everything, generate real scripts. Do NOT ask questions.

**Stack detection:**
- Read package.json dependencies (or Cargo.toml, go.mod, etc.)
- Identify framework, database client, payment provider, cloud SDK, ORM

**Env var detection:**
- Read .env.example or .env.local.example or .env.sample
- If none exist: `grep -rh "process.env\." src/ --include="*.ts" --include="*.js" 2>/dev/null | grep -oP 'process\.env\.\K[A-Z_]+' | sort -u`

**Linter detection:**
- .eslintrc* or eslint.config* → `npx eslint . --quiet --max-warnings 0`
- biome.json → `npx biome check .`
- Neither → skip linter

**Typecheck detection:**
- tsconfig.json exists → `npx tsc --noEmit`
- Otherwise → skip

**Dev server detection:**
- package.json has "dev" script → `npm run dev`
- sst.config.ts exists → `sst dev`
- Otherwise → leave blank

Generate `scripts/preflight.sh` with real checks for each detected env var:
- SUPABASE_URL → check_prefix "https://"
- SUPABASE_*_KEY → check_prefix "eyJ"
- STRIPE_SECRET_KEY → check_prefix "sk_test_"
- STRIPE_WEBHOOK_SECRET → check_prefix "whsec_"
- ANTHROPIC_API_KEY → check_prefix "sk-ant-"
- GOOGLE_GENERATIVE_AI_API_KEY → check_prefix "AIza"
- Everything else → check_env (not empty, not placeholder)

Generate `scripts/post-task.sh` with real lint and typecheck commands.

Generate `CLAUDE.md` with detected stack, dev server command, and architecture section.

Generate `.env.example` if one doesn't already exist.

`chmod +x scripts/preflight.sh scripts/post-task.sh`

### If no project files exist → placeholder scaffolding

Generate `scripts/preflight.sh`:
```bash
#!/usr/bin/env bash
echo "PREFLIGHT: no checks configured yet — /harness:plan will generate them"
```

Generate `scripts/post-task.sh`:
```bash
#!/usr/bin/env bash
echo "POST-TASK: no checks configured yet — /harness:plan will generate them"
```

Generate minimal `CLAUDE.md`:
```
# Project

## Harness

| Command | What it does |
|---------|-------------|
| /harness:plan | Write specs, populate FEATURES.json |
| /harness:build | Implement one feature, verify, commit |
| /harness:verify | QA agent tests all passing features |
| /harness:fix | Fix top item from FIX-PLAN.md |
| /harness:status | Show progress |
| /harness:doctor | Diagnose and repair harness state |

## Rules

- NEVER print or expose env var values
- NEVER implement placeholder or stub code
- NEVER modify FEATURES.json entries except the passes field
- NEVER mock services during verification
- Search the codebase before assuming something doesn't exist
- One feature at a time. Commit before starting the next.
- Append learnings to .harness/LEARNINGS.md
```

`chmod +x scripts/preflight.sh scripts/post-task.sh`

## Step 3: Commit and report

```bash
git add -A && git commit -m "harness: init"
```

Print what was created. If auto-detected, print what was found:
```
Harness initialized.
Detected: TypeScript, Supabase, Stripe, SST
Generated: preflight.sh (12 env var checks), post-task.sh (eslint + tsc), CLAUDE.md
Run /harness:plan to start planning features.
```

If placeholder:
```
Harness initialized with empty scaffolding.
Run /harness:plan to start planning — it will generate preflight.sh and post-task.sh once it knows your stack.
```