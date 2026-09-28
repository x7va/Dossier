from __future__ import annotations

import argparse
import asyncio
from typing import List, Optional

from .scanner import _render_json, check_email_footprints, scan_username
from .tui import run_interactive_dashboard
from .web import serve


def _read_targets(path: Optional[str]) -> List[str]:
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def _print_results(results, *, json_output: bool = False) -> None:
    if json_output:
        print(_render_json(results))
        return

    if not results:
        print("No results found.")
        return

    for result in results:
        label = f"[{result.status.upper()}]"
        print(f"{label:<14} {result.provider:<15} {result.url}")
        if result.title:
            print(f"   title: {result.title}")
        if result.note:
            print(f"   note: {result.note}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dossier: async OSINT username and email reconnaissance")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Run a scan against a username or email")
    scan_subparsers = scan_parser.add_subparsers(dest="scan_target", required=True)

    username_parser = scan_subparsers.add_parser("username", help="Check username footprint across known public profiles")
    username_parser.add_argument("targets", nargs="*", help="Username(s) to investigate")
    username_parser.add_argument("--input-file", type=str, help="Optional file containing one username per line")
    username_parser.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout per request in seconds")
    username_parser.add_argument("--concurrency", type=int, default=8, help="Maximum concurrent probes")
    username_parser.add_argument("--json", action="store_true", help="Emit raw JSON output")

    email_parser = scan_subparsers.add_parser("email", help="Check email footprint across public search-style URLs")
    email_parser.add_argument("target", nargs="?", help="Email address to investigate")
    email_parser.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout per request in seconds")
    email_parser.add_argument("--concurrency", type=int, default=6, help="Maximum concurrent probes")
    email_parser.add_argument("--json", action="store_true", help="Emit raw JSON output")

    ui_parser = subparsers.add_parser("ui", help="Launch the tactical interactive dashboard")
    ui_parser.add_argument("--history", action="store_true", help="Display the latest saved scan history")
    web_parser = subparsers.add_parser("web", help="Launch the local analyst dashboard")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=8765)

    history_parser = subparsers.add_parser("history", help="Show saved case history")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "scan":
            if args.scan_target == "username":
                targets = list(args.targets or [])
                targets.extend(_read_targets(args.input_file))
                if not targets:
                    parser.error("No username(s) provided or input file was empty")
                results = asyncio.run(scan_username(targets, timeout=args.timeout, concurrency=args.concurrency))
                _print_results(results, json_output=args.json)
                return

            if args.scan_target == "email":
                if not args.target:
                    parser.error("An email address is required")
                results = asyncio.run(check_email_footprints(args.target, timeout=args.timeout, concurrency=args.concurrency))
                _print_results(results, json_output=args.json)
                return

        if args.command == "ui":
            asyncio.run(run_interactive_dashboard())
            return

        if args.command == "web":
            serve(args.host, args.port)
            return

        if args.command == "history":
            from .tui import _read_history
            for item in _read_history()[-10:]:
                print(f"[{item.get('type', '?')}] {item.get('target', '')}")
            return

    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
