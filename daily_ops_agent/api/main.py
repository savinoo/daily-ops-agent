from __future__ import annotations

from datetime import date

from fastapi import FastAPI

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
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
