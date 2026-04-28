# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Count `unsafe` usage in a uutils/coreutils checkout at a given revision.

Categories counted (one match per source line):
  blocks  — `unsafe { ... }` blocks
  fn      — `unsafe fn` items
  impl    — `unsafe impl` items
  trait   — `unsafe trait` items
  extern  — `unsafe extern` items
  attr    — `#[unsafe(...)]` attributes (Rust 2024 edition)

Vendored and build directories are excluded so historical numbers stay
comparable across the repository's evolution.
"""

import argparse
import json
import re
import subprocess
import sys

EXCLUDES = (
    ":!vendor/**",
    ":!target/**",
    ":!**/target/**",
)

# Each pattern is anchored on `\bunsafe` and matches the keyword followed by
# its expected punctuation/keyword. We count one hit per line, which matches
# how the source is normally formatted.
PATTERNS = {
    "blocks": r"\bunsafe\s*\{",
    "fn": r"\bunsafe\s+fn\b",
    "impl": r"\bunsafe\s+impl\b",
    "trait": r"\bunsafe\s+trait\b",
    "extern": r"\bunsafe\s+extern\b",
    "attr": r"#\[unsafe\(",
}


def git(repo: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", repo, *args], text=True)


def count_at(repo: str, sha: str) -> dict[str, int]:
    counts = {key: 0 for key in PATTERNS}
    # Pull all .rs files at the given revision once, then grep through them
    # with python regexes so we don't depend on the host's grep flavor and
    # don't shell out per-pattern.
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

    compiled = {key: re.compile(pat) for key, pat in PATTERNS.items()}
    # Fetch file contents in batch via `git show` per file (cheap with packfiles).
    for path in rs_files:
        try:
            blob = git(repo, "show", f"{sha}:{path}")
        except subprocess.CalledProcessError:
            continue
        for line in blob.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for key, regex in compiled.items():
                if regex.search(line):
                    counts[key] += 1
                    break  # one category per line
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
    total = sum(counts.values())

    entry = {
        "sha": sha,
        "total": str(total),
        **{k: str(v) for k, v in counts.items()},
    }
    json.dump({date: entry}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
