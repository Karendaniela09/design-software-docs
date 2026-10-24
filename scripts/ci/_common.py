"""Shared helpers for the docs CI checks (Python 3 standard library only).

Every check compares the PR (HEAD) against its base so that it only reports what
the PR changes, never debt that already exists on ``main``.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable

# Make output safe on any console encoding (Windows consoles, CI logs).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - very old Pythons
        pass

IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"

ADR_DIR = "05-architecture/decisions/records"
OPENAPI_DIR = "07-api/contracts/openapi"


def git(*args: str, check: bool = True) -> str:
    """Run ``git`` and return stdout decoded as UTF-8."""
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(f"git {' '.join(args)} failed with exit code {proc.returncode}")
    return proc.stdout.decode("utf-8", "replace")


def git_bytes(*args: str) -> bytes:
    proc = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(f"git {' '.join(args)} failed with exit code {proc.returncode}")
    return proc.stdout


def merge_base(base: str, head: str) -> str:
    return git("merge-base", base, head).strip()


@dataclass(frozen=True)
class Change:
    status: str  # A, M, D, R, C, T
    path: str  # path in HEAD (or the deleted path for D)
    old_path: str | None = None  # source path for R / C


def changed_files(base_commit: str, head: str) -> list[Change]:
    """Files changed between ``base_commit`` and ``head`` (renames detected)."""
    raw = git("diff", "--name-status", "-z", "-M", base_commit, head)
    parts = raw.split("\0")
    changes: list[Change] = []
    i = 0
    while i < len(parts) and parts[i]:
        status = parts[i]
        if status[0] in "RC":
            changes.append(Change(status[0], parts[i + 2], parts[i + 1]))
            i += 3
        else:
            changes.append(Change(status[0], parts[i + 1]))
            i += 2
    return changes


def tree_files(ref: str) -> list[str]:
    raw = git("ls-tree", "-r", "--name-only", "-z", ref)
    return [p for p in raw.split("\0") if p]


def read_blob(ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def _escape_annotation(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


class Reporter:
    """Collects problems and prints them as GitHub annotations or plain text."""

    def __init__(self, check_name: str) -> None:
        self.check_name = check_name
        self.errors = 0
        self.warnings = 0

    def _emit(self, level: str, message: str, path: str | None, line: int | None) -> None:
        location = ""
        if path:
            location = path + (f":{line}" if line else "")
        if IN_ACTIONS:
            props = [f"title={_escape_annotation(self.check_name)}"]
            if path:
                props.append(f"file={_escape_annotation(path)}")
            if line:
                props.append(f"line={line}")
            print(f"::{level} {','.join(props)}::{_escape_annotation(message)}")
        else:
            prefix = level.upper()
            print(f"{prefix}: {location + ': ' if location else ''}{message}")

    def error(self, message: str, path: str | None = None, line: int | None = None) -> None:
        self.errors += 1
        self._emit("error", message, path, line)

    def warning(self, message: str, path: str | None = None, line: int | None = None) -> None:
        self.warnings += 1
        self._emit("warning", message, path, line)

    @staticmethod
    def info(message: str) -> None:
        print(message)

    def finish(self, ok_message: str) -> int:
        if self.errors:
            print(f"\n{self.check_name}: FAILED ({self.errors} error(s), {self.warnings} warning(s))")
            return 1
        print(f"{self.check_name}: OK - {ok_message}")
        return 0


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


ADR_PATH_RE = re.compile(rf"^{re.escape(ADR_DIR)}/ADR-(\d+)-[^/]+\.md$")


def adr_number(path: str) -> int | None:
    match = ADR_PATH_RE.match(path)
    return int(match.group(1)) if match else None
