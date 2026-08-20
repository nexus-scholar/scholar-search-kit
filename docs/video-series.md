# Scholar Search Kit Video Series

## Building a Reproducible Scholarly Search Toolkit with AI

This series teaches how to build a modular, extensible, and scientifically auditable scholarly search toolkit in Python from first principles, inspired by `strategy-pipeline/src/slr`.

The toolkit supports exploratory research, scoping reviews, dissertation research, citation discovery, background evidence mapping, and systematic literature reviews (SLR) without coupling research methodology to code execution.

---

## Series Structure Overview

The series is structured into **5 seasons** spanning **23 episodes**:

```mermaid
flowchart LR
    S1[Season 1: Foundation & Contracts<br/>Episodes 0-3] --> S2[Season 2: Data Models & Resilience<br/>Episodes 4-8]
    S2 --> S3[Season 3: Providers & Ingestion<br/>Episodes 9-14]
    S3 --> S4[Season 4: Matching & Export<br/>Episodes 15-18]
    S4 --> S5[Season 5: CLI, Harness & AI<br/>Episodes 19-22]
```

| Season | Episodes | Focus Area | Key Deliverable |
| :--- | :--- | :--- | :--- |
| **Season 1: Foundation & Contracts** | 0 – 3 | System boundary, reference archaeology, project scaffolding | Core package skeleton & contracts map |
| **Season 2: Data Models & Resilience** | 4 – 8 | Normalized models, token bucket rate limiter, exponential retry, exceptions | Typed models & offline resilient utility suite |
| **Season 3: Providers & Ingestion** | 9 – 14 | In-memory engine, OpenAlex, Crossref, arXiv, Semantic Scholar, query lexer | Provider ingestion specifications and deterministic fixtures |
| **Season 4: Matching & Export** | 15 – 18 | Conservative deduplication, representative scoring, CSV/JSONL, BibTeX | Provenance-preserving deduplication & export |
| **Season 5: CLI, Harness & AI** | 19 – 22 | Unified CLI, run/search manifests, harness stage adapter, MCP tools | Full agentic capability & end-to-end demo |

---

## Detailed Episode Plan

