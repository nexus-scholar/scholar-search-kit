# Academic Providers & Configuration Guide

`scholar-search-kit` connects to 6 major scholarly APIs out-of-the-box, alongside mock/in-memory providers for local development and offline testing.

---

## 1. Provider Capabilities Matrix

| Provider | Identifier / Alias | Search | Forward Snowballing | Backward Snowballing | Key Features & Metadata |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **OpenAlex** | `openalex` |  |  |  | Global coverage, Open Access PDF/landing URLs, Work IDs (`W...`) |
| **Semantic Scholar** | `semanticscholar`, `s2`, `semantic_scholar` |  |  |  | AI-generated TLDRs, citation intents (`methodology`, `background`, `result`) |
| **Crossref** | `crossref` |  |  |  | Authoritative DOI registry, bibliographic reference matching |
| **arXiv** | `arxiv` |  |  |  | CS, Math, Physics preprints via Atom feed, arXiv IDs |
| **PubMed** | `pubmed` |  |  |  | Biomedical literature, PMIDs, MeSH (Medical Subject Headings) terms |
| **bioRxiv** | `biorxiv` |  |  |  | Life sciences and biomedical preprints |
| **In-Memory** | `memory` |  |  |  | Offline testing with static `Document` lists |
| **Local File** | `local_file` |  |  |  | Offline testing over local `.ris` or `.jsonl` files |

---

## 2. Configuration & Environment Variables

Settings are managed via `pydantic-settings` and can be loaded automatically from a `.env` file or system environment variables prefixed with `SCHOLAR_`:

| Environment Variable | Default | Purpose |
| :--- | :--- | :--- |
| `SCHOLAR_MAILTO` | `student@university.edu` | Email injected into request headers for Crossref and OpenAlex polite pool routing |
| `SCHOLAR_OPENALEX_KEY` | `None` | Optional OpenAlex Premium API key for higher rate limits |
| `SCHOLAR_S2_KEY` | `None` | Optional Semantic Scholar API key |
| `SCHOLAR_CACHE_DIR` | `.cache` | Local directory for storing SQLite HTTP cache |
| `SCHOLAR_CACHE_EXPIRE_DAYS` | `30` | Number of days cached HTTP responses remain valid |

### Default Rate Limits
- **OpenAlex**: 10.0 req/s
- **Crossref**: 5.0 req/s (with polite `mailto`)
- **Semantic Scholar**: 1.0 req/s (without API key)
- **PubMed**: 3.0 req/s (without API key)

---

## 3. Instantiating Providers in Python

```python
from scholar_search.providers import (
    OpenAlexProvider,
    SemanticScholarProvider,
    CrossrefProvider,
    ArxivProvider,
    PubMedProvider,
    BiorxivProvider,
    InMemoryProvider,
    LocalFileProvider,
)

# Live API providers
openalex = OpenAlexProvider()
s2 = SemanticScholarProvider()
crossref = CrossrefProvider()
arxiv = ArxivProvider()
pubmed = PubMedProvider()
biorxiv = BiorxivProvider()

# Offline / Testing providers
memory_provider = InMemoryProvider(documents=[...])
local_provider = LocalFileProvider(filepath="my_papers.ris")
```
