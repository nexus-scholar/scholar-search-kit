from pathlib import Path
from typer.testing import CliRunner

from scholar_search.cli import app
from scholar_search.protocol_adapter import compile_protocol_search

runner = CliRunner()


def test_compile_protocol_search_minimal_dict():
    protocol_dict = {
        "protocol_id": "proto-test-01",
        "search_strategy": {
            "core_concepts": [
                {
                    "concept": "Code Generation",
                    "synonyms": ["code synthesis", "program synthesis"],
                    "boolean_operator": "OR",
                },
                {
                    "concept": "Evaluation",
                    "synonyms": ["benchmarks"],
                    "boolean_operator": "OR",
                },
            ],
            "date_range": {
                "start_year": 2021,
                "end_year": 2025,
            },
            "languages": ["en"],
            "target_candidate_pool_size": {
                "min": 50,
                "max": 300,
            },
            "target_databases": ["openalex", "arxiv"],
        },
    }

    query, providers = compile_protocol_search(protocol_dict)

    assert query.id == "proto-test-01"
    assert '("Code Generation" OR "code synthesis" OR "program synthesis")' in query.text
    assert "(Evaluation OR benchmarks)" in query.text
    assert " AND " in query.text
    assert query.year_min == 2021
    assert query.year_max == 2025
    assert query.max_results == 300
    assert providers == ["openalex", "arxiv"]


def test_compile_protocol_search_valid_fixture(tmp_path: Path):
    fixture_json = """{
      "protocol_id": "proto-ds-01",
      "metadata": {"title": "Test Title"},
      "search_strategy": {
        "core_concepts": [
          {
            "concept": "Quantum",
            "synonyms": []
          }
        ],
        "date_range": {"start_year": 2020, "end_year": 2024},
        "target_databases": ["crossref"]
      }
    }"""
    file_path = tmp_path / "protocol.json"
    file_path.write_text(fixture_json, encoding="utf-8")

    query, providers = compile_protocol_search(file_path)
    assert query.text == "Quantum"
    assert query.year_min == 2020
    assert query.year_max == 2024
    assert providers == ["crossref"]


def test_cli_search_with_protocol_option(tmp_path: Path):
    fixture_json = """{
      "protocol_id": "proto-ds-01",
      "metadata": {"title": "Test Title"},
      "search_strategy": {
        "core_concepts": [{"concept": "attention"}],
        "date_range": {"start_year": 2017, "end_year": 2020},
        "target_databases": []
      }
    }"""
    file_path = tmp_path / "protocol.json"
    file_path.write_text(fixture_json, encoding="utf-8")

    # If target_databases is empty, cli falls back to default suite
    # We pass an invalid provider so search returns quickly without network
    result = runner.invoke(app, ["search", "--protocol", str(file_path), "--provider", "nonexistent"])
    assert result.exit_code != 0
    assert "Unknown provider" in result.output
