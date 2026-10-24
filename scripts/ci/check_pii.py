#!/usr/bin/env python3
"""Fail if the PR adds an identity document number (personal data).

Scope: only the lines ADDED by the PR (``+`` lines of the diff), in any text file.
Pattern: ``CC`` / ``C.C.`` / ``cédula`` / ``cedula`` followed (within a few
characters) by a number of 6 to 10 digits, optionally written with thousands
separators (``1.234.567``). The number is NEVER printed: findings are reported
as ``file:line`` plus the keyword and a masked number.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import Reporter, git, merge_base  # noqa: E402

KEYWORD = r"(?:\bCC\b|\bC\.C\b\.?|(?i:\bc[eé]dula\b))"
NUMBER = r"(?:\d{1,3}(?:[.,]\d{3}){2,3}|\d{6,10})(?![\d])(?![.,]\d)"
PATTERN = re.compile(rf"(?P<kw>{KEYWORD})(?P<sep>[^\d\n]{{0,20}}?)(?P<num>{NUMBER})")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def added_lines(diff: str):
    """Yield ``(path, line_number, text)`` for each added line of a unified diff."""
    path: str | None = None
    line_no = 0
    in_header = False
    for raw in diff.splitlines():
        if raw.startswith("diff --git "):
            in_header = True
            path = None
            continue
        if in_header:
            # File header lines (---/+++/index/rename...) end at the first hunk.
            if raw.startswith("+++ "):
                target = raw[4:].split("\t")[0]
                path = None if target == "/dev/null" else target[2:] if target[:2] in ("b/", "w/") else target
                continue
            if raw.startswith("@@"):
                in_header = False
            else:
                continue
        hunk = HUNK_RE.match(raw)
        if hunk:
            line_no = int(hunk.group(1))
            continue
        if path is None:
            continue
        if raw.startswith("+"):
            yield path, line_no, raw[1:]
            line_no += 1


def find_matches(text: str):
    """Yield ``(keyword, masked_number, digit_count)`` for each identity-number match."""
    for match in PATTERN.finditer(text):
        number = match.group("num")
        digits = re.sub(r"\D", "", number)
        if 6 <= len(digits) <= 10:
            yield match.group("kw"), "*" * len(digits), len(digits)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument("--staged", action="store_true", help="scan staged changes instead of base..head (local tests)")
    args = parser.parse_args()

    report = Reporter("Personal data")
    if args.staged:
        diff = git("diff", "--cached", "-U0", "--no-color", "--no-ext-diff")
    else:
        diff = git("diff", "-U0", "--no-color", "--no-ext-diff", "-M", merge_base(args.base, args.head), args.head)

    scanned = 0
    for path, line_no, text in added_lines(diff):
        scanned += 1
        for keyword, masked, count in find_matches(text):
            report.error(
                f"Possible identity document number ({keyword} {masked}, {count} digits). "
                "Remove it: personal data of real people must not be published. The value is masked here on purpose.",
                path,
                line_no,
            )
    return report.finish(f"{scanned} added line(s) scanned, no identity document numbers")


if __name__ == "__main__":
    sys.exit(main())
