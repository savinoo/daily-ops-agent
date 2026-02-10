from __future__ import annotations

import argparse
from datetime import date

from rich.console import Console

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
from daily_ops_agent.orchestration.pipeline import fetch_yesterday_and_baseline


def cmd_brief(_args: argparse.Namespace) -> int:
    today = date.today()
    y, b = fetch_yesterday_and_baseline(today)
    alerts = compare(y, b)
    brief = render_brief(y, b, alerts)

    Console().print(brief)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dailyops")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("brief", help="Generate daily ops brief")
    b.set_defaults(func=cmd_brief)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
