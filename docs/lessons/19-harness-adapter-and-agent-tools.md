# Lesson 8.2: Harness Adapter & Agent Tool Execution (`harness/`)

## 1. Scientific Motivation & Context
In an agentic research environment, AI models must be capable of discovering and invoking literature search and deduplication tools safely. However, the search domain package (`scholar-search-kit`) must remain decoupled from the workflow harness (`harness`). The harness defines stage adapters, permission classes (read-only vs side-effecting), and approval gates.

## 2. Reference Architecture Analysis
* **Reference Sources**:
  * `harness/scholar_search_integration.py`
  * `tests/test_harness_scholar_search_integration.py`
* **Components**:
  * `DeduplicateDocumentsStage`: Injects harness persistence and wraps `scholar_search.dedup.Deduplicator`.
  * `StageResult`: Standard container returning `stage_name`, `artifact: dict`, and `metadata: dict`.

## 3. Explicit Component Contract

### Class Definition: `DeduplicateDocumentsStage`
* **Module**: `harness.scholar_search_integration`
* **Methods**:
  * `__init__(persistence: Any)`: Receives injected persistence service.
  * `execute(*, project_id: str, documents: List[Document]) -> StageResult`:
    * Runs `Deduplicator().deduplicate(documents)`.
    * Creates artifact containing `project_id`, `cluster_count`, `document_count`, and representative titles.
    * Returns `StageResult(stage_name="deduplicate-documents", artifact=artifact, metadata={"package": "scholar-search-kit", "strategy": "conservative"})`.

### Tool Permission & Side-Effect Classification
| Tool Name | Operation | Side Effect | Agent Approval Required |
| :--- | :--- | :--- | :--- |
| `search_validate_query` | Query syntax check | None | No |
| `search_run_provider` | Network search | Read / Network | Policy-dependent |
| `search_deduplicate` | Cluster records | Local memory | No |
| `search_export_results` | Write files | Local File I/O | Policy-dependent |

## 4. Verification & Falsifying Tests

```python
from harness.runner import Harness
from harness.services import JsonFilePersistence
from harness.scholar_search_integration import DeduplicateDocumentsStage
from scholar_search.models import Document, ExternalIds

def test_harness_stage_adapter(tmp_path):
    harness = Harness(JsonFilePersistence(tmp_path))
    harness.register("deduplicate-documents", DeduplicateDocumentsStage)
    
    docs = [
        Document("A Study", external_ids=ExternalIds(doi="10.1/abc")),
        Document("A Study", external_ids=ExternalIds(doi="https://doi.org/10.1/ABC")),
    ]
    
    result = harness.run("deduplicate-documents", "proj-1", documents=docs)
    
    assert result.artifact["cluster_count"] == 1
    assert result.artifact["document_count"] == 2
    assert result.metadata["package"] == "scholar-search-kit"
```

## 5. AI Build Prompt

```text
Implement DeduplicateDocumentsStage in harness/scholar_search_integration.py according to Lesson 8.2 specifications.
Ensure proper stage execution, artifact creation, metadata assignment, and full isolation from scholar-search internal state.
Add unit tests in tests/test_harness_scholar_search_integration.py.
```
