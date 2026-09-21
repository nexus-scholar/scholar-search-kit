"""Corpus snapshot identity adapter for Nexus Scholar Contract v1.

Exposes deterministic corpus identity, canonical fingerprints, COR-* corpus
identifiers, and producer provenance metadata to downstream envelopes.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import os
import pathlib
import subprocess
from dataclasses import asdict
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from scholar_search.canonical import canonical_fingerprint, canonical_json
from scholar_search.dedup import Deduplicator
from scholar_search.models import Document

_PACKAGE_NAME = "scholar-search-kit"
try:
    _PACKAGE_VERSION = importlib.metadata.version(_PACKAGE_NAME)
except importlib.metadata.PackageNotFoundError:
    _PACKAGE_VERSION = "0+unknown"
_COR_ID_RE = r"^COR-[A-Za-z0-9][A-Za-z0-9._-]*$"
_SHA256_RE = r"^sha256:[0-9a-f]{64}$"


class CorpusProducer(BaseModel):
    """Provenance metadata describing the corpus producer."""

    model_config = ConfigDict(extra="allow")

    package: str = Field(_PACKAGE_NAME, min_length=1)
    version: str = Field(_PACKAGE_VERSION, min_length=1)
    commit: str = Field(..., min_length=1)


class CorpusSnapshotIdentity(BaseModel):
    """Typed corpus identity output for downstream Contract v1 envelopes."""

    model_config = ConfigDict(extra="allow")

    corpus_id: str = Field(..., pattern=_COR_ID_RE)
    corpus_fingerprint: str = Field(..., pattern=_SHA256_RE)
    schema_version: str = Field("1.0.0", min_length=1)
    producer: CorpusProducer
    workspace_id: str = ""
    canonical_bytes: bytes = Field(default=b"", repr=False, exclude=True)

    def as_envelope_context(self) -> dict[str, str]:
        """Return context fields required by downstream artifact envelopes."""
        return {
            "corpus_id": self.corpus_id,
            "corpus_fingerprint": self.corpus_fingerprint,
        }

    def to_dict(self) -> dict[str, Any]:
        """Emit a JSON-serializable dictionary."""
        return self.model_dump(mode="json")


class CorpusSnapshotBuild(BaseModel):
    """Contract-v1 corpus envelope plus its producer operation outcome."""

    model_config = ConfigDict(extra="forbid")

    artifact: dict[str, Any]
    outcome: dict[str, Any]


def resolve_producer_commit(explicit_commit: str | None = None) -> str:
    """Resolve the git commit hash for scholar-search-kit."""
    if explicit_commit and explicit_commit.strip():
        return explicit_commit.strip()

    for env_key in ("SCHOLAR_SEARCH_COMMIT", "NEXUS_SCHOLAR_COMMIT", "GIT_COMMIT"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val

    # A vendored checkout belongs to the harness Git repository, so asking Git
    # for HEAD there reports the harness revision. Prefer its exact kit pin.
    try:
        monorepo_root = pathlib.Path(__file__).resolve().parents[4]
        plugins_json = monorepo_root / ".agents" / "plugins" / "nexus-scholar" / "plugins.json"
        if plugins_json.is_file():
            data = json.loads(plugins_json.read_text(encoding="utf-8"))
            for p in data.get("plugins", []):
                if p.get("name") == "scholar-search-kit":
                    rev = p.get("default_rev", "").strip()
                    if rev:
                        return rev
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        pass

    try:
        pkg_dir = pathlib.Path(__file__).resolve().parent
        res = subprocess.run(
            ["git", "-C", str(pkg_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except OSError:
        pass

    return "unknown"


def mint_or_accept_corpus_id(
    documents: list[Document] | list[dict[str, Any]] | str,
    canonical_bytes: bytes | None = None,
) -> str:
    """Accept an authored COR-* corpus identifier or deterministically mint one.

    If the input provides a valid COR-* ID (as a string), it is returned.
    Otherwise, a stable COR-* identifier is minted from the SHA-256 hash of the
    canonical bytes, preserving corpus fingerprint semantics without mutation.
    """
    import re

    # If it's already a COR- string
    if isinstance(documents, str):
        if re.match(_COR_ID_RE, documents):
            return documents
        raise ValueError(f"String input must be a COR- ID, got: {documents}")

    if canonical_bytes is None:
        canonical_bytes = canonical_json(documents)

    digest = hashlib.sha256(canonical_bytes).hexdigest()[:32]
    return f"COR-{digest}"


def get_corpus_identity(
    documents: list[Document] | list[dict[str, Any]] | pathlib.Path | str | bytes,
    *,
    commit: str | None = None,
    schema_version: str = "1.0.0",
) -> CorpusSnapshotIdentity:
    """Extract or construct a CorpusSnapshotIdentity from any supported input.

    Parameters
    ----------
    documents:
        A list of Document instances, list of dicts, pathlib.Path to a JSON file,
        or raw JSON bytes/str containing the corpus snapshot.
    commit:
        Optional explicit commit hash for producer provenance.
    schema_version:
        Contract schema version (default: '1.0.0').

    Returns
    -------
    CorpusSnapshotIdentity:
        Validated corpus identity with COR-* ID, canonical fingerprint,
        and producer metadata.
    """
    parsed_docs: list[Document] | list[dict[str, Any]]
    
    if isinstance(documents, pathlib.Path) or (
        isinstance(documents, str)
        and not documents.strip().startswith("[")
        and not documents.strip().startswith("{")
        and "\n" not in documents
    ):
        path = pathlib.Path(documents)
        if not path.is_file():
            raise FileNotFoundError(f"Corpus file not found: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for key in ("results", "papers", "documents", "data"):
                if key in raw and isinstance(raw[key], list):
                    raw = raw[key]
                    break
            else:
                raw = [raw]
        parsed_docs = raw
    elif isinstance(documents, str):
        raw = json.loads(documents)
        if isinstance(raw, dict):
            for key in ("results", "papers", "documents", "data"):
                if key in raw and isinstance(raw[key], list):
                    raw = raw[key]
                    break
            else:
                raw = [raw]
        parsed_docs = raw
    elif isinstance(documents, (bytes, bytearray)):
        raw = json.loads(documents.decode("utf-8"))
        if isinstance(raw, dict):
            for key in ("results", "papers", "documents", "data"):
                if key in raw and isinstance(raw[key], list):
                    raw = raw[key]
                    break
            else:
                raw = [raw]
        parsed_docs = raw
    elif isinstance(documents, list):
        parsed_docs = documents
    else:
        raise TypeError(f"Unsupported corpus type: {type(documents).__name__}")

    raw_canon = canonical_json(parsed_docs)
    fp = canonical_fingerprint(parsed_docs)
    corp_id = mint_or_accept_corpus_id(parsed_docs, canonical_bytes=raw_canon)
    producer_info = CorpusProducer(
        package=_PACKAGE_NAME,
        version=_PACKAGE_VERSION,
        commit=resolve_producer_commit(commit),
    )

    workspace_id = ""
    # Attempt to extract workspace_id from the first document if available
    if parsed_docs and len(parsed_docs) > 0:
        first_doc = parsed_docs[0]
        if isinstance(first_doc, Document):
            workspace_id = first_doc.workspace_id or ""
        elif isinstance(first_doc, dict):
            workspace_id = first_doc.get("workspace_id", "")

    return CorpusSnapshotIdentity(
        corpus_id=corp_id,
        corpus_fingerprint=fp,
        schema_version=schema_version,
        producer=producer_info,
        workspace_id=workspace_id,
        canonical_bytes=raw_canon,
    )


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}{_fingerprint(value).removeprefix('sha256:')[:32]}"


def _record_identity(document: Document) -> dict[str, Any]:
    external = asdict(document.external_ids)
    return {
        "provider": document.provider,
        "provider_id": document.provider_id,
        "external_ids": {key: value for key, value in external.items() if value},
        "title": document.title,
        "publication_year": document.year,
    }


def _external_ids(documents: list[Document]) -> dict[str, list[str]]:
    values: dict[str, set[str]] = {}
    names = {
        "doi": "doi",
        "arxiv_id": "arxiv",
        "pubmed_id": "pubmed",
        "openalex_id": "openalex",
        "s2_id": "semantic_scholar",
    }
    for document in documents:
        for attribute, provider in names.items():
            value = getattr(document.external_ids, attribute)
            if value:
                values.setdefault(provider, set()).add(str(value))
    return {provider: sorted(ids) for provider, ids in sorted(values.items())}


def _corpus_fingerprint(data: dict[str, Any]) -> str:
    normalized_studies = []
    for study in data["studies"]:
        normalized_studies.append(
            {
                **study,
                "source_record_ids": sorted(study["source_record_ids"]),
                "alias_ids": sorted(study["alias_ids"]),
                "external_ids": {
                    provider: sorted(values)
                    for provider, values in sorted(study["external_ids"].items())
                },
            }
        )
    normalized_studies.sort(key=lambda item: item["study_id"])
    return _fingerprint(
        {
            **data,
            "studies": normalized_studies,
            "record_to_study": dict(sorted(data["record_to_study"].items())),
        }
    )


def build_corpus_snapshot_artifact(
    documents: list[Document],
    *,
    workspace_id: str,
    run_id: str,
    protocol_fingerprint: str,
    created_at: datetime,
    provider_warnings: list[str] | None = None,
    provider_errors: list[dict[str, Any]] | None = None,
    commit: str | None = None,
) -> CorpusSnapshotBuild:
    """Deduplicate records and emit a deterministic Contract-v1 corpus snapshot."""

    if not documents:
        raise ValueError("a corpus snapshot requires at least one source record")

    warnings = list(provider_warnings or [])
    errors = list(provider_errors or [])
    working_documents = copy.deepcopy(documents)
    original_aliases = {
        id(document): document.workspace_id
        for document in working_documents
        if document.workspace_id and document.workspace_id.startswith("SCI-")
    }
    record_ids = {
        id(document): _stable_id("REC-", _record_identity(document))
        for document in working_documents
    }
    clusters = Deduplicator().deduplicate(working_documents)

    studies: list[dict[str, Any]] = []
    record_to_study: dict[str, str] = {}
    for cluster in clusters:
        members = list(cluster.members)
        member_records = sorted({record_ids[id(member)] for member in members})
        study_id = _stable_id("STU-", member_records)
        aliases = sorted(
            {
                original_aliases[id(member)]
                for member in members
                if id(member) in original_aliases
            }
        )
        studies.append(
            {
                "study_id": study_id,
                "source_record_ids": member_records,
                "alias_ids": aliases,
                "external_ids": _external_ids(members),
                "title": cluster.representative.title,
                "publication_year": cluster.representative.year,
            }
        )
        record_to_study.update({record_id: study_id for record_id in member_records})

    studies.sort(key=lambda item: item["study_id"])
    identity_graph = {
        "identity_algorithm_version": "search-dedup-v1",
        "studies": studies,
        "record_to_study": dict(sorted(record_to_study.items())),
    }
    corpus_id = _stable_id("COR-", identity_graph)
    data = {"corpus_id": corpus_id, **identity_graph}
    corpus_fingerprint = _corpus_fingerprint(data)
    producer = CorpusProducer(commit=resolve_producer_commit(commit)).model_dump(mode="json")
    artifact_id = _stable_id(
        "ART-corpus-",
        {
            "workspace_id": workspace_id,
            "run_id": run_id,
            "protocol_fingerprint": protocol_fingerprint,
            "corpus_fingerprint": corpus_fingerprint,
        },
    )
    artifact = {
        "schema_version": "1.0.0",
        "artifact_type": "corpus_snapshot",
        "artifact_id": artifact_id,
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "producer": producer,
        "workspace_id": workspace_id,
        "run_id": run_id,
        "protocol_fingerprint": protocol_fingerprint,
        "corpus_fingerprint": corpus_fingerprint,
        "inputs": [],
        "data": data,
    }
    status = "PARTIAL" if warnings or errors else "SUCCESS"
    outcome = {
        "contract_version": "1.0.0",
        "operation": "search.corpus_snapshot",
        "run_id": run_id,
        "status": status,
        "data": {
            "source_record_count": len(documents),
            "study_count": len(studies),
        },
        "artifacts": [],
        "warnings": warnings,
        "errors": errors,
        "provenance": {"producer": producer},
    }
    return CorpusSnapshotBuild(artifact=artifact, outcome=outcome)
