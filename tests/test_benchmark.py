from open_jobsite.benchmarking import run_benchmarks


def test_all_five_synthetic_benchmarks() -> None:
    report = run_benchmarks()
    assert report["cases_total"] == 5
    assert report["cases_passed"] == 5
    assert report["numeric_cases_exact"] == "4/4"
    assert report["approval_guardrails_exact"] == "3/3"
