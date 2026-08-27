"""Local JSON project storage with atomic writes and strict project identifiers."""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
EVIDENCE_TYPES = {
    "document",
    "measurement",
    "note",
    "photo",
    "receipt",
    "sketch",
    "voice_transcript",
}
PUBLICATION_STATUSES = {"private", "synthetic", "permission_cleared"}
_WRITE_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError(
            "project_id must be 1–64 lowercase letters, numbers, hyphens, or "
            "underscores, and must start with a letter or number"
        )
    return project_id


class JobsiteStore:
    """Store projects under a user-controlled local directory."""

    def __init__(self, root: str | Path | None = None) -> None:
        configured = root or os.environ.get("OPEN_JOBSITE_DATA_DIR")
        self.root = Path(configured) if configured else Path.cwd() / ".open-jobsite-data"

    def _path(self, project_id: str) -> Path:
        return self.root / f"{validate_project_id(project_id)}.json"

    def _read(self, project_id: str) -> dict[str, Any]:
        path = self._path(project_id)
        if not path.exists():
            raise FileNotFoundError(f"project not found: {project_id}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"project file is invalid JSON: {path.name}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"project file must contain a JSON object: {path.name}")
        return data

    def _write(self, project_id: str, data: dict[str, Any]) -> None:
        path = self._path(project_id)
        self.root.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.root,
                prefix=f".{project_id}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(serialized)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_name = temporary.name
            os.replace(temporary_name, path)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def create_project(
        self,
        project_id: str,
        name: str,
        description: str = "",
    ) -> dict[str, Any]:
        validate_project_id(project_id)
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("name cannot be empty")
        with _WRITE_LOCK:
            path = self._path(project_id)
            if path.exists():
                raise FileExistsError(f"project already exists: {project_id}")
            now = utc_now()
            project: dict[str, Any] = {
                "schema_version": "0.1",
                "project_id": project_id,
                "name": clean_name,
                "description": description.strip(),
                "created_at": now,
                "updated_at": now,
                "evidence": [],
                "artifacts": [],
            }
            self._write(project_id, project)
        return deepcopy(project)

    def get_project(self, project_id: str) -> dict[str, Any]:
        return deepcopy(self._read(project_id))

    def record_evidence(
        self,
        project_id: str,
        evidence_type: str,
        source_reference: str,
        content: str,
        publication_status: str = "private",
    ) -> dict[str, Any]:
        if evidence_type not in EVIDENCE_TYPES:
            allowed = ", ".join(sorted(EVIDENCE_TYPES))
            raise ValueError(f"evidence_type must be one of: {allowed}")
        if publication_status not in PUBLICATION_STATUSES:
            allowed = ", ".join(sorted(PUBLICATION_STATUSES))
            raise ValueError(f"publication_status must be one of: {allowed}")
        if not source_reference.strip():
            raise ValueError("source_reference cannot be empty")
        if not content.strip():
            raise ValueError("content cannot be empty")
        with _WRITE_LOCK:
            project = self._read(project_id)
            evidence = {
                "evidence_id": f"ev-{uuid4().hex[:12]}",
                "evidence_type": evidence_type,
                "source_reference": source_reference.strip(),
                "content": content.strip(),
                "publication_status": publication_status,
                "recorded_at": utc_now(),
            }
            project["evidence"].append(evidence)
            project["updated_at"] = utc_now()
            self._write(project_id, project)
        return deepcopy(evidence)

    def save_artifact(self, project_id: str, artifact: dict[str, Any]) -> dict[str, Any]:
        with _WRITE_LOCK:
            project = self._read(project_id)
            evidence_ids = {
                item["evidence_id"] for item in project.get("evidence", [])
            }
            requested_ids = set(artifact.get("evidence_ids", []))
            for line_item in artifact.get("line_items", []):
                if isinstance(line_item, dict):
                    requested_ids.update(line_item.get("evidence_ids", []))
            missing = sorted(requested_ids - evidence_ids)
            if missing:
                raise ValueError(f"unknown evidence_ids: {', '.join(missing)}")
            project["artifacts"].append(deepcopy(artifact))
            project["updated_at"] = utc_now()
            self._write(project_id, project)
        return deepcopy(artifact)
