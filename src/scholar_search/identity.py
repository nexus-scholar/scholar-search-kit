"""Corpus snapshot identity adapter for Nexus Scholar Contract v1.

Exposes deterministic corpus identity, canonical fingerprints, COR-* corpus
identifiers, and producer provenance metadata to downstream envelopes.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from scholar_search.canonical import canonical_fingerprint, canonical_json
from scholar_search.models import Document
from scholar_search.importers import JSONImporter

_PACKAGE_NAME = "scholar-search-kit"
_PACKAGE_VERSION = "1.0.0"
_COR_ID_RE = r"^COR-[A-Za-z0-9][A-Za-z0-9._-]*$"
_SHA256_RE = r"^sha256:[0-9a-f]{64}$"
_DEFAULT_FALLBACK_COMMIT = "46874778cd0dde6d89414532b52d258843789132"


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


def resolve_producer_commit(explicit_commit: str | None = None) -> str:
    """Resolve the git commit hash for scholar-search-kit."""
    if explicit_commit and explicit_commit.strip():
        return explicit_commit.strip()

    for env_key in ("SCHOLAR_SEARCH_COMMIT", "NEXUS_SCHOLAR_COMMIT", "GIT_COMMIT"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val

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
    except Exception:
        pass

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
    except Exception:
        pass

    return _DEFAULT_FALLBACK_COMMIT


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
