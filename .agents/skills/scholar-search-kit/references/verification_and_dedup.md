# Document Verification, Hydration, and Deduplication Reference

This guide explains how `scholar-search-kit` detects LLM hallucinations, enriches sparse bibliographic records, and deduplicates multi-provider results.

---

## 1. Document Verification & Hallucination Detection

The `DocumentVerifier` validates citations against **Crossref** and **OpenAlex**.

### Verification Workflow
1. **DOI Verification**: If the document contains a DOI, query Crossref (`/works/{doi}`). If valid, extract normalized canonical metadata.
2. **Bibliographic Crossref Match**: If no DOI or lookup fails, send the title to Crossref's reference matching endpoint. Compute string similarity (`SequenceMatcher.ratio()`) against the matched candidate; if $\ge 90\%$, mark as verified.
3. **OpenAlex Candidate Search**: If Crossref fails, search OpenAlex by title (`per-page=1`). If candidate similarity $\ge 90\%$, mark as verified.
4. **Failure Case**: If all steps fail, the record is flagged as `Unverified: Record not found in Crossref or OpenAlex`.

---

## 2. Metadata Hydration

When `--enrich` or `enrich=True` is enabled on verified documents:
- Queries OpenAlex using the verified DOI (`https://api.openalex.org/works/https://doi.org/{doi}`).
- Fills in missing fields: `abstract`, `venue`, `url`, `year`, `authors`, `citations_count`, `references_count`, and `openalex_id`.

---

## 3. Deduplication & Clustering

The `Deduplicator` merges duplicate records gathered across disparate providers:

### Matching Rules
1. **Exact Persistent Identifier Match**:
   - Matches if any of `doi`, `arxiv_id`, `pubmed_id`, `openalex_id`, or `s2_id` match exactly.
2. **Conservative Normalized Title Match**:
   - Strips non-alphanumeric characters, lowercases, and compares using `SequenceMatcher`.
   - Threshold: $\ge 97\%$ similarity.

### Metadata Merging Logic (`_merge_metadata`)
When two documents belong to the same cluster:
- **Identifiers**: Adopts any missing IDs (`doi`, `arxiv_id`, `pubmed_id`, `openalex_id`, `s2_id`) from the duplicate into the representative.
- **Text Attributes**: Populates empty fields (`abstract`, `venue`, `url`, `year`, `tldr`).
- **Authors**: Adopts authors if empty.
- **Metrics**: Takes the maximum of `citations_count` and `references_count`.
- **Arrays**: Computes union of `mesh_terms` and `citation_intents`.

---

## 4. Usage in CLI & Python API

### CLI Verification & Dedup
```bash
# Ingest, verify against Crossref/OpenAlex, hydrate missing abstracts/metrics
uv run scholar-search import citations.ris --verify --enrich --output verified_papers.json

# Deduplicate an existing JSON dataset
uv run scholar-search dedup raw_combined_papers.json --output deduped.json
```

### Python API
```python
import asyncio
from scholar_search import DocumentVerifier, Deduplicator, Document, ExternalIds

async def main():
    verifier = DocumentVerifier()
    deduplicator = Deduplicator()

    raw_docs = [
        Document(
            title="Attention is all you need",
            external_ids=ExternalIds(arxiv_id="1706.03762")
        ),
        Document(
            title="Attention Is All You Need",
            external_ids=ExternalIds(doi="10.5555/3295222.3295349")
        )
    ]

    # 1. Deduplicate
    clusters = deduplicator.deduplicate(raw_docs)
    unique_docs = [c.representative for c in clusters]
    print(f"Merged {len(raw_docs)} records into {len(unique_docs)} unique doc.")

    # 2. Verify and Hydrate (Async)
    processed, audit_log = await verifier.process_batch(
        unique_docs, verify=True, enrich=True
    )
    for entry in audit_log:
        print(f"Title: {entry['title']} | Verified: {entry['verified']} | Status: {entry['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```
