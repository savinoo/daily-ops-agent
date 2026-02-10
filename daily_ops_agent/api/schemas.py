from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class MetricsUpsertRequest(BaseModel):
    day: str = Field(..., description="YYYY-MM-DD")

    revenue: float = 0
    orders: int = 0
    sessions: int = 0

    meta_spend: float = 0
    meta_revenue: float = 0
    google_spend: float = 0
    google_revenue: float = 0


class StoredDailyMetricsOut(BaseModel):
    day: str
    created_at: str
    revenue: float
    orders: int
    sessions: int
    meta_spend: float
    meta_revenue: float
    google_spend: float
    google_revenue: float


class BaselineOut(BaseModel):
    revenue: float
    orders: float
    sessions: float
    meta_spend: float
    meta_revenue: float
    google_spend: float
    google_revenue: float


class AlertOut(BaseModel):
    key: str
    severity: Literal["low", "med", "high"]
    message: str


class DashboardOut(BaseModel):
    current: Optional[StoredDailyMetricsOut] = None
    baseline: Optional[BaselineOut] = None
    alerts: list[AlertOut] = []
    items: list[StoredDailyMetricsOut] = []


class MocksListItem(BaseModel):
    key: str
    title: str
    description: str


class MocksListOut(BaseModel):
    items: list[MocksListItem]


class OkOut(BaseModel):
    ok: bool
    error: Optional[str] = None


class MocksSeedOut(OkOut):
    scenario: Optional[str] = None
    days: Optional[int] = None
