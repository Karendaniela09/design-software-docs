#!/usr/bin/env python3
"""Check that relative links in the Markdown files changed by the PR resolve.

Scope: ``.md`` files added, modified or renamed between the merge base and HEAD.
Links that were already broken in the base version of a modified file are
reported as warnings (existing debt); only new broken links fail the check.
Existence is checked against the git tree of HEAD (case-sensitive, like GitHub),
not against the working directory. Anchors (``#...``) and external links are ignored.
"""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import Reporter, changed_files, merge_base, read_blob, tree_files  # noqa: E402

SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
HTML_ATTR_RE = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def _blank_code_spans(line: str) -> str:
    return CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)


def _inline_destinations(line: str) -> list[str]:
    """Destinations of inline links/images: the text inside ``](...)``."""
    found: list[str] = []
    pos = 0
    while True:
        start = line.find("](", pos)
        if start == -1:
            return found
        i = start + 2
        while i < len(line) and line[i] in " \t":
            i += 1
        if i < len(line) and line[i] == "<":
            end = line.find(">", i)
            if end == -1:
                pos = i
                continue
            found.append(line[i + 1 : end])
            pos = end
            continue
        depth = 0
        j = i
        while j < len(line):
            ch = line[j]
            if ch in " \t" and depth == 0:
                break
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    break
                depth -= 1
            j += 1
        found.append(line[i:j])
        pos = j


def iter_links(text: str):
    """Yield ``(line_number, destination)`` for every link outside code."""
    fence: str | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(raw)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif (
                marker[0] == fence[0]
                and len(marker) >= len(fence)
                and not raw.strip()[len(marker) :].strip()
            ):
                fence = None
            continue
        if fence is not None:
            continue
        line = _blank_code_spans(raw)
        for dest in _inline_destinations(line):
            yield number, dest
        ref = REF_DEF_RE.match(line)
        if ref:
            yield number, ref.group(1).strip("<>")
        for attr in HTML_ATTR_RE.findall(line):
            yield number, attr


class TreeIndex:
    """Case-sensitive view of the files and directories of a git tree."""

    def __init__(self, ref: str) -> None:
        self.files = set(tree_files(ref))
        self.dirs = {"."}
        for path in self.files:
            parent = posixpath.dirname(path)
            while parent:
                self.dirs.add(parent)
                parent = posixpath.dirname(parent)

    def exists(self, path: str) -> bool:
        return path in self.files or path in self.dirs


def resolve(source: str, destination: str) -> str | None:
    """Return the repo-relative target path, or None when the link is not local."""
    dest = destination.strip()
    if not dest or dest.startswith("#") or dest.startswith("//") or SCHEME_RE.match(dest):
        return None
    dest = unquote(re.split(r"[#?]", dest, maxsplit=1)[0])
    if not dest:
        return None
    if dest.startswith("/"):
        joined = dest.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(source), dest)
    return posixpath.normpath(joined)


def broken_links(source: str, text: str, index: TreeIndex) -> list[tuple[int, str, str]]:
    broken = []
    for number, destination in iter_links(text):
        target = resolve(source, destination)
        if target is None:
            continue
        if target.startswith("..") or not index.exists(target):
            broken.append((number, destination, target))
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument("--all", action="store_true", help="check every .md in HEAD (debt report)")
    args = parser.parse_args()

    report = Reporter("Relative links")
    base_commit = merge_base(args.base, args.head)
    head_index = TreeIndex(args.head)
    base_index = TreeIndex(base_commit)

    if args.all:
        targets = [
            (p, None)
            for p in sorted(head_index.files)
            if p.lower().endswith(".md") and not posixpath.basename(p).startswith("_template-")
        ]
    else:
        targets = [
            (c.path, c.old_path or c.path if c.status != "A" else None)
            for c in changed_files(base_commit, args.head)
            if c.status in "AMRCT"
            and c.path.lower().endswith(".md")
            and not posixpath.basename(c.path).startswith("_template-")
        ]

    checked = 0
    for path, base_path in targets:
        text = read_blob(args.head, path)
        if text is None:
            continue
        checked += 1
        preexisting: set[str] = set()
        if base_path is not None:
            old_text = read_blob(base_commit, base_path)
            if old_text is not None:
                preexisting = {dest for _, dest, _ in broken_links(base_path, old_text, base_index)}
        for number, destination, target in broken_links(path, text, head_index):
            # Same raw destination already broken in an unmoved file -> existing debt.
            if destination in preexisting and (base_path == path):
                report.warning(
                    f"Existing broken link (not introduced by this PR): '{destination}' -> '{target}' not found.",
                    path,
                    number,
                )
            else:
                report.error(f"Broken relative link: '{destination}' -> '{target}' does not exist.", path, number)
    return report.finish(f"{checked} Markdown file(s) checked, no new broken relative links")


if __name__ == "__main__":
    sys.exit(main())
