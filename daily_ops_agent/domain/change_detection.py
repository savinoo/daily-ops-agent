from __future__ import annotations

import hashlib

import httpx


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_and_hash_url(url: str, timeout_s: float = 10.0) -> str:
    # Some sites block default clients; set a minimal User-Agent.
    headers = {"User-Agent": "daily-ops-agent/0.1 (+https://github.com/savinoo/daily-ops-agent)"}
    with httpx.Client(timeout=timeout_s, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return hash_text(resp.text)
