# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Count monthly commits and contributors for GNU and uutils coreutils.

For each project, walk the git history since `--since` and bucket every
non-merge commit by its author month (UTC). We record, per month:

  commits — number of non-merge commits
  authors — distinct authors active that month
  cumulative_authors — distinct authors seen since the project's first
                       commit (not just since `--since`)

Authors are deduplicated by mailmapped email (lowercased); bots
(dependabot, renovate, github-actions, …) are excluded from both counts.

The result is a JSON object keyed by month (`YYYY-MM`), each holding one
entry per project:

  {"2021-01": {"gnu": {"commits": "42", ...}, "uutils": {...}}, ...}
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

BOT_PATTERNS = [
    re.compile(r"\[bot\]"),
    re.compile(r"\bdependabot\b"),
    re.compile(r"\brenovate\b"),
    re.compile(r"github-actions"),
    re.compile(r"^actions@github\.com$"),
]


def is_bot(email: str, name: str) -> bool:
    haystack = f"{email} {name}".lower()
    return any(p.search(haystack) for p in BOT_PATTERNS)


def git(repo: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", repo, *args], text=True)


def month_range(since: str, until: str) -> list[str]:
    """All `YYYY-MM` keys from `since` up to `until` (exclusive)."""
    start = date.fromisoformat(f"{since[:7]}-01")
    # `until` is exclusive, so the last reported month is the one holding the
    # day before it.
    end = date.fromisoformat(until[:10]) - timedelta(days=1)
    months = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return months


def collect(repo: str, since: str, until: str, rev: str) -> dict[str, dict[str, str]]:
    """Per-month commit/author counts for `repo` in [since, until).

    Only the reported months are limited by `since`: the whole history up to
    `until` is walked, so `cumulative_authors` counts every contributor the
    project ever had, not just those since `since`.
    """
    log = git(
        repo,
        "log",
        rev,
        "--no-merges",
        "--use-mailmap",
        f"--until={until}",
        "--date=format-local:%Y-%m",
        "--pretty=format:%ad\x1f%aE\x1f%aN",
    )

    per_month: dict[str, dict] = {}
    for line in log.splitlines():
        if not line.strip():
            continue
        month, email, name = line.split("\x1f")
        if is_bot(email, name):
            continue
        bucket = per_month.setdefault(month, {"commits": 0, "authors": set()})
        bucket["commits"] += 1
        bucket["authors"].add(email.lower())

    result = {}
    seen: set[str] = set()
    reported = set(month_range(since, until))
    # Walk every month the repo has, oldest first, so the cumulative author
    # set carries the pre-`since` history into the first reported month.
    for month in sorted(per_month.keys() | reported):
        bucket = per_month.get(month, {"commits": 0, "authors": set()})
        seen |= bucket["authors"]
        if month not in reported:
            continue
        result[month] = {
            "commits": str(bucket["commits"]),
            "authors": str(len(bucket["authors"])),
            "cumulative_authors": str(len(seen)),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gnu", help="path to a coreutils/coreutils git checkout")
    parser.add_argument("uutils", help="path to a uutils/coreutils git checkout")
    parser.add_argument(
        "--since",
        default="2021-01-01",
        help="first month to report (default: 2021-01-01)",
    )
    parser.add_argument(
        "--until",
        default=None,
        help="exclusive end date (default: the 1st of the current month)",
    )
    parser.add_argument("--gnu-rev", default="HEAD", help="GNU revision to walk")
    parser.add_argument("--uutils-rev", default="HEAD", help="uutils revision to walk")
    args = parser.parse_args()

    # Default to the start of the current month: the running month is always
    # partial, and a half-counted month reads as a collapse in activity.
    if args.until is None:
        today = datetime.now(timezone.utc).date()
        args.until = date(today.year, today.month, 1).isoformat()

    gnu = collect(args.gnu, args.since, args.until, args.gnu_rev)
    uutils = collect(args.uutils, args.since, args.until, args.uutils_rev)

    merged = {
        month: {"gnu": gnu[month], "uutils": uutils[month]} for month in sorted(gnu)
    }
    json.dump(merged, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
