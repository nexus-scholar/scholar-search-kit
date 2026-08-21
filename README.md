# Scholar Search Kit

[![CI Status](https://github.com/nexus-scholar-org/scholar-search-kit/actions/workflows/scholar-search-kit-ci.yml/badge.svg)](https://github.com/nexus-scholar-org/scholar-search-kit/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Scholar Search Kit** is the discovery, deduplication, and verification backbone of the Nexus Scholar Suite.

It provides a unified Python API and Command Line Interface (CLI) to query, normalize, verify, and export academic literature across major scholarly databases: **OpenAlex**, **Semantic Scholar**, **Crossref**, **PubMed**, **arXiv**, and **bioRxiv**.

---

## Key Features

- **Federated Academic Search**: Search across multiple scholarly repositories simultaneously with automatic rate limiting and polite crawler headers.
- **Citation Snowballing**: Perform forward snowballing (finding citing papers) and backward snowballing (traversing references) to map research fields.
- **Document Verification & Hydration**: Detect LLM hallucinations and verify citation existence against Crossref/OpenAlex, hydrating missing abstracts, venues, and metrics.
- **Smart Deduplication**: Merges duplicate records by persistent identifiers (DOI, arXiv ID, PMID, OpenAlex ID) and title similarity ($\ge 97\%$), combining metadata into a comprehensive representative record.
- **Interoperable Export**: Directly export normalized results to JSON, JSONL, or CSV for seamless downstream processing with `scholar-pdf-kit` and `scholar-rag-kit`.

---

## Installation

Ensure `git` and `uv` are installed on your system.

```bash
# Clone the repository
git clone https://github.com/nexus-scholar-org/scholar-search-kit.git

# Navigate to the toolkit directory
cd scholar-search-kit

# Install the package and dependencies
uv pip install -e .
```

---

## Command Line Interface (CLI)

### 1. Multi-Provider Literature Search
```bash
uv run scholar-search search "transformer attention mechanism" --limit 20 --output results.json
```

**Example Output:**
```text
Search Results for: 'transformer attention mechanism'
┌────────┬────────────────────────────────┬──────────────┬──────────────────────┬────────────┐
│ Year   │ Title                          │ Provider     │ DOI / ID             │  Citations │
├────────┼────────────────────────────────┼──────────────┼──────────────────────┼────────────┤
│ 2017   │ Attention Is All You Need      │ openalex     │ 10.5555/3295222.329… │     145000 │
│ 2018   │ BERT: Pre-training of Deep     │ arxiv        │ 1810.04805           │      92000 │
│        │ Bidirectional Transformers     │              │                      │            │
└────────┴────────────────────────────────┴──────────────┴──────────────────────┴────────────┘
Saved 20 documents to results.json (JSON)
```

### 2. Citation Snowballing
```bash
# Forward snowballing (papers citing Attention Is All You Need)
uv run scholar-search snowball W2741809807 --provider openalex --direction forward --limit 25 --output citing.json

# Backward snowballing (papers cited by Attention Is All You Need)
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --limit 25 --output refs.json
```

### 3. Ingestion, Verification, & Hydration
```bash
# Import an RIS or JSON library, verify existence, and hydrate missing abstracts
uv run scholar-search import my_collection.ris --verify --enrich --output verified.json
```

### 4. Deduplication
```bash
uv run scholar-search dedup raw_papers.json --output deduped.json
```

---

## Programmatic Python API

```python
from scholar_search import SearchEngine, Query, DocumentVerifier, Exporter
from scholar_search.providers import OpenAlexProvider, ArxivProvider

# 1. Initialize Engine
engine = SearchEngine(providers=[OpenAlexProvider(), ArxivProvider()])

# 2. Execute Query
query = Query(text='title:"deep learning"', year_min=2022, max_results=25)
documents = engine.search_all(query, dedup=True)

# 3. Export to JSON for scholar-pdf-kit
Exporter().json(documents, "literature_review.json")
```

---

## Documentation

Detailed guides and references are available in the `docs/` directory:
- [Tutorial](docs/tutorial.md): Step-by-step walkthrough of search, snowballing, and verification.
- [API Reference](docs/api_reference.md): Technical interface documentation.

---

## License

This project is licensed under the MIT License.
