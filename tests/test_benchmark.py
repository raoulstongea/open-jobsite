import json
from pathlib import Path

from open_jobsite.calculations import (
    calculate_concrete_volume,
    calculate_linear_pieces,
    calculate_sheet_count,
    calculate_surface_area,
)


CALCULATORS = {
    "calculate_surface_area": calculate_surface_area,
    "calculate_concrete_volume": calculate_concrete_volume,
    "calculate_sheet_count": calculate_sheet_count,
    "calculate_linear_pieces": calculate_linear_pieces,
}


def test_synthetic_quantity_benchmark() -> None:
    benchmark_path = Path(__file__).parents[1] / "benchmark" / "cases.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    quantity_cases = [case for case in benchmark["cases"] if case["tool"] in CALCULATORS]
    assert len(quantity_cases) >= 4
    for case in quantity_cases:
        result = CALCULATORS[case["tool"]](**case["arguments"])
        assert result["result"] == case["expected"], case["case_id"]
        assert result["requires_human_approval"] is True, case["case_id"]
