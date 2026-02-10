from __future__ import annotations

from datetime import date


def fetch_shopify_metrics(day: date) -> dict:
    # Mock numbers (replace with real adapter later)
    return {
        "revenue": 12500.0,
        "orders": 142,
        "sessions": 9800,
        "top_products": [
            {"sku": "SKU-001", "title": "Product A", "revenue": 4200.0},
            {"sku": "SKU-002", "title": "Product B", "revenue": 2700.0},
        ],
    }
