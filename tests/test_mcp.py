import json
from pathlib import Path

import pytest
from mcp import Client

from open_jobsite.server import mcp


@pytest.mark.anyio
async def test_mcp_lists_tools_and_runs_evidence_to_estimate_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPEN_JOBSITE_DATA_DIR", str(tmp_path))
    async with Client(mcp) as client:
        tool_result = await client.list_tools()
        names = {tool.name for tool in tool_result.tools}
        assert {
            "create_project",
            "record_site_evidence",
            "calculate_surface_area",
            "draft_estimate",
        }.issubset(names)

        await client.call_tool(
            "create_project",
            {"project_id": "mcp-demo", "name": "Synthetic MCP test"},
        )
        evidence_result = await client.call_tool(
            "record_site_evidence",
            {
                "project_id": "mcp-demo",
                "evidence_type": "measurement",
                "source_reference": "synthetic card A",
                "content": "Wall measures 10 ft by 8 ft.",
                "publication_status": "synthetic",
            },
        )
        evidence = evidence_result.structured_content
        assert evidence is not None
        evidence_id = evidence["evidence_id"]

        estimate_result = await client.call_tool(
            "draft_estimate",
            {
                "project_id": "mcp-demo",
                "title": "Synthetic wall repair",
                "line_items_json": json.dumps(
                    [
                        {
                            "description": "Wallboard",
                            "quantity": 3,
                            "unit": "sheet",
                            "unit_cost": 18.5,
                            "evidence_ids": [evidence_id],
                        }
                    ]
                ),
                "evidence_ids_json": json.dumps([evidence_id]),
                "assumptions_json": json.dumps(["Clear access"]),
                "exclusions_json": json.dumps(["Painting"]),
            },
        )
        estimate = estimate_result.structured_content
        assert estimate is not None
        assert estimate["totals"]["total"] == "55.50"
        assert estimate["requires_human_approval"] is True


@pytest.mark.anyio
async def test_mcp_rejects_invalid_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPEN_JOBSITE_DATA_DIR", str(tmp_path))
    async with Client(mcp) as client:
        await client.call_tool(
            "create_project", {"project_id": "bad-json", "name": "Test"}
        )
        result = await client.call_tool(
            "draft_estimate",
            {
                "project_id": "bad-json",
                "title": "Test",
                "line_items_json": "not-json",
            },
        )
        assert result.is_error is True
