from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


DEFAULT_DB_PATH = Path.home() / ".dossier" / "dossier.sqlite3"


class CaseStore:
    """Small SQLite persistence boundary for local-first investigations."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or DEFAULT_DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    started TEXT NOT NULL,
                    completed TEXT NOT NULL,
                    target TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    profile TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    providers INTEGER NOT NULL,
                    matches INTEGER NOT NULL,
                    modules INTEGER NOT NULL,
                    entities INTEGER NOT NULL,
                    relationships INTEGER NOT NULL,
                    findings INTEGER NOT NULL,
                    manifest TEXT NOT NULL,
                    analysis_json TEXT,
                    categories_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id TEXT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
                    provider TEXT NOT NULL,
                    target TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    http_status INTEGER,
                    title TEXT,
                    note TEXT,
                    payload_json TEXT NOT NULL,
                    collected_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_investigations_target ON investigations(target);
                CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON evidence(investigation_id);
                """
            )

    def save_investigation(self, investigation: Dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO investigations (
                    id, started, completed, target, target_type, profile, duration,
                    providers, matches, modules, entities, relationships, findings,
                    manifest, analysis_json, categories_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    investigation["id"],
                    investigation["started"],
                    investigation["completed"],
                    investigation["target"],
                    investigation["target_type"],
                    investigation["profile"],
                    investigation["duration"],
                    investigation["providers"],
                    investigation["matches"],
                    investigation["modules"],
                    investigation["entities"],
                    investigation["relationships"],
                    investigation["findings"],
                    investigation["manifest"],
                    json.dumps(investigation.get("analysis")),
                    json.dumps(investigation.get("categories", {})),
                ),
            )
            connection.execute(
                "DELETE FROM evidence WHERE investigation_id = ?",
                (investigation["id"],),
            )
            connection.executemany(
                """
                INSERT INTO evidence (
                    investigation_id, provider, target, url, status, http_status,
                    title, note, payload_json, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        investigation["id"],
                        result["provider"],
                        result["target"],
                        result["url"],
                        result["status"],
                        result.get("http_status"),
                        result.get("title"),
                        result.get("note"),
                        json.dumps(result.get("payload", {})),
                        investigation["completed"],
                    )
                    for result in investigation.get("results", [])
                ],
            )

    def list_investigations(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM investigations ORDER BY completed DESC LIMIT ?",
                (max(1, min(limit, 1000)),),
            ).fetchall()
            return [self._row_to_investigation(connection, row) for row in rows]

    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM investigations WHERE id = ?",
                (investigation_id,),
            ).fetchone()
            return self._row_to_investigation(connection, row) if row else None

    def _row_to_investigation(
        self, connection: sqlite3.Connection, row: sqlite3.Row
    ) -> Dict[str, Any]:
        evidence_rows = connection.execute(
            "SELECT * FROM evidence WHERE investigation_id = ? ORDER BY id",
            (row["id"],),
        ).fetchall()
        results = []
        for evidence in evidence_rows:
            results.append(
                {
                    "provider": evidence["provider"],
                    "target": evidence["target"],
                    "url": evidence["url"],
                    "status": evidence["status"],
                    "http_status": evidence["http_status"],
                    "title": evidence["title"],
                    "note": evidence["note"],
                    "payload": json.loads(evidence["payload_json"]),
                }
            )
        return {
            "id": row["id"],
            "started": row["started"],
            "completed": row["completed"],
            "target": row["target"],
            "target_type": row["target_type"],
            "profile": row["profile"],
            "duration": row["duration"],
            "providers": row["providers"],
            "matches": row["matches"],
            "modules": row["modules"],
            "entities": row["entities"],
            "relationships": row["relationships"],
            "findings": row["findings"],
            "manifest": row["manifest"],
            "analysis": json.loads(row["analysis_json"]) if row["analysis_json"] else None,
            "categories": json.loads(row["categories_json"]),
            "results": results,
        }

