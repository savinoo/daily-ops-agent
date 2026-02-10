from __future__ import annotations

from fastapi.testclient import TestClient

from daily_ops_agent.api.main import app
from daily_ops_agent.infra.settings import settings


def test_brief_uses_sqlite_when_metrics_exist(tmp_path) -> None:
    settings.sqlite_path = str(tmp_path / "t.sqlite")
    client = TestClient(app)

    client.post("/mocks/seed?scenario=steady_growth&days=8")
    r = client.get("/brief/daily")
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "sqlite"
    assert "Daily Ops Brief" in data["brief_markdown"]
