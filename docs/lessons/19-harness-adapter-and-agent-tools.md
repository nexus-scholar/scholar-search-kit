# Lesson 8.2: Agentic Skills & Multi-Tool Coordination (`.agents/skills/`)

## 1. Scientific Motivation & Context
In autonomous research workflows, AI coding agents and LLM research assistants discover, screen, and synthesize literature. Rather than generating unvetted synthetic citations or ad-hoc scripts, agents must follow formal **Agent Skills (`SKILL.md`)** that guide deterministic tool invocation, hallucination verification, and multi-package coordination.

---

## 2. Agent Skill Specification

* **Location**: `.agents/skills/scholar-search-kit/SKILL.md`
* **Agent Capabilities**:
  1. **Federated Literature Discovery**: Runs `scholar-search search` across OpenAlex, PubMed, Crossref, arXiv, Semantic Scholar, and bioRxiv.
  2. **Citation Snowballing**: Explores forward citing papers and backward reference graphs.
  3. **Verification & Anti-Hallucination**: Runs `scholar-search import --verify --enrich` to cross-check citations against Crossref's 150M records and flag phantom papers.
  4. **Downstream Handoff**: Exports normalized JSON arrays directly readable by `scholar-pdf-kit` (`scholar-pdf download --input results.json`).

---

## 3. Python API Integration for Agents

```python
from scholar_search import SearchEngine, DocumentVerifier, Exporter, Query

# 1. Federated Search & Deduplication
engine = SearchEngine(providers=["openalex", "crossref", "arxiv"])
query = Query(text="diffusion models in pathology", year_min=2022, max_results=20)
results = engine.search(query)

# 2. Verification
verifier = DocumentVerifier()
verified_docs = []
for doc in results:
    check = verifier.verify_document(doc)
    if check.is_verified:
        verified_docs.append(doc)

# 3. Export for scholar-pdf-kit
Exporter().json(verified_docs, "verified_literature.json")
```
