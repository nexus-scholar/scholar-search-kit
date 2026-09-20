"""Deterministic (canonical) JSON serialization for Search Corpus Snapshot.

Invariant
---------
Given an identical list of ``Document`` instances (or raw dicts), this module 
always produces **byte-identical** JSON.
That byte-identical JSON is then hashed with SHA-256 to produce the
``corpus_fingerprint``.

Serialization rules (must not change without a schema version bump)
-------------------------------------------------------------------
1. **Key order** — All object keys are sorted alphabetically for stability.
2. **Array ordering** — Array ordering is preserved as authored, as semantic
   ordering (e.g. search ranking) may be present.
3. **Whitespace** — Compact JSON; ``separators=(",", ":")``,
   ``ensure_ascii=True``, no trailing newline.
4. **Fingerprint** — ``sha256(utf8(canonical_bytes)).hexdigest()``,
   returned with the ``sha256:`` prefix.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from scholar_search.models import Document


def canonical_json(documents: list[Document] | list[dict[str, Any]]) -> bytes:
    """Serialize a list of documents to canonical UTF-8 JSON bytes.

    The output is deterministic: identical input → identical bytes.

    Parameters
    ----------
    documents:
        A list of ``Document`` instances or raw document dicts.

    Returns
    -------
    bytes
        Compact, UTF-8 encoded JSON with no trailing newline, sorted keys.
    """
    raw_list: list[dict[str, Any]] = []
    
    for doc in documents:
        if isinstance(doc, Document):
            # Convert dataclass to dict
            raw_list.append(asdict(doc))
        elif isinstance(doc, dict):
            raw_list.append(doc)
        else:
            raise TypeError(f"Expected Document or dict, got {type(doc).__name__}")

    # We use sort_keys=True to ensure all object keys are sorted alphabetically.
    # Array ordering (e.g. the list of documents itself) is preserved.
    raw_str = json.dumps(
        raw_list,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
        sort_keys=True,
        default=str, # For datetime fields like retrieved_at
    )

    return raw_str.encode("utf-8")


def canonical_fingerprint(documents: list[Document] | list[dict[str, Any]]) -> str:
    """Return the ``sha256:<hex>`` fingerprint of the canonical JSON.

    Parameters
    ----------
    documents:
        A list of ``Document`` instances or raw document dicts.

    Returns
    -------
    str
        String of the form ``'sha256:<64-hex-chars>'``.
    """
    digest = hashlib.sha256(canonical_json(documents)).hexdigest()
    return f"sha256:{digest}"
