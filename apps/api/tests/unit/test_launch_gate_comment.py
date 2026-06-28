from __future__ import annotations

import subprocess
from pathlib import Path


def test_launch_gate_comment_uses_current_head() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    launch_dir = repo_root.as_posix().replace("C:/", "/mnt/c/")
    expected_sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    completed = subprocess.run(
        [
            "bash.exe",
            "-lc",
            f"cd {launch_dir} && ./scripts/launch-gate-comment.sh",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        completed.stdout.strip()
        == (
            "I confirm every PRODUCTION_READINESS.md checkbox is ticked and "
            "scripts/production-readiness-check.sh exits 0 against commit "
            f"{expected_sha}. Proceeding to flip DNS / promote prod."
        )
    )
