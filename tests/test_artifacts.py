import pytest

from open_jobsite.artifacts import (
    draft_change_order,
    draft_daily_log,
    draft_estimate,
)


def test_daily_log_sums_labor_and_stays_draft() -> None:
    result = draft_daily_log(
        "demo",
        "2026-08-27",
        "Installed synthetic test wallboard.",
        [
            {"identifier": "worker-a", "role": "installer", "hours": 7.5},
            {"identifier": "worker-b", "role": "helper", "hours": 6},
        ],
        ["ev-123"],
    )
    assert result["total_labor_hours"] == "13.50"
    assert result["status"] == "draft"
    assert result["external_action_performed"] is False


def test_estimate_calculates_transparent_totals() -> None:
    result = draft_estimate(
        "demo",
        "Synthetic repair estimate",
        [
            {
                "description": "Board",
                "quantity": 4,
                "unit": "sheet",
                "unit_cost": 20,
                "evidence_ids": ["ev-123"],
            },
            {
                "description": "Labor",
                "quantity": 3,
                "unit": "hour",
                "unit_cost": 50,
            },
        ],
        ["ev-123"],
        ["Clear access during working hours"],
        ["Painting"],
        contingency_percent=10,
        tax_percent=5,
    )
    assert result["totals"] == {
        "subtotal": "230.00",
        "contingency_percent": "10",
        "contingency": "23.00",
        "tax_percent": "5",
        "tax": "12.65",
        "total": "265.65",
    }
    assert result["line_items"][0]["unit_math"] == "4 sheet × 20.00"
    assert result["requires_human_approval"] is True


def test_change_order_exposes_schedule_impact() -> None:
    result = draft_change_order(
        "demo",
        "Unexpected substrate repair",
        "Damage became visible after demolition.",
        [
            {
                "description": "Repair labor",
                "quantity": 4,
                "unit": "hour",
                "unit_cost": 60,
            }
        ],
        [],
        ["Work can begin after written approval"],
        [],
        schedule_impact_days=1,
    )
    assert result["total_change"] == "240.00"
    assert result["schedule_impact_days"] == "1"
    assert result["status"] == "draft"


def test_empty_estimate_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        draft_estimate("demo", "Empty", [], [], [], [])


def test_invalid_daily_log_date_is_rejected() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        draft_daily_log("demo", "August 27", "Work", [], [])
