import pytest

from open_jobsite.calculations import (
    calculate_concrete_volume,
    calculate_linear_pieces,
    calculate_sheet_count,
    calculate_surface_area,
)


def test_surface_area_exposes_math_and_approval_boundary() -> None:
    result = calculate_surface_area(10, 12, 10)
    assert result["result"] == {"value": "132.00", "unit": "square_feet"}
    assert result["intermediate"]["base_square_feet"] == "120.00"
    assert result["requires_human_approval"] is True


def test_concrete_volume_converts_inches_and_cubic_yards() -> None:
    result = calculate_concrete_volume(12, 12, 6, 5)
    assert result["result"] == {"value": "2.80", "unit": "cubic_yards"}
    assert result["intermediate"]["base_cubic_feet"] == "72.00"


def test_sheet_count_rounds_up_to_whole_sheets() -> None:
    result = calculate_sheet_count(100, 8, 4, 10)
    assert result["result"] == {"value": "4", "unit": "sheets"}


def test_linear_piece_count_rounds_up() -> None:
    result = calculate_linear_pieces(100, 8, 10)
    assert result["result"] == {"value": "14", "unit": "pieces"}


@pytest.mark.parametrize(
    ("function", "args"),
    [
        (calculate_surface_area, (0, 12, 10)),
        (calculate_concrete_volume, (12, 12, -1, 5)),
        (calculate_sheet_count, (100, 8, 4, -5)),
        (calculate_linear_pieces, (100, 0, 10)),
    ],
)
def test_invalid_dimensions_are_rejected(function, args) -> None:
    with pytest.raises(ValueError):
        function(*args)


def test_non_finite_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        calculate_surface_area("NaN", 10)
