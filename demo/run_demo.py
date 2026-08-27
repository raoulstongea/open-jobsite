"""Preflight the Berd demo through the real Open Jobsite STDIO process."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


async def _call(
    client: Client[Any], name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    result = await client.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError(f"{name} failed: {result.content}")
    if result.structured_content is None:
        raise RuntimeError(f"{name} returned no structured content")
    return dict(result.structured_content)


async def run_demo(data_dir: Path, project_id: str) -> dict[str, Any]:
    uv = os.environ.get("OPEN_JOBSITE_UV") or shutil.which("uv")
    if not uv:
        raise RuntimeError("uv was not found on PATH")

    environment = os.environ.copy()
    environment["OPEN_JOBSITE_DATA_DIR"] = str(data_dir)
    server = StdioServerParameters(
        command=uv,
        args=[
            "run",
            "--directory",
            str(REPOSITORY_ROOT),
            "open-jobsite",
        ],
        env=environment,
        cwd=REPOSITORY_ROOT,
    )

    async with Client(server, read_timeout_seconds=30) as client:
        tools_result = await client.list_tools()
        tool_names = {tool.name for tool in tools_result.tools}
        required_tools = {
            "create_project",
            "record_site_evidence",
            "calculate_surface_area",
            "calculate_sheet_count",
            "draft_estimate",
            "draft_daily_log",
            "get_project",
        }
        missing = required_tools - tool_names
        if missing:
            raise RuntimeError(f"missing demo tools: {', '.join(sorted(missing))}")

        await _call(
            client,
            "create_project",
            {
                "project_id": project_id,
                "name": "Synthetic training wall repair",
                "description": "Public Berd demonstration using synthetic data only.",
            },
        )
        measurement = await _call(
            client,
            "record_site_evidence",
            {
                "project_id": project_id,
                "evidence_type": "measurement",
                "source_reference": "synthetic field card 01",
                "content": (
                    "The training wall measures 12 feet long by 9 feet high. "
                    "It has no openings."
                ),
                "publication_status": "synthetic",
            },
        )
        site_note = await _call(
            client,
            "record_site_evidence",
            {
                "project_id": project_id,
                "evidence_type": "note",
                "source_reference": "synthetic daily note 01",
                "content": (
                    "Two maintenance technicians each spent 3 hours isolating "
                    "the work area, removing damaged wallboard, and inspecting "
                    "the open cavity. No electrical work or mold treatment was done."
                ),
                "publication_status": "synthetic",
            },
        )

        area = await _call(
            client,
            "calculate_surface_area",
            {"length_ft": 12, "width_ft": 9, "waste_percent": 0},
        )
        sheets = await _call(
            client,
            "calculate_sheet_count",
            {
                "area_sq_ft": 108,
                "sheet_length_ft": 8,
                "sheet_width_ft": 4,
                "waste_percent": 10,
            },
        )

        evidence_ids = [measurement["evidence_id"], site_note["evidence_id"]]
        assumptions = [
            "Clear access during normal working hours",
            "Full sheets are available",
        ]
        exclusions = [
            "Painting",
            "Electrical work",
            "Mold treatment",
            "Permits",
            "Hidden-condition repairs",
        ]
        estimate = await _call(
            client,
            "draft_estimate",
            {
                "project_id": project_id,
                "title": "Synthetic training wall repair",
                "line_items": [
                    {
                        "description": "Wallboard",
                        "quantity": 4,
                        "unit": "sheet",
                        "unit_cost": 18.50,
                        "evidence_ids": [measurement["evidence_id"]],
                    },
                    {
                        "description": "Maintenance labor",
                        "quantity": 6,
                        "unit": "hour",
                        "unit_cost": 45.00,
                        "evidence_ids": [site_note["evidence_id"]],
                    },
                ],
                "evidence_ids": evidence_ids,
                "assumptions": assumptions,
                "exclusions": exclusions,
                "contingency_percent": 10,
                "tax_percent": 0,
                "currency": "CAD",
            },
        )
        daily_log = await _call(
            client,
            "draft_daily_log",
            {
                "project_id": project_id,
                "work_date": "2026-08-27",
                "summary": (
                    "Isolated the work area, removed damaged wallboard, and "
                    "inspected the open cavity."
                ),
                "workers": [
                    {
                        "identifier": "tech-01",
                        "role": "maintenance technician",
                        "hours": 3,
                    },
                    {
                        "identifier": "tech-02",
                        "role": "maintenance technician",
                        "hours": 3,
                    },
                ],
                "evidence_ids": [site_note["evidence_id"]],
                "assumptions": assumptions,
                "exclusions": exclusions,
            },
        )
        project = await _call(client, "get_project", {"project_id": project_id})

    summary = {
        "transport": "stdio",
        "available_tool_count": len(tool_names),
        "project_id": project_id,
        "evidence_count": len(project["evidence"]),
        "artifact_count": len(project["artifacts"]),
        "area_square_feet": area["result"]["value"],
        "sheet_count": sheets["result"]["value"],
        "estimate_subtotal_cad": estimate["totals"]["subtotal"],
        "estimate_total_cad": estimate["totals"]["total"],
        "daily_log_hours": daily_log["total_labor_hours"],
        "requires_human_approval": estimate["requires_human_approval"],
        "external_action_performed": estimate["external_action_performed"],
    }

    expected = {
        "available_tool_count": 10,
        "evidence_count": 2,
        "artifact_count": 2,
        "area_square_feet": "108.00",
        "sheet_count": "4",
        "estimate_subtotal_cad": "344.00",
        "estimate_total_cad": "378.40",
        "daily_log_hours": "6.00",
        "requires_human_approval": True,
        "external_action_performed": False,
    }
    for field, value in expected.items():
        if summary[field] != value:
            raise AssertionError(
                f"unexpected {field}: {summary[field]!r}; expected {value!r}"
            )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-id",
        default="berd-demo-preflight",
        help="Unique lowercase project identifier for a persistent data folder.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Keep output in this folder. By default the preflight uses a temporary folder.",
    )
    args = parser.parse_args()

    if args.data_dir:
        args.data_dir.mkdir(parents=True, exist_ok=True)
        summary = asyncio.run(run_demo(args.data_dir, args.project_id))
    else:
        with tempfile.TemporaryDirectory(prefix="open-jobsite-berd-demo-") as folder:
            summary = asyncio.run(run_demo(Path(folder), args.project_id))

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
