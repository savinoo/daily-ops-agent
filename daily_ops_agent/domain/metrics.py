from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyMetrics:
    day: date

    # Shopify
    revenue: float
    orders: int
    sessions: int

    # Ads
    meta_spend: float
    meta_revenue: float
    google_spend: float
    google_revenue: float

    @property
    def aov(self) -> float:
        return self.revenue / self.orders if self.orders else 0.0

    @property
    def cr(self) -> float:
        return self.orders / self.sessions if self.sessions else 0.0

    @property
    def meta_roas(self) -> float:
        return self.meta_revenue / self.meta_spend if self.meta_spend else 0.0

    @property
    def google_roas(self) -> float:
        return self.google_revenue / self.google_spend if self.google_spend else 0.0
