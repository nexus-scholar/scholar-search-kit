"""
Nexus Scholar Suite - Course Demo (API)
Module 02: Search & Discovery

This script demonstrates how to programmatically use the scholar-search-kit
to discover literature, deduplicate records, and verify citations.
"""

from pathlib import Path
from scholar_search import SearchEngine, Query, Exporter
from scholar_search.dedup import Deduplicator
from scholar_search.providers import OpenAlexProvider, ArxivProvider

def main():
    print("Initializing Search Engine...")
    # 1. Initialize the engine with specific providers
    engine = SearchEngine(providers=[OpenAlexProvider(), ArxivProvider()])

    # 2. Formulate a search query
    print("Querying for 'transformer attention mechanism' (2017+)...")
    query = Query(
        text="transformer attention mechanism",
        year_min=2017,
        max_results=15
    )

    # 3. Execute the search across all registered providers
    documents = engine.search_all(query)
    print(f"Found {len(documents)} raw documents across providers.")

    # 4. Deduplicate the results
    # This merges overlapping records (e.g., an arXiv preprint and its OpenAlex published version)
    print("Deduplicating records...")
    dedup = Deduplicator()
    dedup_docs = dedup.get_unique_documents(documents)
    print(f"Reduced to {len(dedup_docs)} unique documents.")

    # 5. Export for downstream processing
    output_path = Path("literature_review.json")
    print(f"Exporting to {output_path}...")
    Exporter().json(dedup_docs, output_path)

    print("Done! The exported JSON is ready for scholar-pdf-kit or scholar-rag-kit.")

if __name__ == "__main__":
    main()
