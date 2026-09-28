from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .providers import DEFAULT_PROVIDERS, EMAIL_PROVIDERS
from .scanner import check_email_footprints, scan_username

HISTORY_PATH = Path.home() / ".dossier" / "history.json"


def _ensure_history() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]", encoding="utf-8")


def _read_history() -> List[Dict[str, Any]]:
    _ensure_history()
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError:
        return []


def _write_history(data: List[Dict[str, Any]]) -> None:
    _ensure_history()
    HISTORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_history(entry: Dict[str, Any]) -> None:
    history = _read_history()
    history.append(entry)
    _write_history(history)


def print_banner() -> None:
    print("""
    .-.-. .-.-. .-.-. .-.-. .-.-. .-.-.
   /     \\     \\     \\     \\     \\     \
  |  N  |  O  |  R  |  T  |  H  |  /  |
   \\     //     //     //     //     //
    '-'-' '-'-' '-'-' '-'-' '-'-' '-'-'
     //     //     //     //     //     //
    /  N  /  O  /  R  /  D  /  I  /  C  /
   //     //     //     //     //     //
    '-'-' '-'-' '-'-' '-'-' '-'-' '-'-'
    """)

    print("Advanced OSINT & Security Intelligence")
    print("v3.6 · Authorized defensive research")


def print_main_menu() -> None:
    print("\n[S] Settings   [N] Next page   [P] Prev page   [Q] Quit")
    print("\nOperations")
    print("[01] Investigate a target")
    print("[02] Review history")
    print("[03] Reports")
    print("[04] Providers")
    print("[05] Settings")
    print("[06] Diagnostics")
    print("[07] Help")
    print("[08] Shell")
    print("\nIntelligence")
    print("[09] Intelligence feed")
    print("[10] Shared database")
    print("[11] Claims")
    print("[12] Confidence matrix")
    print("[13] Time machine")
    print("[14] Journal")
    print("[15] Explain")
    print("[16] Entity view")
    print("\nAnalysis")
    print("[17] Evidence graph")
    print("[18] Hypotheses")
    print("[19] Review queue")
    print("[20] Query language")
    print("[21] Health report")
    print("[22] Orphans")
    print("[23] Sources")
    print("[24] Exit")
    print("\n[Menu]—[Standard]")


async def handle_investigate() -> None:
    print("\nTarget type: [u] username | [e] email | [w] URL")
    choice = input("dossier> ").strip().lower()
    if choice not in {"u", "e", "w"}:
        print("Unsupported target type.")
        return

    target = input("target> ").strip()
    if not target:
        print("No target provided.")
        return

    if choice == "u":
        results = await scan_username(target, timeout=6.0, concurrency=6)
    elif choice == "e":
        results = await check_email_footprints(target, timeout=6.0, concurrency=5)
    else:
        print("URL-mode is available through the standard HTTP probe path. Use domain/URL target with a future plugin.")
        return

    append_history({"type": choice, "target": target, "results": [r.to_dict() for r in results]})
    for result in results:
        print(f"[{result.status.upper():<12}] {result.provider:<15} {result.url}")
        if result.title:
            print(f"   title: {result.title}")
        if result.note:
            print(f"   note: {result.note}")


async def handle_history() -> None:
    data = _read_history()
    if not data:
        print("No stored history yet.")
        return
    for item in data[-5:]:
        print(f"[{item.get('type', '?')}] {item.get('target', '')}")


async def handle_providers() -> None:
    print("Username providers:")
    for provider in DEFAULT_PROVIDERS:
        print(f" - {provider.name}: {provider.description}")
    print("\nEmail providers:")
    for provider in EMAIL_PROVIDERS:
        print(f" - {provider.name}: {provider.description}")


async def handle_diagnostics() -> None:
    print("Diagnostics: active internal probe engine online")
    print("- HTTP timeout: 6s")
    print("- Max concurrency: 6")
    print("- Output: JSON history + terminal summary")


def handle_help() -> None:
    print("Dossier is a passive OSINT workflow utility.")
    print("Use investigate to query public footprint URLs without authentication.")
    print("Use history to review saved passive checks.")


async def run_interactive_dashboard() -> None:
    print_banner()
    while True:
        print_main_menu()
        selection = input("north@nordic - $ ").strip().lower()
        if selection in {"q", "quit", "24"}:
            print("Session closed.")
            break
        if selection in {"1", "01"}:
            await handle_investigate()
        elif selection in {"2", "02"}:
            await handle_history()
        elif selection in {"4", "04"}:
            await handle_providers()
        elif selection in {"6", "06"}:
            await handle_diagnostics()
        elif selection in {"7", "07"}:
            handle_help()
        elif selection in {"s", "settings", "5", "05"}:
            print("Settings: passive mode enabled, safe defaults, public URL checks only.")
        else:
            print("Command not available in this session.")
