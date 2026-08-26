#!/usr/bin/env python3
"""Fast structural audit for the shared install/run contract."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT_FILES = ("run.bat", "run.ps1", "run.command", "run.sh")
ACTIONS = ("doctor", "repair", "docker", "logs", "stop")
HELPERS = ("scripts/install-utils.ps1", "scripts/install-utils.sh")


def tracked_mode(repo: Path, relative: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--stage", "--", relative],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode or not result.stdout.strip():
        return None
    return result.stdout.split(maxsplit=1)[0]


def audit(repo: Path) -> list[str]:
    issues: list[str] = []
    if not (repo / ".git").exists():
        return ["not a Git repository"]

    for relative in ROOT_FILES + HELPERS + ("README.md", "AGENTS.md", "CLAUDE.md"):
        if not (repo / relative).is_file():
            issues.append(f"missing {relative}")

    ps_path = repo / "run.ps1"
    sh_path = repo / "run.sh"
    readme_path = repo / "README.md"
    agents_path = repo / "AGENTS.md"
    claude_path = repo / "CLAUDE.md"
    ignore_path = repo / ".gitignore"

    ps_text = ps_path.read_text(encoding="utf-8", errors="replace") if ps_path.exists() else ""
    sh_text = sh_path.read_text(encoding="utf-8", errors="replace") if sh_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8", errors="replace") if readme_path.exists() else ""
    agents = agents_path.read_text(encoding="utf-8", errors="replace") if agents_path.exists() else ""
    claude = claude_path.read_text(encoding="utf-8", errors="replace") if claude_path.exists() else ""
    ignored = ignore_path.read_text(encoding="utf-8", errors="replace") if ignore_path.exists() else ""
    ps_helper = (repo / HELPERS[0]).read_text(encoding="utf-8", errors="replace") if (repo / HELPERS[0]).exists() else ""
    sh_helper = (repo / HELPERS[1]).read_text(encoding="utf-8", errors="replace") if (repo / HELPERS[1]).exists() else ""

    if "scripts\\install-utils.ps1" not in ps_text:
        issues.append("run.ps1 does not load scripts/install-utils.ps1")
    if "scripts/install-utils.sh" not in sh_text:
        issues.append("run.sh does not load scripts/install-utils.sh")
    if ".setup/" not in ignored:
        issues.append(".gitignore does not ignore .setup/")
    if '".setup"' not in ps_helper or '/.setup"' not in sh_helper:
        issues.append("install helpers do not both use .setup state")
    for action in ACTIONS:
        if action not in ps_text or action not in sh_text:
            issues.append(f"root launchers do not both expose {action}")
        if f"`{action}`" not in readme and action not in readme:
            issues.append(f"README does not document {action}")
    if ".setup/install.log" not in readme:
        issues.append("README does not identify .setup/install.log")
    if "## Install and run contract" not in agents:
        issues.append("AGENTS.md lacks the shared install/run contract")
    if "@AGENTS.md" not in claude:
        issues.append("CLAUDE.md does not import AGENTS.md")

    compose = any((repo / name).is_file() for name in ("compose.yaml", "compose.yml", "docker-compose.yml", "docker-compose.yaml"))
    if not compose:
        issues.append("missing Compose file")
    if not (repo / "Dockerfile").is_file():
        issues.append("missing Dockerfile")

    for relative in ("run.sh", "run.command", "scripts/install-utils.sh"):
        mode = tracked_mode(repo, relative)
        if mode is not None and mode != "100755":
            issues.append(f"{relative} is tracked with mode {mode}, expected 100755")

    forbidden = ("native-delivery.ps1", "native-delivery.sh", "launcher-common.ps1", "launcher-common.sh")
    for token in forbidden:
        if token in ps_text or token in sh_text or token in readme:
            issues.append(f"obsolete public name remains: {token}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repositories", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for requested in args.repositories:
        repo = requested.resolve()
        issues = audit(repo)
        if issues:
            failed = True
            print(f"FAIL {repo}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS {repo}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
