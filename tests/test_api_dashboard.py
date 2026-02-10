from __future__ import annotations

from fastapi.testclient import TestClient

from daily_ops_agent.api.main import app
from daily_ops_agent.infra.settings import settings


def test_mocks_list() -> None:
    client = TestClient(app)
    r = client.get("/mocks")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    keys = {x["key"] for x in data["items"]}
    assert {"steady_growth", "cr_drop", "ad_spend_spike", "revenue_crash"}.issubset(keys)


def test_seed_then_dashboard_generates_alerts(tmp_path) -> None:
    # isolate sqlite per test
    settings.sqlite_path = str(tmp_path / "t.sqlite")

    client = TestClient(app)
    r = client.post("/mocks/seed?scenario=revenue_crash&days=8")
    assert r.status_code == 200
    assert r.json()["ok"] is True

    dash = client.get("/dashboard?days=30&baseline_days=7")
    assert dash.status_code == 200
    data = dash.json()
    assert data["current"] is not None
    assert len(data["items"]) >= 8
    keys = {a["key"] for a in data["alerts"]}
    # crash scenario should at least drop revenue and/or CR
    assert ("revenue_drop" in keys) or ("cr_drop" in keys)


def test_metrics_validation_day_required(tmp_path) -> None:
    settings.sqlite_path = str(tmp_path / "t.sqlite")
    client = TestClient(app)
    r = client.post("/metrics", json={"revenue": 1})
    # pydantic should 422
    assert r.status_code == 422
