#!/usr/bin/env python3
"""Install this skill into a user's Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1]
    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    target = (args.target or codex_root / "skills" / source.name).resolve()
    print(f"source: {source}")
    print(f"target: {target}")
    if args.dry_run:
        return 0
    if source == target:
        print("already installed")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix="codex-skill-", dir=target.parent))
    staged = staging_root / source.name
    backup: Path | None = None
    try:
        shutil.copytree(
            source,
            staged,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        if target.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = target.with_name(f"{target.name}.backup-{stamp}")
            target.replace(backup)
        staged.replace(target)
        print(f"installed: {target}")
        if backup:
            print(f"previous version preserved: {backup}")
        return 0
    except Exception:
        if backup and backup.exists() and not target.exists():
            backup.replace(target)
        raise
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
