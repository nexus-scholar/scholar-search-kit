# Document Verification, Metadata Hydration, and Deduplication

This guide covers citation verification, LLM hallucination detection, metadata hydration, and record deduplication across multiple providers.

---

## 1. Document Verification & Hallucination Detection

`DocumentVerifier` validates citations against **Crossref** and **OpenAlex** to determine whether a given citation is authentic or an LLM-generated hallucination.

### Verification Flow
1. **DOI Verification**: If a DOI is present, `DocumentVerifier` queries Crossref (`/works/{doi}`). If valid, canonical metadata is normalized.
2. **Bibliographic Crossref Matching**: If no DOI exists or lookup fails, the title is sent to Crossref's reference matching engine. The string similarity between the candidate and target is evaluated using Python's `SequenceMatcher.ratio()`. If similarity is $\ge 90\%$, the record is verified.
3. **OpenAlex Fallback Matching**: If Crossref does not yield a match, OpenAlex is searched by title (`per-page=1`). If candidate similarity is $\ge 90\%$, the record is verified.
4. **Unverified Records**: If none of the verification steps succeed, the record is flagged as `Unverified: Record not found in Crossref or OpenAlex`.

---

## 2. Metadata Hydration

When `--enrich` (CLI) or `enrich=True` (Python API) is enabled on verified documents:
- Queries OpenAlex using the verified DOI (`https://api.openalex.org/works/https://doi.org/{doi}`).
- Automatically hydrates missing fields: `abstract`, `venue`, `url`, `year`, `authors`, `citations_count`, `references_count`, and `openalex_id`.

---

## 3. Deduplication & Clustering

The `Deduplicator` merges duplicate documents found across different providers into representative records:

### Matching Strategy
1. **Persistent Identifiers**:
   - Matches records sharing any identical identifier: `doi`, `arxiv_id`, `pubmed_id`, `openalex_id`, or `s2_id`.
2. **Conservative Title Matching**:
   - Normalizes titles by stripping punctuation and whitespace, then calculates `SequenceMatcher` ratio.
   - Merging threshold: $\ge 97\%$ title similarity.

### Metadata Merging Logic
When duplicate records are merged:
- **Identifiers**: Copies missing IDs (`doi`, `arxiv_id`, `pubmed_id`, etc.) to the representative document.
- **Text Metadata**: Fills missing text fields (`abstract`, `venue`, `url`, `year`, `tldr`).
- **Authors**: Adopts authors if not already present.
- **Metrics**: Takes the maximum of `citations_count` and `references_count`.
- **Arrays**: Performs a deduplicated union of `mesh_terms` and `citation_intents`.

---

## 4. Examples

### CLI Verification & Deduplication
```bash
# Ingest an RIS file, verify authenticity against Crossref/OpenAlex, and hydrate abstracts
uv run scholar-search import citations.ris --verify --enrich --output verified_papers.json

# Deduplicate an existing JSON dataset
uv run scholar-search dedup raw_combined_papers.json --output deduped.json
```

### Programmatic Python API
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

    # 1. Deduplicate records
    clusters = deduplicator.deduplicate(raw_docs)
    unique_docs = [c.representative for c in clusters]
    print(f"Merged {len(raw_docs)} records into {len(unique_docs)} unique document.")

    # 2. Verify authenticity and hydrate missing metadata (Async)
    processed, audit_log = await verifier.process_batch(
        unique_docs, verify=True, enrich=True
    )
    for entry in audit_log:
        print(f"Title: {entry['title']} | Verified: {entry['verified']} | Status: {entry['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```
