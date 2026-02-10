from __future__ import annotations

from datetime import date

from fastapi import FastAPI

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
from daily_ops_agent.domain.memory import add_decision, list_memory
from daily_ops_agent.domain.pages import list_page_hashes, record_page_hash
from daily_ops_agent.infra.settings import settings
from daily_ops_agent.orchestration.pipeline import fetch_yesterday_and_baseline

app = FastAPI(title="Daily Ops Agent", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/brief/daily")
def daily_brief() -> dict:
    today = date.today()
    y, b = fetch_yesterday_and_baseline(today)
    alerts = compare(y, b)
    return {
        "date": y.day.isoformat(),
        "brief_markdown": render_brief(y, b, alerts),
        "alerts": [a.__dict__ for a in alerts],
    }


@app.get("/memory")
def memory(limit: int = 20) -> dict:
    items = list_memory(limit=limit)
    return {"items": [i.__dict__ for i in items]}


@app.post("/memory")
def memory_add(payload: dict) -> dict:
    decision = str(payload.get("decision", "")).strip()
    if not decision:
        return {"ok": False, "error": "decision is required"}

    outcome = payload.get("outcome")
    day = payload.get("day")

    new_id = add_decision(decision=decision, outcome=outcome, day=day)
    return {"ok": True, "id": new_id}


@app.post("/changes/snapshot")
def snapshot_pages() -> dict:
    urls = [u.strip() for u in settings.landing_pages.split(",") if u.strip()]
    results = []
    for url in urls:
        try:
            ph = record_page_hash(url)
            results.append({"ok": True, **ph.__dict__})
        except Exception as e:  # noqa: BLE001
            results.append({"ok": False, "url": url, "error": str(e)})
    return {"results": results}


@app.get("/changes")
def changes(url: str | None = None, limit: int = 50) -> dict:
    items = list_page_hashes(url=url, limit=limit)
    return {"items": [i.__dict__ for i in items]}
