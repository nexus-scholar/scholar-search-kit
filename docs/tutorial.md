# Scholar Search Kit Tutorial

A complete walkthrough on how to search, snowball, verify, and export academic literature using `scholar-search-kit`.

## 1. Installation & Environment Setup

```bash
cd slr-search-kit
uv pip install -e .
```

---

## 2. Searching Across Academic Providers

The `scholar-search` command provides a unified interface across OpenAlex, Semantic Scholar, Crossref, PubMed, arXiv, and bioRxiv.

### Example A: Multi-Provider Federated Search
Query across all providers with automatic deduplication:
```bash
uv run scholar-search search "retrieval augmented generation" --limit 20 --output rag_papers.json
```

### Example B: Provider-Specific Search with Year Filters
```bash
uv run scholar-search search "crispr cas9" --provider pubmed --year-min 2022 --limit 15 --output crispr.json
```

---

## 3. Citation Snowballing

Snowballing expands your literature graph from a single seminal paper.

### Example A: Forward Snowballing (Find Citing Papers)
Find papers citing *Attention Is All You Need* (OpenAlex ID: `W2741809807`):
```bash
uv run scholar-search snowball W2741809807 --provider openalex --direction forward --limit 25 --output citing_attention.json
```

### Example B: Backward Snowballing (Find Referenced Papers)
Find the foundational bibliography cited by a paper:
```bash
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --output references_attention.json
```

---

## 4. Ingesting, Verifying, & Hydrating Citations

When working with reference manager exports (`.ris`) or LLM-generated citation lists, verify their authenticity and hydrate missing abstracts.

```bash
# Ingest an RIS export from Zotero, verify against Crossref, and hydrate abstracts from OpenAlex
uv run scholar-search import my_zotero_library.ris --verify --enrich --output verified_library.json
```

**What `--verify` and `--enrich` do:**
1. Cross-references titles and DOIs against Crossref's 150M+ document index.
2. Flags unverified / hallucinated citations with clear warnings.
3. Automatically fetches missing abstracts, publication venues, and citation metrics from OpenAlex.

---

## 5. Deduplicating Existing Collections

Merge duplicate records collected across different search engines while preserving the richest metadata:
```bash
uv run scholar-search dedup raw_scraped_papers.json --output deduped_collection.json
```