| Ep # | Episode Title | Focus & Component | Lesson Spec Document |
| :--- | :--- | :--- | :--- |
| **0** | *Why Build a Scholarly Search Tool?* | Scientific need, auditability, separating search mechanics from research methods | [docs/README.md](README.md) |
| **1** | *Reading `src/slr` as a Clean Contract* | Architectural archaeology, mapping models, providers, dedup, and export | [docs/component-specs.md](component-specs.md) |
| **2** | *Clean-Room Package Architecture* | `pyproject.toml`, package layout, `uv` dependency management, no cyclic imports | [docs/component-specs.md](component-specs.md#2-system-architecture-overview) |
| **3** | *Persistent Identifiers (`ExternalIds`)* | DOI regex stripping, arXiv ID, PMID, OpenAlex ID, S2 ID normalization | [lessons/01-models-external-ids.md](lessons/01-models-external-ids.md) |
| **4** | *The Normalized Document & Author Model* | `Author`, `Document`, `SearchResult`, UTC timestamps, provenance fields | [lessons/02-models-author-document.md](lessons/02-models-author-document.md) |
| **5** | *Query as a Research Instrument* | `Query` model, filter bounds, language codes, stable query IDs | [lessons/03-models-query.md](lessons/03-models-query.md) |
| **6** | *Clusters & Duplicate Aggregation* | `DocumentCluster`, confidence metrics, multi-provider counts, non-destructive merges | [lessons/04-models-cluster.md](lessons/04-models-cluster.md) |
| **7** | *Exception Hierarchy for Resilient Search* | `SearchException`, `ProviderError`, `RateLimitError`, `NetworkError`, `AuthenticationError` | [lessons/05-utils-exceptions.md](lessons/05-utils-exceptions.md) |
| **8** | *Rate Limiting with Token Buckets* | `TokenBucket`, burst capacity, continuous refill, `SlidingWindowRateLimiter` | [lessons/06-utils-rate-limiter.md](lessons/06-utils-rate-limiter.md) |
| **9** | *Exponential Backoff & Rate Limit Retries* | `@retry_with_backoff`, `@retry_on_rate_limit`, dynamic HTTP 429 `Retry-After` handling | [lessons/07-utils-retry.md](lessons/07-utils-retry.md) |
| **10** | *Query Lexing & Translation* | `QueryParser`, `QueryToken`, `SimpleQueryTranslator`, `BooleanQueryTranslator` | [lessons/08-query-parser-translator.md](lessons/08-query-parser-translator.md) |
| **11** | *Response Normalization Subsystem* | `FieldExtractor`, `AuthorParser`, `DateParser`, `IDExtractor`, `ResponseNormalizer` | [lessons/09-normalization-subsystem.md](lessons/09-normalization-subsystem.md) |
| **12** | *The Provider Protocol & In-Memory Engine* | `SearchProvider` Protocol, `BaseProvider`, `InMemoryProvider`, `ProviderRegistry` | [lessons/10-providers-base-and-in-memory.md](lessons/10-providers-base-and-in-memory.md) |
| **13** | *Ingesting OpenAlex at Scale* | REST API, cursor pagination, polite pool `mailto`, inverted index abstract decompression | [lessons/11-providers-openalex.md](lessons/11-providers-openalex.md) |
| **14** | *Ingesting Crossref DOIs & Metadata* | REST API, deep cursor pagination, polite pool `mailto`, `issued.date-parts` parsing | [lessons/12-providers-crossref.md](lessons/12-providers-crossref.md) |
| **15** | *Ingesting arXiv Preprints & Atom XML* | Atom XML namespaces, field query expansion, 10k offset cap, client-side year filtering | [lessons/13-providers-arxiv.md](lessons/13-providers-arxiv.md) |
| **16** | *Ingesting Semantic Scholar Bulk Search* | Bulk API, continuation tokens, Boolean operator rewriting (`AND` $\rightarrow$ `+`, `OR` $\rightarrow$ `&#124;`) | [lessons/14-providers-semantic-scholar.md](lessons/14-providers-semantic-scholar.md) |
| **17** | *4-Phase Conservative Deduplication* | Exact DOI index $\rightarrow$ exact arXiv $\rightarrow$ fuzzy title ($\ge 97\%$) + year gap | [lessons/15-dedup-conservative-strategy.md](lessons/15-dedup-conservative-strategy.md) |
| **18** | *Representative Selection & Metrics* | Canonical document scoring tuple, duplicate rate, cluster distribution | [lessons/15-dedup-conservative-strategy.md](lessons/15-dedup-conservative-strategy.md#2-implementation-tiers) |
| **19** | *Exporting to CSV, JSON & JSONL* | `BaseExporter`, `CSVExporter` (flattened/clusters), `JSONLExporter` (streaming/nested) | [lessons/16-export-csv-jsonl.md](lessons/16-export-csv-jsonl.md) |
| **20** | *Exporting to BibTeX for Citation Managers* | `BibTeXExporter`, cite key generation (`FirstAuthorYYYYKeyword`), LaTeX escaping | [lessons/17-export-bibtex.md](lessons/17-export-bibtex.md) |
| **21** | *The CLI as an Agent Tool & Manifests* | `init`, `search`, `deduplicate`, `export`, `metadata.json`, `prisma_counts.json` | [lessons/18-cli-tooling-and-manifests.md](lessons/18-cli-tooling-and-manifests.md) |
| **22** | *Harness Adapter & Agent Tool Execution* | `DeduplicateDocumentsStage`, permissions, approval gates, MCP runtime | [lessons/19-harness-adapter-and-agent-tools.md](lessons/19-harness-adapter-and-agent-tools.md) |

---

## Recording Checklist for Each Episode

1. **Reference Check**: Display the corresponding module in `strategy-pipeline/src/slr/` to establish reference behavior.
2. **Contract First**: Review the specific lesson spec document in `docs/lessons/`.
3. **Counterexample Demonstration**: Run a failing test demonstrating a naive implementation edge case.
4. **Implementation & Proof**: Implement the component and run the focused `pytest` suite.
5. **No Credentials Needed**: Demonstrate execution using deterministic mocks or in-memory fixtures.
6. **Artifact Inspection**: Inspect the generated files, JSONL outputs, or manifests in the artifact viewer.
