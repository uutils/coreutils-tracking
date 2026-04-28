# This file is part of the uutils coreutils package.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

"""Walk the uutils/coreutils git history and produce historical unsafe-counts.

Picks one commit per `--step` window (default: month) and writes
`unsafe-result.json` in the same shape as the other *-result.json files.
Run once to seed the data; the daily CI workflow keeps it fresh.
"""

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from unsafe_count import count_at  # noqa: E402  - reuses the per-commit counter


def git(repo: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", repo, *args], text=True)


def parse_iso(iso: str) -> dt.datetime:
    # "2024-06-28 16:15:56 +0200" → aware datetime. fromisoformat doesn't
    # accept the space-separated tz, so reshape it first.
    date_part, time_part, tz = iso.split(" ")
    return dt.datetime.fromisoformat(f"{date_part}T{time_part}{tz}")


def collect(repo: str, branch: str, step_days: int) -> dict[str, dict[str, str]]:
    log = git(
        repo,
        "log",
        branch,
        "--first-parent",
        "--reverse",
        "--format=%H%x09%ai%x09%ad",
    )
    rows = []
    for line in log.splitlines():
        sha, iso, friendly = line.split("\t")
        rows.append((sha, parse_iso(iso), friendly))

    if not rows:
        return {}

    result: dict[str, dict[str, str]] = {}
    last_ts: dt.datetime | None = None
    step = dt.timedelta(days=step_days)

    for sha, ts, friendly in rows:
        if last_ts is not None and ts - last_ts < step:
            continue
        last_ts = ts
        try:
            counts = count_at(repo, sha)
        except subprocess.CalledProcessError as exc:
            print(f"skip {sha[:10]} ({ts.date()}): {exc}", file=sys.stderr)
            continue
        total = sum(counts.values())
        result[friendly] = {
            "sha": sha,
            "total": str(total),
            **{k: str(v) for k, v in counts.items()},
        }
        print(f"{ts.date()} {sha[:10]} total={total}", file=sys.stderr)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="path to a uutils/coreutils git checkout")
    parser.add_argument("--branch", default="main")
    parser.add_argument(
        "--step-days",
        type=int,
        default=30,
        help="minimum spacing between sampled commits (default: 30 days)",
    )
    parser.add_argument(
        "--out",
        default="unsafe-result.json",
        help="output JSON path (default: unsafe-result.json)",
    )
    args = parser.parse_args()

    data = collect(args.repo, args.branch, args.step_days)
    Path(args.out).write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {len(data)} entries to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
