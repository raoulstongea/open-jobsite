import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from open_jobsite.store import JobsiteStore, validate_project_id


def test_create_read_and_record_evidence(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    created = store.create_project("demo-01", "Synthetic bathroom repair")
    assert created["project_id"] == "demo-01"

    evidence = store.record_evidence(
        "demo-01",
        "measurement",
        "synthetic field card A",
        "Wall measures 10 ft by 8 ft.",
        "synthetic",
    )
    project = store.get_project("demo-01")
    assert project["evidence"] == [evidence]
    assert evidence["evidence_id"].startswith("ev-")

    on_disk = json.loads((tmp_path / "demo-01.json").read_text(encoding="utf-8"))
    assert on_disk["evidence"][0]["publication_status"] == "synthetic"


def test_duplicate_project_is_rejected(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    store.create_project("demo", "Demo")
    with pytest.raises(FileExistsError):
        store.create_project("demo", "Duplicate")


def test_concurrent_evidence_writes_do_not_lose_an_update(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    store.create_project("parallel", "Parallel test")

    def record(index: int) -> dict:
        return JobsiteStore(tmp_path).record_evidence(
            "parallel",
            "note",
            f"synthetic source {index}",
            f"Synthetic note {index}",
            "synthetic",
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        recorded = list(executor.map(record, [1, 2]))

    project = store.get_project("parallel")
    assert len(project["evidence"]) == 2
    assert {item["evidence_id"] for item in project["evidence"]} == {
        item["evidence_id"] for item in recorded
    }


@pytest.mark.parametrize(
    "project_id", ["../escape", "Uppercase", "has a space", "", "-starts-dash"]
)
def test_unsafe_project_ids_are_rejected(project_id: str) -> None:
    with pytest.raises(ValueError):
        validate_project_id(project_id)


def test_unknown_evidence_type_is_rejected(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    store.create_project("demo", "Demo")
    with pytest.raises(ValueError, match="evidence_type"):
        store.record_evidence("demo", "email", "source", "content")


def test_artifact_cannot_claim_unknown_evidence(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    store.create_project("demo", "Demo")
    with pytest.raises(ValueError, match="unknown evidence_ids"):
        store.save_artifact("demo", {"evidence_ids": ["ev-missing"]})


def test_line_item_cannot_claim_unknown_evidence(tmp_path: Path) -> None:
    store = JobsiteStore(tmp_path)
    store.create_project("demo", "Demo")
    artifact = {
        "evidence_ids": [],
        "line_items": [{"evidence_ids": ["ev-missing"]}],
    }
    with pytest.raises(ValueError, match="unknown evidence_ids"):
        store.save_artifact("demo", artifact)
