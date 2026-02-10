from __future__ import annotations

from datetime import date

from fastapi import FastAPI

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
from daily_ops_agent.domain.memory import add_decision, list_memory
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
