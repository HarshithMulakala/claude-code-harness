#!/usr/bin/env python3
"""
Merge this repo's plugin settings.json (permissions) and hooks/hooks.json (hooks)
into ~/.claude/settings.json.

- Unions permissions.allow and permissions.deny (sorted, deduped).
- Merges hooks per event name: appends fragment hooks whose JSON shape is not
  already present (dedupe by normalized JSON string).

Creates a timestamped backup of the target file before writing.
Does not remove or overwrite unrelated top-level keys (model, statusLine, etc.).
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def _norm(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def merge_permissions(user: dict, frag: dict) -> None:
    uperm = user.setdefault("permissions", {})
    fperm = frag.get("permissions") or {}
    for key in ("allow", "deny"):
        merged = sorted(set(uperm.get(key, [])) | set(fperm.get(key, [])))
        uperm[key] = merged


def merge_hooks(user: dict, frag: dict) -> None:
    uhooks = user.setdefault("hooks", {})
    fhooks = frag.get("hooks") or {}
    for event, frag_entries in fhooks.items():
        if not isinstance(frag_entries, list):
            continue
        existing = uhooks.get(event, [])
        if not isinstance(existing, list):
            existing = []
        seen = {_norm(e) for e in existing}
        for entry in frag_entries:
            sig = _norm(entry)
            if sig not in seen:
                existing.append(entry)
                seen.add(sig)
        uhooks[event] = existing


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    plugin_settings = repo_root / "settings.json"
    plugin_hooks = repo_root / "hooks" / "hooks.json"
    target = Path.home() / ".claude" / "settings.json"

    fragment: dict = {}
    fragment.update(json.loads(plugin_settings.read_text(encoding="utf-8")))
    fragment.update(json.loads(plugin_hooks.read_text(encoding="utf-8")))
    user: dict = {}
    if target.exists():
        user = json.loads(target.read_text(encoding="utf-8"))

    merge_permissions(user, fragment)
    merge_hooks(user, fragment)

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = target.with_suffix(f".json.bak.{stamp}")
        shutil.copy2(target, backup)
        print(f"Backup: {backup}")

    target.write_text(json.dumps(user, indent=2) + "\n", encoding="utf-8")
    print(f"Updated: {target}")


if __name__ == "__main__":
    main()
