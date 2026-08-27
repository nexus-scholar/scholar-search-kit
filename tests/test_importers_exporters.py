from pathlib import Path

from scholar_search.export import Exporter
from scholar_search.importers import JSONImporter, JSONLImporter, RISImporter
from scholar_search.models import Author, Document, ExternalIds


def test_json_and_jsonl_export_import_roundtrip(tmp_path: Path):
    docs = [
        Document(
            title="Deep Learning Benchmark",
            year=2022,
            provider="test",
            external_ids=ExternalIds(doi="10.1000/182", arxiv_id="2201.00001"),
            abstract="A comprehensive study on neural networks.",
            authors=[Author(family_name="LeCun", given_name="Yann")],
            venue="ICLR",
            citations_count=450,
        )
    ]
    exporter = Exporter()

    # Test JSON
    json_path = tmp_path / "test.json"
    exporter.json(docs, json_path)
    imported_json = list(JSONImporter().parse(json_path))
    assert len(imported_json) == 1
    assert imported_json[0].title == docs[0].title
    assert imported_json[0].external_ids.doi == "10.1000/182"
    assert imported_json[0].citations_count == 450

    # Test JSONL
    jsonl_path = tmp_path / "test.jsonl"
    exporter.jsonl(docs, jsonl_path)
    imported_jsonl = list(JSONLImporter().parse(jsonl_path))
    assert len(imported_jsonl) == 1
    assert imported_jsonl[0].title == docs[0].title
    assert imported_jsonl[0].authors[0].family_name == "LeCun"

    # Test CSV
    csv_path = tmp_path / "test.csv"
    exporter.csv(docs, csv_path)
    assert csv_path.exists()
    assert "Deep Learning Benchmark" in csv_path.read_text(encoding="utf-8")


def test_ris_importer(tmp_path: Path):
    ris_content = """TY  - JOUR
TI  - The Mathematical Theory of Communication
AU  - Shannon, Claude E.
PY  - 1948
DO  - 10.1002/j.1538-7305.1948.tb01338.x
JO  - Bell System Technical Journal
AB  - Recent development of various methods of modulation...
ER  - 
"""
    ris_path = tmp_path / "shannon.ris"
    ris_path.write_text(ris_content, encoding="utf-8")

    imported = list(RISImporter().parse(ris_path))
    assert len(imported) == 1
    doc = imported[0]
    assert doc.title == "The Mathematical Theory of Communication"
    assert doc.year == 1948
    assert doc.external_ids.doi == "10.1002/j.1538-7305.1948.tb01338.x"
    assert len(doc.authors) == 1
    assert doc.authors[0].family_name == "Shannon"
    assert doc.authors[0].given_name == "Claude E."
