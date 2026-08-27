"""Reproducible runner for the five synthetic Open Jobsite benchmark cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from open_jobsite.artifacts import draft_estimate
from open_jobsite.calculations import (
    calculate_concrete_volume,
    calculate_linear_pieces,
    calculate_sheet_count,
    calculate_surface_area,
)


DEFAULT_CASES_PATH = Path(__file__).parents[2] / "benchmark" / "cases.json"
TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "calculate_surface_area": calculate_surface_area,
    "calculate_concrete_volume": calculate_concrete_volume,
    "calculate_sheet_count": calculate_sheet_count,
    "calculate_linear_pieces": calculate_linear_pieces,
    "draft_estimate": draft_estimate,
}


def run_benchmarks(cases_path: Path = DEFAULT_CASES_PATH) -> dict[str, Any]:
    benchmark = json.loads(cases_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    numeric_checks = 0
    numeric_matches = 0
    guardrail_checks = 0
    guardrail_matches = 0

    for case in benchmark["cases"]:
        result = TOOLS[case["tool"]](**case["arguments"])
        checks: dict[str, bool]
        if "expected" in case:
            checks = {"exact_result": result["result"] == case["expected"]}
            numeric_checks += 1
            numeric_matches += int(checks["exact_result"])
        else:
            checks = {
                field: result.get(field) == expected
                for field, expected in case["expected_invariants"].items()
            }
            guardrail_checks += len(checks)
            guardrail_matches += sum(checks.values())
        results.append(
            {
                "case_id": case["case_id"],
                "passed": all(checks.values()),
                "checks": checks,
            }
        )

    passed = sum(item["passed"] for item in results)
    total = len(results)
    return {
        "benchmark_version": benchmark["benchmark_version"],
        "data_policy": benchmark["data_policy"],
        "cases_total": total,
        "cases_passed": passed,
        "pass_rate_percent": round(100 * passed / total, 2),
        "numeric_cases_exact": f"{numeric_matches}/{numeric_checks}",
        "approval_guardrails_exact": f"{guardrail_matches}/{guardrail_checks}",
        "results": results,
    }


def main() -> None:
    report = run_benchmarks()
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["cases_passed"] != report["cases_total"]:
        raise SystemExit(1)
