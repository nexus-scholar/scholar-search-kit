# Lesson 5.4: Ingesting arXiv Preprints & Atom XML (`providers/arxiv.py`)

## 1. Scientific Motivation & Context
arXiv is the premier open-access repository for preprints in computer science, physics, mathematics, and quantitative biology. Crucially, arXiv preprints often appear months or years before formal journal publication. Ingesting arXiv requires handling Atom XML feeds, translating terms to arXiv field prefixes, respecting a 3 req/s limit, and observing a hard API offset cap ($start < 10,000$).

## 2. Reference Architecture Analysis
* **Reference Source**: `strategy-pipeline/src/slr/providers/arxiv.py`
* **API Details**:
  * Base URL: `https://export.arxiv.org/api/query` (Atom XML Feed).
  * Rate limit: 3 requests/sec (arXiv policy).
  * Pagination: Offset-based (`start=0, 100, 200...`, `max_results=100`).
  * Safety cap: Halts when `start >= 10000` or when `start >= opensearch:totalResults`.
  * XML Namespaces: `atom: http://www.w3.org/2005/Atom`, `arxiv: http://arxiv.org/schemas/atom`.

## 3. Explicit Component Contract

### Class Definition: `ArxivProvider`
* **Query Syntax Translation (`_build_search_query`)**:
  * If query contains field prefixes (`ti:`, `abs:`, `cat:`, `au:`), preserves syntax.
  * Otherwise, expands term $T$ into: `(ti:"T" OR abs:"T" OR all:"T")`.
* **XML Atom Parsing (`_normalize_response`)**:
  * Extracts title from `atom:title` (stripping internal line breaks).
  * Extracts abstract from `atom:summary`.
  * Extracts arXiv ID from `atom:id` using regex `arxiv\.org/abs/(\d+\.\d+)(?:v\d+)?`.
  * Extracts primary category from `arxiv:primary_category` $\rightarrow$ `venue = f"arXiv ({term})"`.
  * Extracts PDF link (`type="application/pdf"` or `title="pdf"`).
* **Client-Side Year Filtering**:
  * Post-filters parsed records against `query.year_min` and `query.year_max` based on `int(atom:published[:4])`.

## 4. Verification & Falsifying Tests

```python
import xml.etree.ElementTree as ET
from scholar_search.providers.arxiv import ArxivProvider
from scholar_search.core.config import ProviderConfig

def test_arxiv_xml_entry_parsing():
    provider = ArxivProvider(ProviderConfig())
    xml_data = """
    <entry xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
        <id>http://arxiv.org/abs/2301.00001v1</id>
        <title>Attention Is All You Need In Practice</title>
        <summary>A comprehensive study on transformers.</summary>
        <published>2023-01-01T00:00:00Z</published>
        <author><name>Ashish Vaswani</name></author>
        <arxiv:primary_category term="cs.CL"/>
    </entry>
    """
    entry = ET.fromstring(xml_data)
    doc = provider._normalize_response(entry)
    
    assert doc is not None
    assert doc.title == "Attention Is All You Need In Practice"
    assert doc.external_ids.arxiv_id == "2301.00001"
    assert doc.year == 2023
    assert doc.venue == "arXiv (cs.CL)"
    assert doc.authors[0].family_name == "Vaswani"
```

## 5. AI Build Prompt

```text
Implement ArxivProvider in scholar_search/providers/arxiv.py following Lesson 5.4.
Support Atom XML parsing, search query field expansion, offset pagination with the 10k offset cap, client-side year filtering, and PDF link resolution.
Add mock-based unit tests in tests/test_arxiv.py.
```
