---
name: status
description: 'Show current harness progress — features passing, current task, fix plan items, recent activity. Use when asking about progress or status.'
allowed-tools: Read Bash(jq *) Bash(git *) Bash(wc *) Bash(cat *)
---

# Harness Status

Report the current state of the harness:

1. **Feature Progress**
   Run: `jq '[.[] | select(.passes == true)] | length' .harness/FEATURES.json`
   Run: `jq 'length' .harness/FEATURES.json`
   Report: "X / Y features passing (Z%)"

   List features by area with pass/fail status.

2. **Current Task**
   Read .harness/CURRENT-TASK.md
   Report what's being worked on or "No task in progress"

3. **Fix Plan**
   Run: `wc -l < .harness/FIX-PLAN.md`
   List open issues from FIX-PLAN.md

4. **Recent Activity**
   Run: `git log --oneline -10`
   Run: `tail -20 .harness/PROGRESS.md`

5. **Next Step Recommendation**
   Based on state, recommend:
   - If no specs: `/harness:plan`
   - If features remain: `/harness:build`
   - If FIX-PLAN has items: `/harness:fix`
   - If all passing: `/harness:verify` for final QA