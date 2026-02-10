from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
from daily_ops_agent.domain.dashboard import asdict_baseline, asdict_metrics, compute_alerts, compute_baseline
from daily_ops_agent.domain.memory import add_decision, list_memory
from daily_ops_agent.domain.metrics_store import list_metrics, upsert_from_payload
from daily_ops_agent.domain.mock_scenarios import generate_series, list_scenarios
from daily_ops_agent.domain.pages import list_page_hashes, record_page_hash
from daily_ops_agent.infra.settings import settings
from daily_ops_agent.orchestration.pipeline import fetch_yesterday_and_baseline

UI_VERSION = "v4"

app = FastAPI(title="Daily Ops Agent", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "ui_version": UI_VERSION})


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/brief/daily")
def daily_brief() -> dict:
    """Mock-mode daily brief (always available)."""
    today = date.today()
    y, b = fetch_yesterday_and_baseline(today)
    alerts = compare(y, b)
    return {
        "date": y.day.isoformat(),
        "brief_markdown": render_brief(y, b, alerts),
        "alerts": [a.__dict__ for a in alerts],
    }


@app.post("/metrics")
def metrics_upsert(payload: dict) -> dict:
    day = str(payload.get("day", "")).strip()
    if not day:
        return {"ok": False, "error": "day is required (YYYY-MM-DD)"}

    upsert_from_payload(day=day, payload=payload)
    return {"ok": True}


@app.get("/metrics")
def metrics_list(days: int = 30) -> dict:
    items = list_metrics(days=days)
    return {"items": [asdict_metrics(m) for m in items]}


@app.get("/dashboard")
def dashboard(days: int = 30, baseline_days: int = 7) -> dict:
    items = list_metrics(days=days)
    if not items:
        return {"items": [], "baseline": None, "alerts": []}

    curr = items[0]
    baseline = compute_baseline(items[1 : 1 + baseline_days])
    alerts = compute_alerts(curr, baseline)

    return {
        "current": asdict_metrics(curr),
        "baseline": asdict_baseline(baseline),
        "alerts": [a.__dict__ for a in alerts],
        "items": [asdict_metrics(m) for m in items],
    }


@app.get("/mocks")
def mocks_list() -> dict:
    return {"items": list_scenarios()}


@app.post("/mocks/seed")
def mocks_seed(scenario: str = "steady_growth", days: int = 8) -> dict:
    try:
        rows = generate_series(scenario_key=scenario, days=days)
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    for r in rows:
        upsert_from_payload(day=r["day"], payload=r)

    return {"ok": True, "scenario": scenario, "days": days}


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
