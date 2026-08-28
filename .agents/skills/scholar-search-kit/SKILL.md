---
name: scholar-search-kit
description: Instructions for using the scholar-search-kit Python API and CLI to search, snowball, verify, deduplicate, and export academic literature across OpenAlex, Semantic Scholar, Crossref, PubMed, arXiv, and bioRxiv.
---

# `scholar-search-kit` Skill Instructions

You are an expert academic research agent equipped with `scholar-search-kit`. This toolkit is the discovery, deduplication, and verification backbone of the Nexus Scholar Suite.

## Core Capabilities
1. **Federated Academic Search**: Search across multiple scholarly repositories (`OpenAlex`, `Semantic Scholar`, `Crossref`, `PubMed`, `arXiv`, `bioRxiv`) with rate limiting and polite headers.
2. **Citation Snowballing**: Trace forward citing papers and backward reference graphs.
3. **Verification & Hydration**: Verify citation existence against Crossref/OpenAlex to detect hallucinations and hydrate missing abstracts and metrics.
4. **Smart Deduplication**: Merge duplicate records by persistent IDs (DOI, arXiv, PMID, S2, OpenAlex) and title similarity ($\ge 97\%$).
5. **Standardized Export**: Export normalized collections to JSON, JSONL, or CSV for direct handoff to `scholar-pdf-kit` or `scholar-rag-kit`.

---

## Quick CLI Cheat-Sheet

All commands should be run within the project context via `uv run`:

```bash
# 1. Search Literature (Multi-Provider or Single Provider)
uv run scholar-search search "transformer attention mechanism" --limit 30 --output results.json
uv run scholar-search search "retrieval augmented generation" --provider openalex --year-min 2022 --limit 20 --output rag_papers.json

# 2. Citation Snowballing (Forward = Citing Papers, Backward = References)
uv run scholar-search snowball W2741809807 --provider openalex --direction forward --output citing.json
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --output references.json

# 3. Import, Verify Authenticity, and Hydrate Metadata (.ris, .json, .jsonl)
uv run scholar-search import citations.ris --verify --enrich --output verified.json

# 4. Deduplicate Existing Dataset
uv run scholar-search dedup raw_papers.json --output deduped.json

# 5. Format Conversion
uv run scholar-search export input.ris output.json --format json
```

---

## Programmatic Python API

> **CRITICAL RULE**: The engine and verifier are asynchronous. All `search_all`, `snowball_*`, and `process_batch` calls must be awaited inside an `asyncio` event loop.

```python
import asyncio
from scholar_search import SearchEngine, Query, DocumentVerifier, Exporter
from scholar_search.providers import (
    OpenAlexProvider,
    SemanticScholarProvider,
    ArxivProvider,
)

async def main():
    # 1. Initialize Engine with desired providers
    engine = SearchEngine(
        providers=[OpenAlexProvider(), SemanticScholarProvider(), ArxivProvider()]
    )

    # 2. Formulate Query
    query = Query(
        text='title:"deep learning" AND "medical imaging"',
        year_min=2021,
        max_results=30,
    )

    # 3. Search and Deduplicate (Async)
    documents = await engine.search_all(query, dedup=True)
    await engine.close()

    # 4. Optional: Verify authenticity & hydrate missing metadata (Async)
    verifier = DocumentVerifier()
    processed_docs, audit = await verifier.process_batch(
        documents, verify=True, enrich=True
    )

    # 5. Export for downstream tools (e.g. scholar-pdf-kit)
    exporter = Exporter()
    exporter.json(processed_docs, "output_papers.json")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Detailed References

For advanced configuration, specialized provider options, or internal mechanisms, read these reference files on demand:

- [Academic Providers & Config](references/providers.md): Specific provider features, rate limits, API keys, and environment variables.
- [Search Syntax & Citation Snowballing](references/search_and_snowballing.md): Boolean queries, field syntax (`title:`, `author:`), and graph traversal.
- [Verification & Deduplication](references/verification_and_dedup.md): Hallucination detection algorithm, fuzzy title thresholds, and metadata merging.
- [IO & Pipeline Integration](references/io_and_pipeline.md): Ingesting RIS/JSON/JSONL, converting formats, and piping results to `scholar-pdf-kit`.

---

## Agent Guidelines & Best Practices

- **Handoff to PDF Kit**: Always export in `json` format when handing off to `scholar-pdf-kit` (`uv run scholar-pdf --input results.json`).
- **Polite Crawling & Cache**: `scholar-search-kit` automatically caches HTTP requests to SQLite in `.cache/` (30 days TTL). Do not attempt to bypass rate limits.
- **Provider Choice**:
  - `openalex`: Default recommended provider for broad discovery and Open Access tracking.
  - `pubmed`: Biomedical and life sciences literature (includes MeSH terms).
  - `arxiv` / `biorxiv`: Preprints in math/CS/physics and biology.
  - `semanticscholar`: Citation intents and paper TLDR summaries.
  - `crossref`: Authoritative DOI validation and bibliographic matching.
