---
name: scholar-search-kit
description: Instructions for using scholar-search-kit Python API and CLI to search, snowball, verify, and export scholarly literature across OpenAlex, Semantic Scholar, Crossref, PubMed, and arXiv.
---

# `scholar-search-kit` Skill Instructions

You are an expert academic research agent equipped with `scholar-search-kit`. This toolkit is the discovery, deduplication, and verification backbone for scholarly literature.

## Core Capabilities
1. **Federated Search**: Search across multiple academic APIs (`OpenAlex`, `Semantic Scholar`, `Crossref`, `PubMed`, `arXiv`, `bioRxiv`) with unified query normalization and rate limiting.
2. **Citation Snowballing**: Perform forward snowballing (finding citing papers) and backward snowballing (finding references) to expand citation graphs.
3. **Document Verification & Hydration**: Verify whether a citation is genuine or an LLM hallucination against Crossref/OpenAlex, and automatically hydrate missing abstracts and metadata.
4. **Smart Deduplication**: Cluster duplicate documents by persistent IDs (DOI, arXiv ID, PMID, OpenAlex ID) and title similarity ($\ge 97\%$), merging metadata into a rich representative record.
5. **Standardized Export**: Export collections to JSON, JSONL, or CSV for direct handoff to `scholar-pdf-kit` or `scholar-rag-kit`.

---

## Command Line Usage (CLI)

### 1. Search Literature
Search across all configured providers or a specific one:
```bash
# Query across all providers and save to JSON
uv run scholar-search search "transformer attention mechanism" --limit 30 --output results.json

# Query specifically OpenAlex with year filtering
uv run scholar-search search "retrieval augmented generation" --provider openalex --year-min 2022 --limit 20 --output rag_papers.json
```

### 2. Citation Snowballing
Trace citations or references from a foundational seed paper:
```bash
# Forward snowballing: find all papers citing Attention Is All You Need (OpenAlex ID: W2741809807)
uv run scholar-search snowball W2741809807 --provider openalex --direction forward --output citing_papers.json

# Backward snowballing: find all references cited by the paper
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --output references.json
```

### 3. Import, Verify, and Hydrate
Ingest `.ris` or `.json` collections, check for hallucinations, and enrich missing fields:
```bash
# Import an RIS collection, verify authenticity, and hydrate missing abstracts
uv run scholar-search import my_collection.ris --verify --enrich --output verified_papers.json
```

### 4. Deduplicate Existing Datasets
```bash
uv run scholar-search dedup raw_papers.json --output deduped_papers.json
```

---

## Programmatic Python API

When writing custom Python scripts or subagent workflows, use `SearchEngine` and `DocumentVerifier`:

```python
from scholar_search import SearchEngine, Query, DocumentVerifier, Exporter
from scholar_search.providers import OpenAlexProvider, SemanticScholarProvider, ArxivProvider

# 1. Initialize Engine with desired providers
engine = SearchEngine(providers=[
    OpenAlexProvider(),
    SemanticScholarProvider(),
    ArxivProvider()
])

# 2. Formulate Query
query = Query(
    text='title:"deep learning" AND "medical imaging"',
    year_min=2021,
    max_results=50
)

# 3. Search and Deduplicate
documents = engine.search_all(query, dedup=True)
print(f"Found {len(documents)} unique documents.")

# 4. Optional: Verify and Hydrate
verifier = DocumentVerifier()
processed_docs, audit = verifier.process_batch(documents, verify=True, enrich=True)

# 5. Export for downstream tools (e.g. scholar-pdf-kit)
exporter = Exporter()
exporter.json(processed_docs, "output_papers.json")
```

---

## Agent Guidelines & Best Practices
- **Interoperability**: Always export results in `json` format when handing off to `scholar-pdf-kit` (`scholar-pdf --input results.json`).
- **Polite Crawling**: The toolkit automatically throttles and caches requests via SQLite in `.cache/`. Do not bypass rate limiting.
- **Provider Selection**: Use `openalex` for general discovery and Open Access tracking, `pubmed` for biomedical literature, `arxiv` for preprints, and `semanticscholar` for citation intent and TLDRs.
