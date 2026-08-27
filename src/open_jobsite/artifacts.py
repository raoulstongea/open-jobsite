"""Draft auditable job artifacts without performing external actions."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from open_jobsite.store import utc_now, validate_project_id


MONEY = Decimal("0.01")


def _decimal(value: Any, field: str, *, allow_negative: bool = False) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a valid number") from exc
    if not number.is_finite():
        raise ValueError(f"{field} must be finite")
    if not allow_negative and number < 0:
        raise ValueError(f"{field} cannot be negative")
    return number


def _money(value: Decimal) -> str:
    return format(value.quantize(MONEY), "f")


def _strings(values: list[Any], field: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list")
    cleaned: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field}[{index}] must be a non-empty string")
        cleaned.append(value.strip())
    return cleaned


def _base(
    artifact_type: str,
    project_id: str,
    evidence_ids: list[Any],
    assumptions: list[Any],
    exclusions: list[Any],
) -> dict[str, Any]:
    validate_project_id(project_id)
    return {
        "schema_version": "0.1",
        "artifact_id": f"draft-{artifact_type}-{uuid4().hex[:12]}",
        "artifact_type": artifact_type,
        "project_id": project_id,
        "status": "draft",
        "created_at": utc_now(),
        "evidence_ids": _strings(evidence_ids, "evidence_ids"),
        "assumptions": _strings(assumptions, "assumptions"),
        "exclusions": _strings(exclusions, "exclusions"),
        "requires_human_approval": True,
        "allowed_next_actions": ["review", "edit", "approve", "reject"],
        "external_action_performed": False,
    }


def draft_daily_log(
    project_id: str,
    work_date: str,
    summary: str,
    workers: list[dict[str, Any]],
    evidence_ids: list[Any],
    assumptions: list[Any] | None = None,
    exclusions: list[Any] | None = None,
) -> dict[str, Any]:
    """Create a reviewable daily log with auditable labor math."""
    try:
        date.fromisoformat(work_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("work_date must use YYYY-MM-DD") from exc
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary cannot be empty")
    if not isinstance(workers, list):
        raise ValueError("workers must be a list")
    clean_workers: list[dict[str, str]] = []
    total_hours = Decimal("0")
    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            raise ValueError(f"workers[{index}] must be an object")
        role = str(worker.get("role", "")).strip()
        identifier = str(worker.get("identifier", "")).strip()
        if not role or not identifier:
            raise ValueError(f"workers[{index}] requires identifier and role")
        hours = _decimal(worker.get("hours"), f"workers[{index}].hours")
        total_hours += hours
        clean_workers.append(
            {"identifier": identifier, "role": role, "hours": _money(hours)}
        )
    artifact = _base(
        "daily-log",
        project_id,
        evidence_ids,
        assumptions or [],
        exclusions or [],
    )
    artifact.update(
        {
            "work_date": work_date,
            "summary": summary.strip(),
            "workers": clean_workers,
            "total_labor_hours": _money(total_hours),
        }
    )
    return artifact


def _price_lines(line_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Decimal]:
    if not isinstance(line_items, list) or not line_items:
        raise ValueError("line_items must be a non-empty list")
    clean_items: list[dict[str, Any]] = []
    subtotal = Decimal("0")
    for index, item in enumerate(line_items):
        if not isinstance(item, dict):
            raise ValueError(f"line_items[{index}] must be an object")
        description = str(item.get("description", "")).strip()
        unit = str(item.get("unit", "")).strip()
        if not description or not unit:
            raise ValueError(f"line_items[{index}] requires description and unit")
        quantity = _decimal(item.get("quantity"), f"line_items[{index}].quantity")
        unit_cost = _decimal(item.get("unit_cost"), f"line_items[{index}].unit_cost")
        amount = quantity * unit_cost
        subtotal += amount
        evidence_ids = item.get("evidence_ids", [])
        clean_items.append(
            {
                "description": description,
                "quantity": str(quantity),
                "unit": unit,
                "unit_cost": _money(unit_cost),
                "amount": _money(amount),
                "evidence_ids": _strings(
                    evidence_ids, f"line_items[{index}].evidence_ids"
                ),
                "unit_math": f"{quantity} {unit} × {_money(unit_cost)}",
            }
        )
    return clean_items, subtotal


def draft_estimate(
    project_id: str,
    title: str,
    line_items: list[dict[str, Any]],
    evidence_ids: list[Any],
    assumptions: list[Any],
    exclusions: list[Any],
    contingency_percent: Any = 0,
    tax_percent: Any = 0,
    currency: str = "CAD",
) -> dict[str, Any]:
    """Create a draft estimate that exposes unit math and approval boundaries."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title cannot be empty")
    contingency_rate = _decimal(contingency_percent, "contingency_percent")
    tax_rate = _decimal(tax_percent, "tax_percent")
    clean_items, subtotal = _price_lines(line_items)
    contingency = subtotal * contingency_rate / Decimal("100")
    pretax = subtotal + contingency
    tax = pretax * tax_rate / Decimal("100")
    total = pretax + tax
    artifact = _base(
        "estimate", project_id, evidence_ids, assumptions, exclusions
    )
    artifact.update(
        {
            "title": title.strip(),
            "currency": currency.strip().upper() or "CAD",
            "line_items": clean_items,
            "totals": {
                "subtotal": _money(subtotal),
                "contingency_percent": str(contingency_rate),
                "contingency": _money(contingency),
                "tax_percent": str(tax_rate),
                "tax": _money(tax),
                "total": _money(total),
            },
            "approval_warning": "Review scope, evidence, quantities, prices, tax, and exclusions before sharing or accepting this estimate.",
        }
    )
    return artifact


def draft_change_order(
    project_id: str,
    title: str,
    reason: str,
    line_items: list[dict[str, Any]],
    evidence_ids: list[Any],
    assumptions: list[Any],
    exclusions: list[Any],
    schedule_impact_days: Any = 0,
    currency: str = "CAD",
) -> dict[str, Any]:
    """Create a draft change order; never send or approve it."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title cannot be empty")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason cannot be empty")
    clean_items, subtotal = _price_lines(line_items)
    schedule_days = _decimal(
        schedule_impact_days, "schedule_impact_days", allow_negative=True
    )
    artifact = _base(
        "change-order", project_id, evidence_ids, assumptions, exclusions
    )
    artifact.update(
        {
            "title": title.strip(),
            "reason": reason.strip(),
            "currency": currency.strip().upper() or "CAD",
            "line_items": clean_items,
            "total_change": _money(subtotal),
            "schedule_impact_days": str(schedule_days),
            "approval_warning": "This is a draft only. Confirm contract terms, scope, price, schedule impact, and signatures before issue.",
        }
    )
    return artifact
