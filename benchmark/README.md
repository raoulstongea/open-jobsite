# Synthetic benchmark

Open Jobsite v0.1 ships five small, public, synthetic cases. They test four
deterministic quantity calculations and one approval boundary. They do not
measure real-world estimate accuracy, model quality, code compliance, or user
outcomes.

Run the benchmark with:

```bash
uv run python benchmark/run_benchmarks.py
```

## Verified baseline

As of 2026-08-27, the reproducible baseline is:

| Metric | Result |
|---|---:|
| Cases passed | 5 / 5 |
| Exact numeric results | 4 / 4 |
| Approval invariants | 3 / 3 |
| Synthetic-only data policy | Yes |

The approval case checks that every drafted estimate remains `draft`, requires
human approval, and reports that no external action was performed. GitHub
Actions reruns the benchmark on every push and pull request.

This is an intentionally narrow grant-proof baseline. The Q1 target is 25
versioned cases, including invalid inputs, evidence-link failures, and complete
agent workflows. Latency, field accuracy, and human usability are not claimed by
the v0.1 benchmark.
