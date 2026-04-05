#!/usr/bin/env python3
"""Export a pAI-Replicator code workspace as a clean PaperBench submission.

Usage:
    python export_direct_submission.py <repo_dir> <output_dir>

Creates a clean git repo at output_dir with:
- All tracked files from repo_dir
- reproduce.sh at root and executable
- .gitignore for results/
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Export PaperBench submission")
    parser.add_argument("repo_dir", type=Path, help="Source code workspace")
    parser.add_argument("output_dir", type=Path, help="Output directory for submission")
    args = parser.parse_args()

    src = args.repo_dir.resolve()
    dst = args.output_dir.resolve()

    if not src.is_dir():
        print(f"Error: {src} is not a directory", file=sys.stderr)
        sys.exit(1)

    if dst.exists():
        print(f"Error: {dst} already exists. Remove it first.", file=sys.stderr)
        sys.exit(1)

    # Copy repo
    print(f"Copying {src} → {dst}")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("results", "__pycache__", "*.pyc", ".git"))

    # Ensure reproduce.sh is executable
    rsh = dst / "reproduce.sh"
    if rsh.exists():
        rsh.chmod(0o755)
        print("reproduce.sh: executable")
    else:
        print("WARNING: reproduce.sh not found in submission", file=sys.stderr)

    # Ensure .gitignore
    gitignore = dst / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("results/\n__pycache__/\n*.pyc\n*.egg-info/\n")

    # Init git repo
    subprocess.run(["git", "-C", str(dst), "init"], capture_output=True)
    subprocess.run(["git", "-C", str(dst), "add", "-A"], capture_output=True)
    subprocess.run(
        ["git", "-C", str(dst), "commit", "-m", "PaperBench submission exported by pAI-Replicator"],
        capture_output=True,
    )

    # Verify git clean
    result = subprocess.run(
        ["git", "-C", str(dst), "clean", "-fdn"],
        capture_output=True, text=True,
    )
    if result.stdout.strip():
        print(f"WARNING: git clean would remove: {result.stdout.strip()}", file=sys.stderr)
    else:
        print("git clean -fd safety check: PASS")

    # Summary
    file_count = sum(1 for _ in dst.rglob("*") if _.is_file() and ".git" not in _.parts)
    print(f"\nSubmission exported: {dst}")
    print(f"Files: {file_count}")
    print(f"reproduce.sh: {'YES' if rsh.exists() else 'NO'}")


if __name__ == "__main__":
    main()
