# Search, Query Translation, and Citation Snowballing Reference

This guide details query formulation, Boolean parsing, multi-provider search orchestration, and citation snowballing.

---

## 1. Query Translation & Boolean Syntax

`scholar-search-kit` includes a query parser (`QueryParser`) and provider-specific query translators (`BooleanQueryTranslator`).

### Supported Syntax
- **Boolean Operators**: `AND`, `OR`, `NOT` (case-insensitive in user input, parsed canonically).
- **Exact Phrases**: Quoted strings, e.g. `"retrieval augmented generation"`.
- **Grouping**: Parentheses `(...)` for nested logic, e.g. `("large language models" OR LLM) AND (benchmarking OR evaluation)`.
- **Field-Scoped Filters**: Prefix terms or phrases with standard field indicators:
  - `title:` — Search exclusively in paper titles.
  - `abstract:` — Search in abstract text.
  - `author:` — Search by author name.
  - `year:` — Filter by publication year.
  - `venue:` — Search by journal or conference venue.
  - `doi:` — Filter by specific DOI.
  - `keyword:` — Search keyword list.

---

## 2. CLI Usage

### Search Literature
```bash
# Query across all default providers
uv run scholar-search search "transformer attention mechanism" --limit 30 --output results.json

# Query a single provider with year constraints
uv run scholar-search search 'title:"machine learning" AND healthcare' --provider pubmed --year-min 2020 --year-max 2024 --limit 50 --output pubmed_ml.json

# Export to CSV without deduplication
uv run scholar-search search "quantum computing" --no-dedup --output quantum.csv --format csv
```

### Citation Snowballing
```bash
# Forward snowballing: find all papers citing Attention Is All You Need (OpenAlex ID: W2741809807)
uv run scholar-search snowball W2741809807 --provider openalex --direction forward --limit 50 --output citing_attention.json

# Backward snowballing: find all references cited by the paper
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --limit 50 --output attention_refs.json

# Snowballing using Semantic Scholar
uv run scholar-search snowball 204e3073870fae3d05bcbc2f6a8e263c9b72e776 --provider semanticscholar --direction forward --output s2_citing.json
```

---

## 3. Asynchronous Python API

```python
import asyncio
from scholar_search import SearchEngine, Query
from scholar_search.providers import OpenAlexProvider, ArxivProvider, SemanticScholarProvider

async def main():
    # 1. Initialize engine with specific providers (or default to all if empty)
    engine = SearchEngine(providers=[OpenAlexProvider(), ArxivProvider(), SemanticScholarProvider()])

    # 2. Formulate query
    query = Query(
        text='title:"neural radiance fields" AND "3D reconstruction"',
        year_min=2021,
        max_results=30
    )

    # 3. Concurrent search across providers (automatically deduplicated)
    documents = await engine.search_all(query, dedup=True)
    print(f"Retrieved {len(documents)} unique papers.")

    # 4. Forward snowballing on a foundational seed paper
    if documents and documents[0].provider_id:
        seed_id = documents[0].provider_id
        citing_papers = await engine.snowball_forward(seed_id, provider_name="openalex")
        print(f"Retrieved {len(citing_papers)} citing papers.")

    # 5. Clean up HTTP client sessions
    await engine.close()

if __name__ == "__main__":
    asyncio.run(main())
```
