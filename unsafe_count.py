# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Count `unsafe` usage in a uutils/coreutils checkout at a given revision.

For each `.rs` file outside `vendor/` and `target/`, we bucket each line that
contains an `unsafe` keyword form into:

  type buckets — one per syntactic kind:
    blocks  — `unsafe { ... }`
    fn      — `unsafe fn` items
    impl    — `unsafe impl`
    trait   — `unsafe trait`
    extern  — `unsafe extern`
    attr    — `#[unsafe(...)]` attributes (Rust 2024 edition)

  location buckets — one per source area:
    code    — production source
    test    — paths under `tests/` or `fuzz/`

A line contributes to exactly one type bucket and exactly one location bucket.
`total = sum(types) = code + test`.
"""

import argparse
import json
import re
import subprocess
import sys

# Each pattern is anchored on `\bunsafe` and matches the keyword followed by
# its expected punctuation/keyword. Order matters — more specific matches
# (`fn`, `impl`, ...) before the catch-all `{`.
TYPE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("attr", re.compile(r"#\[unsafe\(")),
    ("fn", re.compile(r"\bunsafe\s+fn\b")),
    ("impl", re.compile(r"\bunsafe\s+impl\b")),
    ("trait", re.compile(r"\bunsafe\s+trait\b")),
    ("extern", re.compile(r"\bunsafe\s+extern\b")),
    ("blocks", re.compile(r"\bunsafe\s*\{")),
]
TYPES = [name for name, _ in TYPE_PATTERNS]


def git(repo: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", repo, *args], text=True)


def is_test_path(path: str) -> bool:
    parts = path.split("/")
    return "tests" in parts or "fuzz" in parts


def count_at(repo: str, sha: str) -> dict[str, int]:
    counts = {t: 0 for t in TYPES}
    counts["code"] = 0
    counts["test"] = 0

    files = git(repo, "ls-tree", "-r", "--name-only", sha).splitlines()
    rs_files = [
        f
        for f in files
        if f.endswith(".rs")
        and not f.startswith("vendor/")
        and "/vendor/" not in f
        and not f.startswith("target/")
        and "/target/" not in f
    ]
    if not rs_files:
        return counts

    for path in rs_files:
        location = "test" if is_test_path(path) else "code"
        try:
            blob = git(repo, "show", f"{sha}:{path}")
        except subprocess.CalledProcessError:
            continue
        for line in blob.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for type_name, regex in TYPE_PATTERNS:
                if regex.search(line):
                    counts[type_name] += 1
                    counts[location] += 1
                    break
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="path to a uutils/coreutils git checkout")
    parser.add_argument(
        "--sha",
        default="HEAD",
        help="commit to count at (default: HEAD)",
    )
    parser.add_argument(
        "--date-format",
        default="%ad",
        help="git format string for the JSON key (default: %%ad — RFC2822-ish)",
    )
    args = parser.parse_args()

    sha = git(args.repo, "rev-parse", args.sha).strip()
    date = git(args.repo, "show", "-s", f"--format={args.date_format}", sha).strip()

    counts = count_at(args.repo, sha)
    entry = {
        "sha": sha,
        "total": str(counts["code"] + counts["test"]),
        "code": str(counts["code"]),
        "test": str(counts["test"]),
        **{t: str(counts[t]) for t in TYPES},
    }
    json.dump({date: entry}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
