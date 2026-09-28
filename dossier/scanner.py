from __future__ import annotations

import asyncio
import json
import re
import socket
from html import unescape
from typing import Iterable, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import Provider, ScanResult
from .providers import DEFAULT_PROVIDERS, EMAIL_PROVIDERS


def _normalize_username(raw_username: str) -> str:
    username = raw_username.strip()
    if not username:
        raise ValueError("username must not be empty")
    return username


def _normalize_email(raw_email: str) -> str:
    email = raw_email.strip()
    if not email:
        raise ValueError("email must not be empty")
    if "@" not in email:
        raise ValueError("email must contain an @ symbol")
    return quote(email)


def _format_pattern(provider: Provider, value: str) -> str:
    return provider.pattern.format(username=value, email=value)


def _extract_title(html_text: Optional[str]) -> Optional[str]:
    if not html_text:
        return None
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    title = unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return title or None


def _probe_url(url: str, timeout: float) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    request = Request(url, headers={"User-Agent": "Dossier/0.1 (+https://example.com/dossier)"})
    try:
        with urlopen(request, timeout=timeout) as response:
            html = response.read(4096).decode("utf-8", errors="replace")
            return response.getcode(), _extract_title(html), None
    except HTTPError as error:
        body = error.read(4096).decode("utf-8", errors="replace")
        return error.code, _extract_title(body), f"HTTP {error.code}"
    except (URLError, TimeoutError, ValueError, socket.timeout) as exc:
        return None, None, str(exc)


async def _scan_single(provider: Provider, target: str, timeout: float, semaphore: asyncio.Semaphore) -> ScanResult:
    async with semaphore:
        url = _format_pattern(provider, target)
        http_status, title, note = await asyncio.to_thread(_probe_url, url, timeout)

        if http_status is None:
            status = "unreachable"
        elif 200 <= http_status < 300:
            status = "exists"
        elif http_status == 403:
            status = "forbidden"
        elif http_status == 404:
            status = "not_found"
        elif 300 <= http_status < 400:
            status = "redirect"
        elif 429 == http_status:
            status = "rate_limited"
        else:
            status = "unknown"

        return ScanResult(
            provider=provider.name,
            target=target,
            url=url,
            status=status,
            http_status=http_status,
            title=title,
            note=note,
            payload={"description": provider.description},
        )


async def scan_username(
    usernames: str | Iterable[str],
    *,
    providers: Optional[Iterable[Provider]] = None,
    timeout: float = 8.0,
    concurrency: int = 8,
) -> List[ScanResult]:
    provider_list = list(providers or DEFAULT_PROVIDERS)
    if isinstance(usernames, str):
        targets = [_normalize_username(usernames)]
    else:
        targets = [_normalize_username(item) for item in usernames]

    semaphore = asyncio.Semaphore(concurrency)
    tasks: list[asyncio.Task[ScanResult]] = []
    for target in targets:
        for provider in provider_list:
            tasks.append(asyncio.create_task(_scan_single(provider, target, timeout, semaphore)))

    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda item: (item.target, item.provider))


async def check_email_footprints(
    email: str,
    *,
    providers: Optional[Iterable[Provider]] = None,
    timeout: float = 8.0,
    concurrency: int = 6,
) -> List[ScanResult]:
    provider_list = list(providers or EMAIL_PROVIDERS)
    normalized_email = _normalize_email(email)
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(_scan_single(provider, normalized_email, timeout, semaphore))
        for provider in provider_list
    ]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda item: item.provider)


def _render_json(results: List[ScanResult]) -> str:
    return json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False)


__all__ = [
    "DEFAULT_PROVIDERS",
    "EMAIL_PROVIDERS",
    "scan_username",
    "check_email_footprints",
    "_render_json",
]
