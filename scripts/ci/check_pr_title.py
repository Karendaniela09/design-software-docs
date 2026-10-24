#!/usr/bin/env python3
"""Check that the PR title follows Conventional Commits (docs repo types only).

The repo is squash-merged, so the PR title becomes the commit on ``main``.
Format: ``<type>(<scope>): <description>`` with type in docs|fix|chore|refactor.
The scope is optional. The title is read from ``--title`` or the ``PR_TITLE``
environment variable (never interpolate it into a shell command).
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import Reporter  # noqa: E402

ALLOWED_TYPES = ("docs", "fix", "chore", "refactor")
TITLE_RE = re.compile(rf"^({'|'.join(ALLOWED_TYPES)})(\(([^()\r\n]+)\))?: (\S.*)$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", default=os.environ.get("PR_TITLE"))
    args = parser.parse_args()

    report = Reporter("PR title")
    title = args.title
    if title is None:
        report.error("No PR title provided (set PR_TITLE or pass --title).")
        return report.finish("")

    title = title.strip()
    match = TITLE_RE.match(title)
    if not match:
        report.error(
            f"PR title does not follow Conventional Commits for this repo: {title!r}. "
            f"Expected '<type>(<scope>): <description>' with type one of "
            f"{'|'.join(ALLOWED_TYPES)} (scope optional), e.g. "
            "'docs(10-devops): add docs validation workflow'. "
            "The PR is squash-merged, so this title becomes the commit message."
        )
    return report.finish(f"title {title!r} is valid")


if __name__ == "__main__":
    sys.exit(main())
