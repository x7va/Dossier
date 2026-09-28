from __future__ import annotations

import json
import re
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from .providers import DEFAULT_PROVIDERS
from .scanner import check_email_footprints, scan_username
from .storage import CaseStore


HISTORY_PATH = Path.home() / ".dossier" / "investigations.json"
CASE_STORE = CaseStore()
DISPOSABLE_DOMAINS = {"mailinator.com", "10minutemail.com", "guerrillamail.com", "tempmail.com"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_history() -> List[Dict[str, Any]]:
    stored = CASE_STORE.list_investigations()
    if stored:
        return stored
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def _save_investigation(investigation: Dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = _load_history()
    history.append(investigation)
    HISTORY_PATH.write_text(json.dumps(history[-100:], indent=2), encoding="utf-8")


def _email_analysis(email: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    local, _, domain = email.partition("@")
    domain = domain.lower()
    valid_format = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))
    domain_resolves = False
    website_exists = False
    if domain:
        try:
            import socket

            socket.getaddrinfo(domain, 443)
            domain_resolves = True
        except (OSError, ValueError):
            domain_resolves = False
        try:
            request = Request(f"https://{domain}", method="HEAD", headers={"User-Agent": "Dossier/0.1"})
            with urlopen(request, timeout=3):
                website_exists = True
        except Exception:
            website_exists = False

    score = 0
    if valid_format:
        score += 1
    if domain_resolves:
        score += 1
    if website_exists:
        score += 1
    if domain in DISPOSABLE_DOMAINS:
        score += 4
    risk = "HIGH" if score >= 5 else "MEDIUM" if score >= 3 else "LOW"
    registered_accounts = [item for item in results if item["status"] == "exists"]
    return {
        "risk_score": score,
        "risk_label": f"{risk} RISK",
        "deliverable": valid_format and domain_resolves,
        "valid_format": valid_format,
        "full_inbox": None,
        "randomness": round(min(9.99, len(local) / 3.0), 2),
        "domain": domain,
        "registered": domain_resolves,
        "disposable": domain in DISPOSABLE_DOMAINS,
        "free_provider": domain in {"gmail.com", "outlook.com", "yahoo.com", "proton.me"},
        "custom_domain": domain not in {"gmail.com", "outlook.com", "yahoo.com", "proton.me"},
        "valid_mx": domain_resolves,
        "suspicious_tld": domain.rsplit(".", 1)[-1] in {"zip", "click", "top", "xyz"},
        "website_exists": website_exists,
        "dmarc": "Unknown (passive check)",
        "spf": "Unknown (passive check)",
        "registered_accounts": registered_accounts,
    }


def _investigate(target: str, target_type: str) -> Dict[str, Any]:
    started = _utc_now()
    if target_type == "email":
        results = __import__("asyncio").run(check_email_footprints(target, timeout=5, concurrency=4))
        serialised = [item.to_dict() for item in results]
        analysis = _email_analysis(target, serialised)
        categories = {"Social Media": (1 if analysis["registered_accounts"] else 0, 7), "Business": (0, 4), "Email Service": (0, 1), "Entertainment": (0, 7), "Gaming": (0, 5), "Science And Education": (0, 6), "Technology": (0, 7)}
        findings = len(serialised) + len(analysis)
        entity_count = 1 + len(analysis["registered_accounts"])
    else:
        results = __import__("asyncio").run(scan_username(target, timeout=5, concurrency=6))
        serialised = [item.to_dict() for item in results]
        analysis = None
        categories = {"Social Media": (sum(r["status"] == "exists" for r in serialised), len(serialised)), "Business": (0, 4), "Email Service": (0, 1), "Entertainment": (0, 7), "Gaming": (0, 5), "Science And Education": (0, 6), "Technology": (0, 7)}
        findings = len(serialised)
        entity_count = 1

    investigation = {
        "id": str(uuid.uuid4()),
        "started": started,
        "completed": _utc_now(),
        "target": target,
        "target_type": target_type,
        "profile": "standard",
        "duration": "passive",
        "providers": len(serialised),
        "matches": sum(item["status"] == "exists" for item in serialised),
        "modules": len(serialised) + 21,
        "entities": entity_count,
        "relationships": 0,
        "findings": findings,
        "manifest": uuid.uuid4().hex[:12],
        "results": serialised,
        "analysis": analysis,
        "categories": categories,
    }
    CASE_STORE.save_investigation(investigation)
    _save_investigation(investigation)
    return investigation


class DossierHandler(BaseHTTPRequestHandler):
    def _json(self, payload: Any, status: int = 200) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/history":
            self._json(_load_history())
            return
        if parsed.path.startswith("/api/investigations/"):
            investigation_id = parsed.path.rsplit("/", 1)[-1]
            investigation = CASE_STORE.get_investigation(investigation_id)
            if investigation is None:
                self._json({"error": "investigation not found"}, 404)
                return
            self._json(investigation)
            return
        if parsed.path == "/api/providers":
            self._json([provider.__dict__ for provider in DEFAULT_PROVIDERS])
            return
        if parsed.path == "/api/investigate":
            params = parse_qs(parsed.query)
            target = params.get("target", [""])[0].strip()
            target_type = params.get("type", ["email"])[0]
            if not target or target_type not in {"email", "username"}:
                self._json({"error": "target and a valid type are required"}, 400)
                return
            try:
                self._json(_investigate(target, target_type))
            except ValueError as exc:
                self._json({"error": str(exc)}, 400)
            return
        if parsed.path in {"/", "/index.html"}:
            body = (Path(__file__).parent / "dashboard.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._json({"error": "not found"}, 404)

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), DossierHandler)
    print(f"Dossier dashboard running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
