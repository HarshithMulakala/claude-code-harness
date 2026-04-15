# Harness (Claude Code plugin)

Structured build harness for Claude Code: specs, a feature backlog with verification steps, TDD-oriented implementation, adversarial QA, and session memory so work hands off cleanly between chats.

## Repository layout

```text
harness/
├── .claude-plugin/
│   └── plugin.json          # manifest (name, version, description, author)
├── hooks/
│   └── hooks.json           # PreToolUse / PostToolUse / Stop / SessionStart (loaded with the plugin)
├── skills/
│   ├── init/SKILL.md
│   ├── map/SKILL.md
│   ├── plan/SKILL.md
│   ├── build/SKILL.md
│   ├── verify/SKILL.md
│   ├── fix/SKILL.md
│   ├── status/SKILL.md
│   └── doctor/SKILL.md
├── settings.json            # see note below (plugin default settings)
└── README.md
```

Plugin metadata must live under **`.claude-plugin/plugin.json`** (not a single `.claude-plugin` file at the repo root). Skills live under **`skills/<folder>/SKILL.md`**; the folder name is the skill id inside this plugin’s namespace.

### Namespaced commands

Installed plugins namespace skills as **`/plugin-name:skill-folder`**. With manifest `"name": "harness"` and folders like `build`, `plan`, …, invoke:

| Command | Role |
|---------|------|
| `/harness:init` | Bootstrap `.harness/`, scripts, first commit |
| `/harness:map` | Read-only codebase map (brownfield) |
| `/harness:plan` | Specs, `FEATURES.json`, sprint contract |
| `/harness:build` | One failing feature, TDD, verify, commit |
| `/harness:verify` | Independent QA on passing features |
| `/harness:fix` | Top item on `FIX-PLAN.md` |
| `/harness:status` | Progress snapshot |
| `/harness:doctor` | Repair / validate harness state |

Short folder names keep commands readable (`/harness:build` instead of `/harness:harness-build`).

## What you get

- **`.harness/` state** — `FEATURES.json` (testable behaviors and pass/fail), `CURRENT-TASK.md`, `PROGRESS.md`, `FIX-PLAN.md`, `LEARNINGS.md`, specs, QA verdicts, and optional sprint contract.
- **`scripts/preflight.sh`** — Environment checks before work (no secret values printed).
- **`scripts/post-task.sh`** — Lint and typecheck (or stack-appropriate checks) after changes.
- **`CLAUDE.md`** — Project context for the agent, including harness command reference after init.

The harness separates **planning** (specs and features only), **building** (one feature, real verification, commits), **verifying** (independent QA; does not fix code), and **fixing** (one fix from the fix plan at a time).

## Install

1. **From a Git checkout or marketplace** — Add this repo as a [Claude Code plugin](https://code.claude.com/docs/en/plugins), enable **harness** for the project, then run `/reload-plugins` if needed.

2. **Local development** — Point Claude Code at the plugin directory:

   ```bash
   claude --plugin-dir ./harness
   ```

   Replace `./harness` with the path to this repository on your machine.

3. **Discover / marketplace installs** — Follow [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) for the current `/plugin` flows once the plugin is published (for example after you push this repo to GitHub and add it to a marketplace).

### Permissions and hooks shipped with the plugin

Per the [plugin structure overview](https://code.claude.com/docs/en/plugins), **`hooks/hooks.json`** at the plugin root is how event hooks ship with a plugin (here: secret-blocking **PreToolUse**, optional Prettier on save, **Stop** nudge when features remain, **SessionStart** env stamps).

**`settings.json`** at the plugin root is the standard place for [default settings when the plugin is enabled](https://code.claude.com/docs/en/plugins). This repo includes a **`permissions`** block aligned with the harness skills. Note that the same docs currently describe plugin `settings.json` as only applying certain keys (for example `agent`); if your Claude Code build ignores unknown keys, copy the `permissions` object into project or user [settings](https://code.claude.com/docs/en/settings) yourself. You do **not** need a separate merge script or `extras/` folder for a normal plugin install—hooks come from **`hooks/hooks.json`**, not from manually editing `~/.claude/settings.json`.

**Runtime notes**

- Hook commands use **bash** and **python3**; **Stop** and **SessionStart** use **jq** and **git** where noted. Ensure those exist on `PATH` for the environment that runs Claude Code hooks.
- The **PostToolUse** Prettier hook runs only when `node_modules/.bin/prettier` exists.
- **Stop** reads `.harness/FEATURES.json` and `.harness/CURRENT-TASK.md` relative to the session working directory; use the harness in a project root where `.harness/` exists after **`/harness:init`**.

## Quick start

1. **`/harness:init`** — Creates `.harness/`, starter state files, `scripts/`, and either auto-detects your stack (`package.json`, `Cargo.toml`, etc.) or installs placeholder scripts until planning fills them in. Expects a git repo and ends with a `harness: init` commit.
2. **Optional: `/harness:map`** — For existing codebases: read-only mapping into `.harness/specs/*.md` and `.harness/CODEBASE-MAP.md` (no implementation).
3. **`/harness:plan`** — Writes specs under `.harness/specs/`, appends rows to `FEATURES.json` (never deletes or edits existing feature metadata except as rules allow), captures preferences where specs are ambiguous, writes `SPRINT-CONTRACT.md`, and refreshes `preflight.sh` / `post-task.sh` / `CLAUDE.md` when they are still placeholders.
4. **`/harness:build`** — Picks one failing feature (highest priority), TDD, verifies against **real** infrastructure, updates `passes` only when verified, commits, and updates progress/current task.
5. **`/harness:verify`** — Fork-style QA: re-tests every feature with `passes: true`, scores robustness, writes `.harness/eval_feedback/{ID}.json` and `VERIFICATION-REPORT.md`; failures flip `passes` and land on `FIX-PLAN.md`.
6. **`/harness:fix`** — Addresses the top item on `FIX-PLAN.md` once per run, with tests and real verification.
7. **`/harness:status`** — Read-only summary: counts, current task, fix plan, recent git and progress log, plus a suggested next command.
8. **`/harness:doctor`** — Validates and repairs harness state (`FEATURES.json`, task file, verdict files, fix plan, git cleanliness, optional `.harness/.retry_count`, preflight report).

Typical loop: **init → (map) → plan → build** repeatedly → **verify → fix** until stable → **status** anytime → **doctor** after bad sessions or corrupted state.

After **`/harness:init`** in a project, you will also have `.harness/`, `scripts/preflight.sh`, `scripts/post-task.sh`, and usually `CLAUDE.md`.

## Rules that matter

- **`FEATURES.json`**: Do not delete entries or change `id`, `area`, `priority`, `description`, or `verify` on existing rows. Only add entries or toggle **`passes`** according to the build/verify/fix skills.
- **No stubs**: Build mode requires real implementations and tests that survive sessions.
- **Verification**: Build and verify use real services and data paths; verification does not “fix” code and does not mock integrations away.
- **Secrets**: Do not print env values; use `scripts/preflight.sh` for pass/fail style checks.
- **Scope**: One feature per build invocation; one fix per fix invocation; unrelated bugs go to `FIX-PLAN.md` for later.

## Requirements

- **Git** — Init and most skills assume commits on a real repository.
- **Shell tooling** — Scripts and doctor/status commands use `bash`, and several flows use **`jq`** for JSON. On Windows, use an environment where those commands exist (for example Git Bash or WSL) if your default shell does not provide them.

## Learn more

Each workflow’s steps, allowed tools, and commit message conventions are documented in the corresponding `skills/<name>/SKILL.md`. Read the skill you are about to run before changing harness behavior.
