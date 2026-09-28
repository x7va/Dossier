from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Provider:
    name: str
    pattern: str
    kind: str = "username"
    description: str = ""


@dataclass
class ScanResult:
    provider: str
    target: str
    url: str
    status: str
    http_status: Optional[int] = None
    title: Optional[str] = None
    note: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "target": self.target,
            "url": self.url,
            "status": self.status,
            "http_status": self.http_status,
            "title": self.title,
            "note": self.note,
            "payload": self.payload,
        }
