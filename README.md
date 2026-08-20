# Scholar Search Kit

`scholar-search-kit` is a tutorial project for building a modular, extensible Python scholarly literature search tool. It recreates selected behavior from `strategy-pipeline/src/slr` without copying the reference implementation.

The name comes from the reference project, but the toolkit is intentionally broader than strict systematic literature reviews. It supports exploratory research, scoping reviews, thesis preparation, citation discovery, background research, evidence mapping, and research landscape analysis.

## What It Is

Scholar Search Kit helps a researcher search, normalize, compare, deduplicate, and export scholarly documents. It is a search and evidence-gathering toolkit, not a rigid review methodology.

The user decides the research method. Scholar Search Kit provides reusable technical capabilities:

- search queries and filter boundaries;
- provider adapters (deterministic in-memory baseline, expanding to external APIs);
- normalized document records;
- persistent identifier and conservative title matching;
- provenance and retrieval metadata;
- portable exports for later reading, screening, or citation management.

## Example Uses

| Research Task | How Scholar Search Kit Helps |
| :--- | :--- |
| **Scoping review** | Gather a broad, traceable set of literature and inspect themes. |
| **Thesis preparation** | Find foundational papers, related work, and citation chains. |
| **Article writing** | Discover sources for an introduction, discussion, or background section. |
| **Systematic review** | Support repeatable searches, deduplication, and export as part of a larger protocol. |
| **Research mapping** | Compare topics, years, venues, providers, and clusters. |
| **Evidence update** | Re-run a saved query and compare new results with an earlier snapshot. |

## Implementation Status & Architecture

To avoid ambiguity during AI-assisted development and human learning, the project explicitly separates **current baseline code** from **tutorial milestone targets** and **reference architecture**:

| Component Area | Current Baseline (`v0.1.0`) | Tutorial Lesson Target | Reference Source (`strategy-pipeline/src/slr`) |
| :--- | :--- | :--- | :--- |
| **Core Models** | `Document`, `Author`, `ExternalIds` (DOI/arXiv/PMID), `Query`, `DocumentCluster` | Extended IDs (`openalex_id`, `s2_id`), cited counts, `SearchResult` | `core/models.py` |
| **Providers** | `InMemoryProvider`, `SearchProvider` protocol | `OpenAlexProvider`, `CrossrefProvider`, `ArxivProvider`, `SemanticScholarProvider` | `providers/` |
| **Resilience & Rate Limits** | Basic in-memory execution | `TokenBucket`, `SlidingWindow`, `@retry_with_backoff`, `SLRException` | `utils/` |
| **Deduplication** | Exact DOI + exact arXiv + fuzzy title ($\ge 0.97$) | 4-phase conservative strategy, year-gap filter, representative scoring tuple | `dedup/` |
| **Export Subsystem** | `CSVExporter`, `JSONLExporter` | `BibTeXExporter` (cite keys, LaTeX escaping), `JSONExporter`, RIS | `export/` |
| **CLI & Manifests** | `scholar-search deduplicate ...` | Subcommands (`search`, `deduplicate`, `export`), `SearchManifest`, PRISMA export | `cli/` |
| **Harness Adapter** | `DeduplicateDocumentsStage` | Agent tool permissions, MCP adapter | `harness/` |

## Install Locally

```powershell
uv pip install -e .
```

## Run Tests

```powershell
pytest
```

## Documentation & Learning Path

- [**docs/README.md**](docs/README.md): Project overview, boundaries, and reference-to-tutorial mappings.
- [**docs/component-specs.md**](docs/component-specs.md): Full component contracts, invariants, status badges, and counterexamples.
- [**docs/ai-build-curriculum.md**](docs/ai-build-curriculum.md): 8-chapter AI-assisted construction curriculum with staged checkpoint tasks.
- [**docs/video-series.md**](docs/video-series.md): 5-season 22-episode production roadmap.
- [**docs/lessons/**](docs/lessons/): Individual lesson specifications and verification tests for each component.
