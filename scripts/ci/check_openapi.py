#!/usr/bin/env python3
"""Lint the OpenAPI contracts touched by the PR and fail only on NEW errors.

Runs ``npx @redocly/cli@1 lint`` (config: the repo ``redocly.yaml``) on the
``07-api/contracts/openapi/*.yaml`` files changed by the PR, once on the HEAD
version and once on the merge-base version. Errors are compared as a multiset of
``(rule, file, pointer, message)`` keys, so line shifts do not matter and errors
that already exist on main do not fail the PR. Warnings are only counted.

If ``_shared.yaml`` or ``redocly.yaml`` changes, every spec is linted (the others
``$ref`` the shared components). Both versions are exported from git into
temporary directories, so the working tree is not used.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import OPENAPI_DIR, Reporter, changed_files, git_bytes, merge_base, tree_files  # noqa: E402

REDOCLY_CONFIG = "redocly.yaml"
REDOCLY_PACKAGE = "@redocly/cli@1"


def export_tree(ref: str, dest: str) -> None:
    """Extract the OpenAPI directory and redocly.yaml of ``ref`` into ``dest``."""
    paths = [p for p in (OPENAPI_DIR, REDOCLY_CONFIG) if p in tree_files_set(ref)]
    if not paths:
        return
    data = git_bytes("archive", "--format=tar", ref, "--", *paths)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        try:
            archive.extractall(dest, filter="data")  # Python >= 3.11.4
        except TypeError:  # pragma: no cover - older Python without extraction filters
            archive.extractall(dest)


_TREE_CACHE: dict[str, set[str]] = {}


def tree_files_set(ref: str) -> set[str]:
    """Top-level entries of interest present in ``ref`` (directory or file names)."""
    if ref not in _TREE_CACHE:
        found: set[str] = set()
        for path in tree_files(ref):
            if path == REDOCLY_CONFIG:
                found.add(REDOCLY_CONFIG)
            elif path.startswith(OPENAPI_DIR + "/"):
                found.add(OPENAPI_DIR)
        _TREE_CACHE[ref] = found
    return _TREE_CACHE[ref]


def is_spec(path: str) -> bool:
    """True for ``07-api/contracts/openapi/<name>.yaml`` (no subdirectories)."""
    prefix = OPENAPI_DIR + "/"
    return path.startswith(prefix) and path.endswith(".yaml") and "/" not in path[len(prefix):]


def normalize_ref(ref: str, root: str) -> str:
    ref = ref.replace("\\", "/")
    root = root.replace("\\", "/").rstrip("/") + "/"
    if ref.startswith(root):
        ref = ref[len(root):]
    return ref


def lint(root: str, spec: str, npx: str) -> tuple[Counter, int, str | None]:
    """Lint ``spec`` (relative to ``root``). Returns (error keys, warning count, tool failure)."""
    env = dict(os.environ, REDOCLY_TELEMETRY="off", CI="true")
    config = os.path.join(root, REDOCLY_CONFIG)
    cmd = [npx, "--yes", REDOCLY_PACKAGE, "lint", "--format=json"]
    if os.path.exists(config):
        cmd += ["--config", REDOCLY_CONFIG]
    cmd.append(spec)
    proc = subprocess.run(cmd, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    out = proc.stdout.decode("utf-8", "replace")
    try:
        data = json.loads(out[out.index("{"):])
    except ValueError:
        tail = (proc.stderr.decode("utf-8", "replace") or out).strip()[-600:]
        return Counter(), 0, f"redocly produced no parsable output (exit {proc.returncode}): {tail}"
    errors: Counter = Counter()
    warnings = 0
    for problem in data.get("problems", []):
        if problem.get("severity") != "error":
            warnings += 1
            continue
        location = (problem.get("location") or [{}])[0]
        source = normalize_ref((location.get("source") or {}).get("ref", spec), root)
        errors[(problem.get("ruleId", "?"), source, location.get("pointer", ""), problem.get("message", ""))] += 1
    return errors, warnings, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    args = parser.parse_args()

    report = Reporter("OpenAPI lint")
    base_commit = merge_base(args.base, args.head)
    changes = changed_files(base_commit, args.head)
    touched = [c for c in changes if c.status != "D" and is_spec(c.path)]
    config_changed = any(c.path == REDOCLY_CONFIG for c in changes)
    shared_changed = any(c.path == f"{OPENAPI_DIR}/_shared.yaml" for c in touched)

    if not touched and not config_changed:
        report.info("No OpenAPI contract or redocly.yaml changes in this PR; nothing to lint.")
        return report.finish("skipped")

    head_files = sorted(p for p in tree_files(args.head) if is_spec(p))
    if shared_changed or config_changed:
        specs = head_files
        report.info("_shared.yaml or redocly.yaml changed: linting every OpenAPI spec.")
    else:
        specs = sorted(c.path for c in touched)

    npx = shutil.which("npx")
    if not npx:
        report.error("npx not found: Node.js is required to run Redocly.")
        return report.finish("")

    renamed_from = {c.path: c.old_path for c in touched if c.status == "R"}
    base_exists = set(tree_files(base_commit))
    workdir = tempfile.mkdtemp(prefix="docs-ci-openapi-")
    try:
        head_root = os.path.join(workdir, "head")
        base_root = os.path.join(workdir, "base")
        os.makedirs(head_root)
        os.makedirs(base_root)
        export_tree(args.head, head_root)
        if tree_files_set(base_commit):
            export_tree(base_commit, base_root)

        total_new = 0
        total_warnings = 0
        for spec in specs:
            head_errors, warnings, failure = lint(head_root, spec, npx)
            total_warnings += warnings
            if failure:
                report.error(f"Could not lint {spec}: {failure}", spec)
                continue
            base_spec = renamed_from.get(spec, spec)
            base_errors: Counter = Counter()
            if base_spec in base_exists:
                base_errors, _, base_failure = lint(base_root, base_spec, npx)
                if base_failure:
                    report.warning(f"Could not lint the base version of {spec}; every error counts as new.", spec)
                    base_errors = Counter()
                elif base_spec != spec:  # renamed: align file names in the keys
                    base_errors = Counter({(r, s.replace(base_spec, spec), p, m): n for (r, s, p, m), n in base_errors.items()})
            new_errors = head_errors - base_errors
            existing = sum(head_errors.values()) - sum(new_errors.values())
            for (rule, source, pointer, message), count in sorted(new_errors.items()):
                total_new += count
                report.error(f"[{rule}] {message} ({source}{pointer}){' x%d' % count if count > 1 else ''}", spec)
            report.info(
                f"{spec}: {sum(head_errors.values())} error(s) "
                f"({existing} already on the base, {sum(new_errors.values())} new), {warnings} warning(s)"
            )
        report.info(f"Total new errors: {total_new}; warnings (not blocking): {total_warnings}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    return report.finish(f"{len(specs)} spec(s) linted, no new errors")


if __name__ == "__main__":
    sys.exit(main())
