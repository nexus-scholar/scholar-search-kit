# API Reference

Technical documentation for developers integrating `scholar-search-kit` into custom Python pipelines and AI agent systems.

---

## `SearchEngine`

```python
from scholar_search import SearchEngine, Query
```

Orchestrates federated queries across multiple academic providers and handles deduplication and snowballing.

### `__init__(providers: Optional[List[SearchProvider]] = None)`
Initializes the engine. If `providers` is `None`, loads the default suite (`OpenAlex`, `SemanticScholar`, `Crossref`, `Arxiv`, `PubMed`, `Biorxiv`).

### `search_all(query: Query, dedup: bool = True) -> List[Document]`
Executes the query across all active providers concurrently/sequentially and returns a deduplicated list of `Document` models.

### `snowball_forward(document_id: str, provider_name: str) -> List[Document]`
Finds papers citing the specified document ID on the target provider.

### `snowball_backward(document_id: str, provider_name: str) -> List[Document]`
Finds references cited by the specified document ID on the target provider.

---

## `DocumentVerifier`

```python
from scholar_search import DocumentVerifier
```

Verifies the authenticity of citations to prevent LLM hallucinations and hydates missing metadata.

### `verify_document(doc: Document) -> Tuple[bool, Document, str]`
Checks if a document exists in Crossref/OpenAlex via DOI or bibliographic matching.

### `hydrate_metadata(doc: Document) -> Document`
Fills in missing abstracts, venues, authors, and citation counts using OpenAlex.

### `process_batch(documents: List[Document], verify: bool = True, enrich: bool = True) -> Tuple[List[Document], List[Dict]]`
Runs batch verification and hydration, returning processed documents alongside an audit report.

---

## `Deduplicator`

```python
from scholar_search import Deduplicator
```

Deterministic clustering and metadata merging.

### `deduplicate(documents: List[Document]) -> List[DocumentCluster]`
Clusters documents by DOI, arXiv ID, PubMed ID, OpenAlex ID, S2 ID, and conservative fuzzy title matching ($\ge 97\%$). Merges metadata into each cluster's representative.

### `get_statistics(clusters: List[DocumentCluster]) -> Dict[str, Union[int, float]]`
Calculates total documents, unique documents, duplicate count, and duplicate rate.

---

## `AcademicHttpClient`

```python
from scholar_search import AcademicHttpClient
```

Thread-safe, rate-limited HTTP client with SQLite response caching and exponential backoff retries.

### `get(url: str, params: Optional[Dict] = None, timeout: float = 30.0, **kwargs) -> requests.Response`
Executes a rate-limited, polite HTTP request.
