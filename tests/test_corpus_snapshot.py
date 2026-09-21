from datetime import UTC, datetime

from scholar_search.identity import build_corpus_snapshot_artifact
from scholar_search.models import Author, Document, ExternalIds


CONTEXT = {
    "workspace_id": "WSP-search-contract",
    "run_id": "RUN-search-contract",
    "protocol_fingerprint": "sha256:" + "a" * 64,
    "created_at": datetime(2026, 9, 21, tzinfo=UTC),
    "commit": "1" * 40,
}


def test_same_title_distinct_studies_and_order_independence() -> None:
    left = Document(
        title="Shared short title",
        year=2020,
        provider="crossref",
        provider_id="left",
        external_ids=ExternalIds(doi="10.1000/left"),
        authors=[Author("Alpha")],
        workspace_id="SCI-000010",
    )
    right = Document(
        title="Shared short title",
        year=2024,
        provider="crossref",
        provider_id="right",
        external_ids=ExternalIds(doi="10.1000/right"),
        authors=[Author("Beta")],
        workspace_id="SCI-000020",
    )

    first = build_corpus_snapshot_artifact([left, right], **CONTEXT)
    reversed_build = build_corpus_snapshot_artifact([right, left], **CONTEXT)

    assert len(first.artifact["data"]["studies"]) == 2
    assert first.artifact == reversed_build.artifact
    assert first.outcome["status"] == "SUCCESS"


def test_transitive_doi_arxiv_bridge_and_partial_outcome() -> None:
    doi_record = Document(
        title="Bridge paper",
        year=2023,
        provider="crossref",
        provider_id="doi-record",
        external_ids=ExternalIds(doi="10.1000/bridge"),
        authors=[Author("Bridge")],
    )
    bridge_record = Document(
        title="Bridge paper extended",
        year=2023,
        provider="openalex",
        provider_id="bridge-record",
        external_ids=ExternalIds(doi="10.1000/bridge", arxiv_id="2401.00001"),
        authors=[Author("Bridge")],
    )
    arxiv_record = Document(
        title="Bridge preprint",
        year=2023,
        provider="arxiv",
        provider_id="arxiv-record",
        external_ids=ExternalIds(arxiv_id="2401.00001"),
        authors=[Author("Bridge")],
    )

    result = build_corpus_snapshot_artifact(
        [doi_record, bridge_record, arxiv_record],
        provider_warnings=["semantic-scholar unavailable"],
        **CONTEXT,
    )

    studies = result.artifact["data"]["studies"]
    assert len(studies) == 1
    assert len(studies[0]["source_record_ids"]) == 3
    assert studies[0]["external_ids"]["doi"] == ["10.1000/bridge"]
    assert studies[0]["external_ids"]["arxiv"] == ["2401.00001"]
    assert result.outcome["status"] == "PARTIAL"
