"""Deterministic construction quantity calculations.

All public functions return JSON-serializable dictionaries. Decimal arithmetic is
used internally so the same inputs produce the same result across MCP clients.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import Any


TWO_PLACES = Decimal("0.01")


def _decimal(value: str | int | float | Decimal, field: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a valid number") from exc
    if not number.is_finite():
        raise ValueError(f"{field} must be finite")
    return number


def _positive(value: str | int | float | Decimal, field: str) -> Decimal:
    number = _decimal(value, field)
    if number <= 0:
        raise ValueError(f"{field} must be greater than zero")
    return number


def _non_negative(value: str | int | float | Decimal, field: str) -> Decimal:
    number = _decimal(value, field)
    if number < 0:
        raise ValueError(f"{field} cannot be negative")
    return number


def _display(value: Decimal, places: Decimal = TWO_PLACES) -> str:
    return format(value.quantize(places), "f")


def _up(value: Decimal, places: Decimal = TWO_PLACES) -> Decimal:
    return value.quantize(places, rounding=ROUND_CEILING)


def _result(
    *,
    calculation: str,
    value: str,
    unit: str,
    formula: str,
    inputs: dict[str, str],
    intermediate: dict[str, str],
    assumptions: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "calculation": calculation,
        "result": {"value": value, "unit": unit},
        "formula": formula,
        "inputs": inputs,
        "intermediate": intermediate,
        "assumptions": assumptions,
        "status": "calculation_only",
        "requires_human_approval": True,
    }


def calculate_surface_area(
    length_ft: str | int | float | Decimal,
    width_ft: str | int | float | Decimal,
    waste_percent: str | int | float | Decimal = 10,
) -> dict[str, Any]:
    """Calculate rectangular surface area with a transparent waste factor."""
    length = _positive(length_ft, "length_ft")
    width = _positive(width_ft, "width_ft")
    waste = _non_negative(waste_percent, "waste_percent")
    base = length * width
    total = _up(base * (Decimal("1") + waste / Decimal("100")))
    return _result(
        calculation="surface_area",
        value=_display(total),
        unit="square_feet",
        formula="length_ft × width_ft × (1 + waste_percent ÷ 100)",
        inputs={
            "length_ft": str(length),
            "width_ft": str(width),
            "waste_percent": str(waste),
        },
        intermediate={"base_square_feet": _display(base)},
        assumptions=["The measured surface is rectangular."],
    )


def calculate_concrete_volume(
    length_ft: str | int | float | Decimal,
    width_ft: str | int | float | Decimal,
    depth_in: str | int | float | Decimal,
    waste_percent: str | int | float | Decimal = 5,
) -> dict[str, Any]:
    """Calculate concrete volume in cubic yards from feet/feet/inches."""
    length = _positive(length_ft, "length_ft")
    width = _positive(width_ft, "width_ft")
    depth = _positive(depth_in, "depth_in")
    waste = _non_negative(waste_percent, "waste_percent")
    cubic_feet = length * width * (depth / Decimal("12"))
    cubic_yards = cubic_feet / Decimal("27")
    total = _up(cubic_yards * (Decimal("1") + waste / Decimal("100")))
    return _result(
        calculation="concrete_volume",
        value=_display(total),
        unit="cubic_yards",
        formula="length_ft × width_ft × (depth_in ÷ 12) ÷ 27 × (1 + waste_percent ÷ 100)",
        inputs={
            "length_ft": str(length),
            "width_ft": str(width),
            "depth_in": str(depth),
            "waste_percent": str(waste),
        },
        intermediate={
            "base_cubic_feet": _display(cubic_feet),
            "base_cubic_yards": _display(cubic_yards),
        },
        assumptions=[
            "The pour has uniform depth.",
            "The result is quantity math, not a structural or mix-design recommendation.",
        ],
    )


def calculate_sheet_count(
    area_sq_ft: str | int | float | Decimal,
    sheet_length_ft: str | int | float | Decimal = 8,
    sheet_width_ft: str | int | float | Decimal = 4,
    waste_percent: str | int | float | Decimal = 10,
) -> dict[str, Any]:
    """Calculate the whole number of sheets needed for a target area."""
    area = _positive(area_sq_ft, "area_sq_ft")
    sheet_length = _positive(sheet_length_ft, "sheet_length_ft")
    sheet_width = _positive(sheet_width_ft, "sheet_width_ft")
    waste = _non_negative(waste_percent, "waste_percent")
    sheet_area = sheet_length * sheet_width
    unrounded = area * (Decimal("1") + waste / Decimal("100")) / sheet_area
    count = unrounded.to_integral_value(rounding=ROUND_CEILING)
    return _result(
        calculation="sheet_count",
        value=str(count),
        unit="sheets",
        formula="ceil(area_sq_ft × (1 + waste_percent ÷ 100) ÷ (sheet_length_ft × sheet_width_ft))",
        inputs={
            "area_sq_ft": str(area),
            "sheet_length_ft": str(sheet_length),
            "sheet_width_ft": str(sheet_width),
            "waste_percent": str(waste),
        },
        intermediate={
            "sheet_area_sq_ft": _display(sheet_area),
            "unrounded_sheet_count": _display(unrounded),
        },
        assumptions=[
            "Full sheet area is usable except for the stated waste factor.",
            "Layout, openings, seams, and orientation still require field review.",
        ],
    )


def calculate_linear_pieces(
    required_length_ft: str | int | float | Decimal,
    piece_length_ft: str | int | float | Decimal,
    waste_percent: str | int | float | Decimal = 10,
) -> dict[str, Any]:
    """Calculate whole stock pieces needed for a required linear length."""
    required = _positive(required_length_ft, "required_length_ft")
    piece = _positive(piece_length_ft, "piece_length_ft")
    waste = _non_negative(waste_percent, "waste_percent")
    unrounded = required * (Decimal("1") + waste / Decimal("100")) / piece
    count = unrounded.to_integral_value(rounding=ROUND_CEILING)
    return _result(
        calculation="linear_pieces",
        value=str(count),
        unit="pieces",
        formula="ceil(required_length_ft × (1 + waste_percent ÷ 100) ÷ piece_length_ft)",
        inputs={
            "required_length_ft": str(required),
            "piece_length_ft": str(piece),
            "waste_percent": str(waste),
        },
        intermediate={"unrounded_piece_count": _display(unrounded)},
        assumptions=["Cut optimization and reusable offcuts are not included."],
    )
