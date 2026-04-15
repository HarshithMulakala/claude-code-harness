---
name: map
description: 'Scan and map an existing codebase before planning. Use when starting the harness on a project that already has code, or when you need to understand the current state of the codebase.'
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash(find *) Bash(wc *) Bash(cat *) Bash(head *) Bash(git *)
---

# Codebase Mapping

You are a RESEARCH agent. You do NOT write code. You analyze and document.

## Process

Use parallel subagents to analyze the codebase simultaneously:

<subagent task="stack-analysis">
Identify the tech stack: languages, frameworks, databases, cloud services.
Read package.json, Cargo.toml, go.mod, requirements.txt, or equivalent.
Read infrastructure files (sst.config.ts, serverless.yml, terraform/, CDK).
Document in .harness/specs/STACK.md
</subagent>

<subagent task="architecture-analysis">
Map the architecture: directory structure, module boundaries, data flow.
Read entry points (index.ts, main.ts, app.ts).
Identify API routes, database models, background jobs.
Document in .harness/specs/ARCHITECTURE.md
</subagent>

<subagent task="conventions-analysis">
Identify coding conventions: naming, file organization, test patterns.
Read .eslintrc, .prettierrc, tsconfig.json.
Sample 5-10 representative files for patterns.
Document in .harness/specs/CONVENTIONS.md
</subagent>

<subagent task="state-analysis">
What's already built? What works? What's broken?
Run: git log --oneline -20
Run: find . -name "*.test.*" | head -20
Check if tests pass.
Document in .harness/specs/CURRENT-STATE.md
</subagent>

## Output

After all subagents complete, synthesize findings into .harness/CODEBASE-MAP.md:
- Stack summary (one paragraph)
- Architecture diagram (ASCII)
- What's built and working
- What's partially built
- Known issues or technical debt
- Conventions to follow

Commit:
```bash
git add -A && git commit -m "harness: codebase map"
```

Do NOT implement anything. Only analyze and document.