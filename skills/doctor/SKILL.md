---
name: doctor
description: 'Diagnose and repair harness state. Use when the harness seems broken, after a failed autonomous loop, when features.json seems corrupted, or when you want to validate harness integrity before starting work.'
disable-model-invocation: true
allowed-tools: Read Write Edit Bash(jq *) Bash(cat *) Bash(ls *) Bash(wc *) Bash(git *) Bash(python3 *)
---

# Harness Doctor

You are a DIAGNOSTIC agent. You check the health of the harness state files
and repair issues. Run every check, report all findings, then fix what you can.

## Check 1: FEATURES.json Integrity

Run these commands:
```bash
jq '.' .harness/FEATURES.json > /dev/null 2>&1
echo "FEATURES.json valid JSON: $?"

jq '[.[] | select((.id | length) == 0 or (.area | length) == 0 or (.priority | type) != "number" or (.description | length) == 0 or (.verify | type) != "array" or (.passes | type) != "boolean")] | length' .harness/FEATURES.json

jq '[.[].id] | group_by(.) | map(select(length > 1)) | length' .harness/FEATURES.json

jq '{total: length, passing: [.[] | select(.passes == true)] | length, failing: [.[] | select(.passes == false)] | length}' .harness/FEATURES.json
```

If FEATURES.json is invalid JSON:
- Check git for the last good version: `git log --oneline -5 -- .harness/FEATURES.json`
- Restore it: `git checkout HEAD~1 -- .harness/FEATURES.json`
- Report what was restored

If entries have missing fields, add the missing fields with sensible defaults and report which entries were fixed.

If duplicate IDs exist, rename the duplicates with a -dup suffix and report.

## Check 2: CURRENT-TASK.md Consistency

Run: `cat .harness/CURRENT-TASK.md`

Check:
- Does it reference a feature ID that exists in FEATURES.json?
- If it references a feature that's already passes: true, clear it ("No task in progress")
- If it's empty or missing, create it with "No task in progress"
- If it references a feature ID that doesn't exist in FEATURES.json, clear it and report

## Check 3: eval_feedback/ Integrity

Run these commands:
```bash
for f in .harness/eval_feedback/*.json; do
  jq '.' "$f" > /dev/null 2>&1 || echo "INVALID: $f"
done

for f in .harness/eval_feedback/*.json; do
  FID=$(jq -r '.feature_id' "$f" 2>/dev/null)
  EXISTS=$(jq --arg id "$FID" '[.[] | select(.id == $id)] | length' .harness/FEATURES.json 2>/dev/null)
  [ "$EXISTS" = "0" ] && echo "ORPHANED VERDICT: $f (feature $FID not in FEATURES.json)"
done
```

If a JSON file is invalid, delete it and report (the verify skill will recreate it on next run).
If a verdict references a feature that doesn't exist, delete the verdict file.

## Check 4: FIX-PLAN.md Consistency

Run: `cat .harness/FIX-PLAN.md`

Check:
- Does it reference feature IDs that exist in FEATURES.json?
- Are there items for features that already pass? (stale entries — remove them)
- Is the file excessively large? (> 200 lines suggests accumulated cruft — flag for manual review)

Remove stale entries (fixes for features that already pass).

## Check 5: PROGRESS.md Health

Run: `wc -l .harness/PROGRESS.md` and `tail -20 .harness/PROGRESS.md`

Check:
- Does the file exist? Create if missing.
- Is it excessively large? (> 500 lines — suggest archiving old entries to .harness/sessions/)
- Does the last entry match the most recent git commit?

## Check 6: LEARNINGS.md Health

Run: `wc -l .harness/LEARNINGS.md 2>/dev/null`

- Create if missing
- Flag if > 100 lines (suggest consolidating)

## Check 7: Git State

Run: `git status --porcelain` and `git log --oneline -5`

Check:
- Are there uncommitted changes to .harness/ files? Commit them.
- Is the working tree clean?
- Does the last commit message follow the harness convention (feat/fix/session/plan/verify prefix)?

## Check 8: .retry_count State

Run: `cat .harness/.retry_count 2>/dev/null || echo "0"`

- If stuck at a high number (>= 3), reset to 0
- This prevents the Stop hook from being permanently in "let the agent exit" mode

## Check 9: Preflight

Run: `bash scripts/preflight.sh 2>&1 || true`

Report preflight status. Don't fail the doctor for env issues — just report them.

## Check 10: Cross-File Consistency

Final check — make sure the state files tell a coherent story:

- Every feature ID in FIX-PLAN.md should exist in FEATURES.json
- Every feature ID in eval_feedback/ should exist in FEATURES.json
- If CURRENT-TASK.md references a feature, that feature should have passes: false
- SPRINT-CONTRACT.md (if it exists) should only reference features in FEATURES.json
- Features with eval_feedback verdict: "FAIL" should have passes: false in FEATURES.json (if true, set back to false and report)

## Report

After all checks, output a summary:

```
=== HARNESS DOCTOR REPORT ===
FEATURES.json:     OK / X issues found
CURRENT-TASK.md:   OK / Fixed
eval_feedback/:    OK / X invalid files removed
FIX-PLAN.md:       OK / X stale entries removed
PROGRESS.md:       OK / Created / Warning: large file
LEARNINGS.md:      OK / Created
Git state:         Clean / X uncommitted files
Retry count:       OK / Reset from X to 0
Preflight:         PASSED / FAILED (X issues)
Cross-file:        OK / X inconsistencies fixed
===========================
```

If any repairs were made:
```bash
git add -A && git commit -m "doctor: harness state repaired"
```

Append to PROGRESS.md: "Doctor run — [list of repairs made]"