#!/usr/bin/env python3
"""Check ADR number uniqueness.

Rules (only ADR files under 05-architecture/decisions/records/ADR-NNN-*.md):

1. In the PR tree (HEAD) no two ADR files may share the same number.
2. A NEW ADR file added by the PR may not reuse a number that already exists on
   the base branch (main) in a different file.
3. A NEW ADR file may not use a number that another OPEN PR with a LOWER number
   also adds in a different file (the older PR keeps the number; this PR must
   renumber). This is the "N open PRs claim ADR-020" case: it cannot be seen from
   main alone, so it queries the GitHub API (``gh``) with the workflow token.
   If the API is unavailable the cross-PR rule is skipped with a warning.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    Reporter,
    adr_number,
    changed_files,
    merge_base,
    tree_files,
)


def group_by_number(paths) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = defaultdict(list)
    for path in paths:
        number = adr_number(path)
        if number is not None:
            groups[number].append(path)
    return groups


def _gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip() or "gh failed")
    return proc.stdout.decode("utf-8", "replace")


def fetch_open_prs(repo: str, base_branch: str, below: int) -> list[dict]:
    """Open PRs targeting ``base_branch`` with a number lower than ``below``, with their files."""
    numbers = _gh(
        "api", "--paginate", f"repos/{repo}/pulls?state=open&base={base_branch}&per_page=100", "--jq", ".[].number"
    ).split()
    prs = []
    for number in sorted(int(n) for n in numbers):
        if number >= below:
            continue
        lines = _gh(
            "api", "--paginate", f"repos/{repo}/pulls/{number}/files?per_page=100",
            "--jq", '.[] | "\\(.status)\\t\\(.filename)"',
        ).splitlines()
        files = []
        for line in lines:
            status, _, filename = line.partition("\t")
            files.append({"status": status, "filename": filename})
        prs.append({"number": number, "files": files})
    return prs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument("--pr", type=int, default=int(os.environ.get("PR_NUMBER") or 0), help="this PR number")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/name for the GitHub API")
    parser.add_argument("--open-prs-json", help="offline fixture: [{number, files:[{status, filename}]}]")
    args = parser.parse_args()

    report = Reporter("ADR numbers")
    base_commit = merge_base(args.base, args.head)
    head_groups = group_by_number(tree_files(args.head))
    main_groups = group_by_number(tree_files(args.base))
    changes = changed_files(base_commit, args.head)
    removed = {c.path for c in changes if c.status == "D"} | {c.old_path for c in changes if c.status == "R"}
    new_adrs = {c.path: adr_number(c.path) for c in changes if c.status in "ACR" and adr_number(c.path) is not None}

    # Rule 1: uniqueness in the PR tree.
    for number, paths in sorted(head_groups.items()):
        if len(paths) > 1:
            report.error(
                f"ADR-{number:03d} is used by {len(paths)} files in the PR tree: "
                + ", ".join(os.path.basename(p) for p in sorted(paths))
                + ". Each ADR number must be unique.",
                sorted(paths)[0],
            )

    # Rule 2: new ADR reusing a number that already exists on main.
    for path, number in sorted(new_adrs.items()):
        clashes = [p for p in main_groups.get(number, []) if p != path and p not in removed]
        if clashes:
            report.error(
                f"New ADR reuses number {number:03d}, already used on {args.base} by "
                f"{os.path.basename(clashes[0])}. Renumber to the next free number.",
                path,
            )

    # Rule 3: another open (older) PR adds an ADR with the same number.
    if new_adrs:
        prs: list[dict] | None = None
        try:
            if args.open_prs_json:
                with open(args.open_prs_json, encoding="utf-8") as handle:
                    prs = [p for p in json.load(handle) if not args.pr or p["number"] < args.pr]
            elif args.pr and args.repo:
                prs = fetch_open_prs(args.repo, args.base.split("/", 1)[-1], args.pr)
            else:
                report.warning("Cross-PR rule skipped: PR number or repository not provided.")
        except (RuntimeError, OSError, ValueError, FileNotFoundError) as exc:
            report.warning(f"Cross-PR rule skipped: could not read open PRs ({exc}).")
        for pr in prs or []:
            for item in pr["files"]:
                other = item["filename"]
                number = adr_number(other)
                if number is None or item["status"] not in ("added", "renamed", "copied"):
                    continue
                for path, mine in sorted(new_adrs.items()):
                    if mine == number and path != other:
                        report.error(
                            f"ADR-{number:03d} is also added by older open PR #{pr['number']} "
                            f"({os.path.basename(other)}). The older PR keeps the number; "
                            "renumber this ADR to the next free number (also check numbers claimed by other open PRs).",
                            path,
                        )

    return report.finish("ADR numbers are unique")


if __name__ == "__main__":
    sys.exit(main())
