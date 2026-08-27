"""MCP tool surface for Open Jobsite."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from mcp.server import MCPServer

from open_jobsite import __version__
from open_jobsite.artifacts import (
    draft_change_order as make_change_order,
    draft_daily_log as make_daily_log,
    draft_estimate as make_estimate,
)
from open_jobsite.calculations import (
    calculate_concrete_volume as concrete_volume,
    calculate_linear_pieces as linear_pieces,
    calculate_sheet_count as sheet_count,
    calculate_surface_area as surface_area,
)
from open_jobsite.store import JobsiteStore


mcp = MCPServer("Open Jobsite")


def _store() -> JobsiteStore:
    return JobsiteStore()


def _json_list(raw: str, field: str) -> list[Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} must be valid JSON") from exc
    if not isinstance(value, list):
        raise ValueError(f"{field} must contain a JSON array")
    return value


@mcp.tool()
def create_project(project_id: str, name: str, description: str = "") -> dict[str, Any]:
    """Create a new local project. Use a lowercase, non-sensitive project_id."""
    return _store().create_project(project_id, name, description)


@mcp.tool()
def record_site_evidence(
    project_id: str,
    evidence_type: str,
    source_reference: str,
    content: str,
    publication_status: str = "private",
) -> dict[str, Any]:
    """Record a local evidence note and its source; this performs no upload."""
    return _store().record_evidence(
        project_id,
        evidence_type,
        source_reference,
        content,
        publication_status,
    )


@mcp.tool()
def get_project(project_id: str) -> dict[str, Any]:
    """Read the complete local project record."""
    return _store().get_project(project_id)


@mcp.tool()
def calculate_surface_area(
    length_ft: float, width_ft: float, waste_percent: float = 10
) -> dict[str, Any]:
    """Calculate rectangular area in square feet, including a stated waste factor."""
    return surface_area(length_ft, width_ft, waste_percent)


@mcp.tool()
def calculate_concrete_volume(
    length_ft: float,
    width_ft: float,
    depth_in: float,
    waste_percent: float = 5,
) -> dict[str, Any]:
    """Calculate cubic yards for a uniform rectangular pour; not engineering advice."""
    return concrete_volume(length_ft, width_ft, depth_in, waste_percent)


@mcp.tool()
def calculate_sheet_count(
    area_sq_ft: float,
    sheet_length_ft: float = 8,
    sheet_width_ft: float = 4,
    waste_percent: float = 10,
) -> dict[str, Any]:
    """Calculate whole sheet count with explicit sheet dimensions and waste."""
    return sheet_count(area_sq_ft, sheet_length_ft, sheet_width_ft, waste_percent)


@mcp.tool()
def calculate_linear_pieces(
    required_length_ft: float,
    piece_length_ft: float,
    waste_percent: float = 10,
) -> dict[str, Any]:
    """Calculate whole stock pieces for a linear requirement."""
    return linear_pieces(required_length_ft, piece_length_ft, waste_percent)


@mcp.tool()
def draft_daily_log(
    project_id: str,
    work_date: str,
    summary: str,
    workers_json: str = "[]",
    evidence_ids_json: str = "[]",
    assumptions_json: str = "[]",
    exclusions_json: str = "[]",
) -> dict[str, Any]:
    """Create and locally save a draft daily log. JSON arguments must be arrays."""
    artifact = make_daily_log(
        project_id,
        work_date,
        summary,
        _json_list(workers_json, "workers_json"),
        _json_list(evidence_ids_json, "evidence_ids_json"),
        _json_list(assumptions_json, "assumptions_json"),
        _json_list(exclusions_json, "exclusions_json"),
    )
    return _store().save_artifact(project_id, artifact)


@mcp.tool()
def draft_estimate(
    project_id: str,
    title: str,
    line_items_json: str,
    evidence_ids_json: str = "[]",
    assumptions_json: str = "[]",
    exclusions_json: str = "[]",
    contingency_percent: float = 0,
    tax_percent: float = 0,
    currency: str = "CAD",
) -> dict[str, Any]:
    """Create and save an auditable draft estimate; never send or accept it."""
    artifact = make_estimate(
        project_id,
        title,
        _json_list(line_items_json, "line_items_json"),
        _json_list(evidence_ids_json, "evidence_ids_json"),
        _json_list(assumptions_json, "assumptions_json"),
        _json_list(exclusions_json, "exclusions_json"),
        contingency_percent,
        tax_percent,
        currency,
    )
    return _store().save_artifact(project_id, artifact)


@mcp.tool()
def draft_change_order(
    project_id: str,
    title: str,
    reason: str,
    line_items_json: str,
    evidence_ids_json: str = "[]",
    assumptions_json: str = "[]",
    exclusions_json: str = "[]",
    schedule_impact_days: float = 0,
    currency: str = "CAD",
) -> dict[str, Any]:
    """Create and save a draft change order with an explicit approval gate."""
    artifact = make_change_order(
        project_id,
        title,
        reason,
        _json_list(line_items_json, "line_items_json"),
        _json_list(evidence_ids_json, "evidence_ids_json"),
        _json_list(assumptions_json, "assumptions_json"),
        _json_list(exclusions_json, "exclusions_json"),
        schedule_impact_days,
        currency,
    )
    return _store().save_artifact(project_id, artifact)


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="open-jobsite",
        description="Run the Open Jobsite MCP server over stdio.",
    )
    parser.add_argument(
        "--data-dir",
        help="Local project-data directory (defaults to .open-jobsite-data)",
    )
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()
    if args.data_dir:
        os.environ["OPEN_JOBSITE_DATA_DIR"] = args.data_dir
    mcp.run()


if __name__ == "__main__":
    cli()
