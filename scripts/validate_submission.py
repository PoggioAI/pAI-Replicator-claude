#!/usr/bin/env python3
"""Validate a pAI-Replicator submission for PaperBench compliance.

Usage:
    python validate_submission.py <repo_dir> [--blacklist <blacklist.txt>]

Checks:
    1. reproduce.sh exists and is executable
    2. requirements.txt exists
    3. All files are git-tracked (no untracked dependencies)
    4. No blacklisted URLs in source files
    5. Total repo size < 500MB
    6. No absolute paths in Python/shell files
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def check_reproduce_sh(repo: Path) -> list[str]:
    rsh = repo / "reproduce.sh"
    issues = []
    if not rsh.exists():
        issues.append("CRITICAL: reproduce.sh not found at repo root")
        return issues
    if not os.access(rsh, os.X_OK):
        issues.append("reproduce.sh exists but is not executable (run: chmod +x reproduce.sh)")
    content = rsh.read_text()
    if not content.startswith("#!/"):
        issues.append("reproduce.sh missing shebang (should start with #!/usr/bin/env bash)")
    if "pip install" not in content and "conda install" not in content:
        issues.append("reproduce.sh does not install dependencies")
    return issues


def check_requirements(repo: Path) -> list[str]:
    if not (repo / "requirements.txt").exists():
        return ["requirements.txt not found"]
    return []


def check_git_tracked(repo: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=30,
        )
        untracked = [f for f in result.stdout.strip().split("\n") if f]
        # Filter out common noise
        untracked = [f for f in untracked if not f.startswith("results/") and f != ""]
        if untracked:
            return [f"Untracked files: {', '.join(untracked[:10])}{'...' if len(untracked) > 10 else ''}"]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ["Could not check git status (git not available or not a git repo)"]
    return []


def check_blacklist(repo: Path, blacklist_path: Path | None) -> list[str]:
    if blacklist_path is None or not blacklist_path.exists():
        return []
    urls = [line.strip() for line in blacklist_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
    if not urls:
        return []
    issues = []
    for root, _, files in os.walk(repo):
        for fname in files:
            if not fname.endswith((".py", ".sh", ".md", ".txt", ".yaml", ".yml", ".json", ".cfg", ".toml")):
                continue
            fpath = Path(root) / fname
            try:
                content = fpath.read_text(errors="ignore")
            except Exception:
                continue
            for url in urls:
                if url in content:
                    rel = fpath.relative_to(repo)
                    issues.append(f"Blacklisted URL '{url}' found in {rel}")
    return issues


def check_repo_size(repo: Path) -> list[str]:
    total = sum(f.stat().st_size for f in repo.rglob("*") if f.is_file())
    mb = total / (1024 * 1024)
    if mb > 500:
        return [f"Repo size {mb:.1f}MB exceeds 500MB limit"]
    return []


def check_absolute_paths(repo: Path) -> list[str]:
    abs_path_re = re.compile(r'["\']/(home|Users|root|tmp|var|opt|usr)/[^"\']+["\']')
    issues = []
    for root, _, files in os.walk(repo):
        for fname in files:
            if not fname.endswith((".py", ".sh", ".yaml", ".yml")):
                continue
            fpath = Path(root) / fname
            try:
                for i, line in enumerate(fpath.read_text(errors="ignore").splitlines(), 1):
                    if abs_path_re.search(line):
                        rel = fpath.relative_to(repo)
                        issues.append(f"Absolute path in {rel}:{i}")
            except Exception:
                continue
    return issues[:10]  # cap output


def main():
    parser = argparse.ArgumentParser(description="Validate PaperBench submission")
    parser.add_argument("repo_dir", type=Path, help="Path to the repo to validate")
    parser.add_argument("--blacklist", type=Path, default=None, help="Path to blacklist.txt")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    repo = args.repo_dir.resolve()
    if not repo.is_dir():
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(1)

    all_issues: dict[str, list[str]] = {}
    all_issues["reproduce_sh"] = check_reproduce_sh(repo)
    all_issues["requirements"] = check_requirements(repo)
    all_issues["git_tracked"] = check_git_tracked(repo)
    all_issues["blacklist"] = check_blacklist(repo, args.blacklist)
    all_issues["repo_size"] = check_repo_size(repo)
    all_issues["absolute_paths"] = check_absolute_paths(repo)

    total_issues = sum(len(v) for v in all_issues.values())
    report = {
        "repo": str(repo),
        "valid": total_issues == 0,
        "issue_count": total_issues,
        "checks": {k: {"passed": len(v) == 0, "issues": v} for k, v in all_issues.items()},
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "VALID" if report["valid"] else f"INVALID ({total_issues} issues)"
        print(f"Submission validation: {status}")
        print(f"Repo: {repo}\n")
        for check, data in report["checks"].items():
            icon = "PASS" if data["passed"] else "FAIL"
            print(f"  [{icon}] {check}")
            for issue in data["issues"]:
                print(f"         {issue}")

    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
