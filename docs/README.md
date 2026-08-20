# Scholar Search Kit Documentation

This documentation suite guides the construction of an extensible, scientifically auditable Python scholarly search and literature organization toolkit. It recreates selected behavior from `strategy-pipeline/src/slr` as an independent package consumed by the tutorial harness.

---

## Status Model: Distinguishing Implementation Tiers

To prevent confusion between what is working today, what is built in upcoming lessons, and what exists only in the reference codebase, all documentation follows this 4-tier status model:

* **🟢 [Implemented v0.1.0]**: Working in the current codebase with passing unit and integration tests.
* **🟡 [Lesson Milestone]**: Target specification for upcoming AI-assisted construction lessons.
* **🔵 [Reference Architecture]**: Reference implementation in `strategy-pipeline/src/slr` used as architectural inspiration.
* **🟣 [Production Target]**: Long-term advanced enhancement (e.g. Specter2 semantic embeddings).

---

## Reference-to-Tutorial Target Mapping

| Component Area | Current Baseline (`v0.1.0`) | Target Module | Status | Lesson Spec |
| :--- | :--- | :--- | :--- | :--- |
| **External IDs** | `scholar_search.models.ExternalIds` | `models.py` | 🟢 Implemented | [Lesson 2.1](lessons/01-models-external-ids.md) |
| **Author & Document** | `scholar_search.models.Document` | `models.py` | 🟢 Implemented | [Lesson 2.2](lessons/02-models-author-document.md) |
| **Query Model** | `scholar_search.models.Query` | `models.py` | 🟢 Implemented | [Lesson 2.3](lessons/03-models-query.md) |
| **Document Cluster** | `scholar_search.models.DocumentCluster` | `models.py` | 🟢 Implemented | [Lesson 2.4](lessons/04-models-cluster.md) |
| **Exceptions** | `scholar_search.utils.exceptions` | `utils/exceptions.py` | 🟡 Lesson Target | [Lesson 3.1](lessons/05-utils-exceptions.md) |
| **Rate Limiting** | `scholar_search.utils.rate_limit` | `utils/rate_limit.py` | 🟡 Lesson Target | [Lesson 3.2](lessons/06-utils-rate-limiter.md) |
| **Exponential Retry** | `scholar_search.utils.retry` | `utils/retry.py` | 🟡 Lesson Target | [Lesson 3.3](lessons/07-utils-retry.md) |
| **Query Translator** | `scholar_search.providers.query_translator` | `providers/query_translator.py` | 🟡 Lesson Target | [Lesson 4.1](lessons/08-query-parser-translator.md) |
| **Normalizer** | `scholar_search.providers.normalizer` | `providers/normalizer.py` | 🟡 Lesson Target | [Lesson 4.2](lessons/09-normalization-subsystem.md) |
| **In-Memory Provider** | `scholar_search.providers.InMemoryProvider` | `providers.py` | 🟢 Implemented | [Lesson 5.1](lessons/10-providers-base-and-in-memory.md) |
| **OpenAlex Provider** | `scholar_search.providers.OpenAlexProvider` | `providers/openalex.py` | 🟡 Lesson Target | [Lesson 5.2](lessons/11-providers-openalex.md) |
| **Crossref Provider** | `scholar_search.providers.CrossrefProvider` | `providers/crossref.py` | 🟡 Lesson Target | [Lesson 5.3](lessons/12-providers-crossref.md) |
| **arXiv Provider** | `scholar_search.providers.ArxivProvider` | `providers/arxiv.py` | 🟡 Lesson Target | [Lesson 5.4](lessons/13-providers-arxiv.md) |
| **S2 Bulk Provider** | `scholar_search.providers.SemanticScholarProvider` | `providers/s2.py` | 🟡 Lesson Target | [Lesson 5.5](lessons/14-providers-semantic-scholar.md) |
| **Deduplicator** | `scholar_search.dedup.Deduplicator` (Baseline) | `dedup.py` | 🟢 Implemented (Baseline) / 🟡 4-Phase Target | [Lesson 6.1](lessons/15-dedup-conservative-strategy.md) |
| **CSV / JSONL Export** | `scholar_search.export.Exporter` | `export.py` | 🟢 Implemented | [Lesson 7.1](lessons/16-export-csv-jsonl.md) |
| **BibTeX Exporter** | `scholar_search.export.BibTeXExporter` | `export/bibtex_exporter.py` | 🟡 Lesson Target | [Lesson 7.2](lessons/17-export-bibtex.md) |
| **CLI Tooling** | `scholar_search.cli` (Baseline) | `cli.py` / `cli/` | 🟢 Implemented (Baseline) / 🟡 Command Suite | [Lesson 8.1](lessons/18-cli-tooling-and-manifests.md) |
| **Harness Adapter** | `harness.scholar_search_integration` | `harness/` | 🟢 Implemented | [Lesson 8.2](lessons/19-harness-adapter-and-agent-tools.md) |

---

## Core Documentation Files

* [**`component-specs.md`**](component-specs.md): Master technical specifications, mathematical formulas, status badges, and counterexamples.
* [**`ai-build-curriculum.md`**](ai-build-curriculum.md): 8-chapter AI construction curriculum with 7-step incremental checkpoints for provider modules.
* [**`video-series.md`**](video-series.md): Complete 5-season, 22-episode production plan.
* [**`lessons/`**](lessons/): Individual, focused specification documents and test contracts for each component.

---

## Architectural Boundary Rule

`scholar-search-kit` owns domain search, normalization, matching, and export logic. The `harness` owns pipeline orchestration, permissions, persistence, approval gates, and presentation. Neither package imports the other directly at runtime.
