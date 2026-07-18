from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _bash_command() -> str:
    program_files = os.environ.get("ProgramFiles")
    if program_files:
        git_bash = Path(program_files) / "Git" / "bin" / "bash.exe"
        if git_bash.is_file():
            return str(git_bash)
    return "bash"


def test_launch_gate_comment_uses_current_head() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    expected_sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    completed = subprocess.run(
        [
            _bash_command(),
            "-lc",
            "./scripts/launch-gate-comment.sh",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.strip() == (
        "I confirm every PRODUCTION_READINESS.md checkbox is ticked and "
        "scripts/production-readiness-check.sh exits 0 against commit "
        f"{expected_sha}. Proceeding to flip DNS / promote prod."
    )
