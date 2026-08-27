from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from scholar_search.cli import app
from scholar_search.models import Document, ExternalIds

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scholarly literature search" in result.stdout
    assert "search" in result.stdout
    assert "import" in result.stdout
    assert "snowball" in result.stdout
    assert "dedup" in result.stdout


def test_cli_search(tmp_path: Path):
    output_file = tmp_path / "results.json"
    dummy_doc = Document(
        title="Attention Is All You Need",
        year=2017,
        provider="openalex",
        external_ids=ExternalIds(doi="10.5555/3295222.3295349"),
        citations_count=50000,
    )

    with patch("scholar_search.cli.SearchEngine.search_all", return_value=[dummy_doc]):
        result = runner.invoke(
            app,
            [
                "search",
                "transformer attention",
                "--provider",
                "openalex",
                "--limit",
                "5",
                "--output",
                str(output_file),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        assert "Attention Is All You Need" in result.stdout
        assert output_file.exists()


def test_cli_snowball(tmp_path: Path):
    output_file = tmp_path / "snowball.json"
    dummy_doc = Document(
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        year=2018,
        provider="openalex",
        external_ids=ExternalIds(doi="10.18653/v1/N19-1423"),
    )

    with patch(
        "scholar_search.cli.SearchEngine.snowball_forward", return_value=[dummy_doc]
    ):
        result = runner.invoke(
            app,
            [
                "snowball",
                "W2741809807",
                "--provider",
                "openalex",
                "--direction",
                "forward",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert "BERT" in result.stdout
        assert output_file.exists()


def test_cli_import_and_dedup(tmp_path: Path):
    input_file = tmp_path / "input.json"
    input_file.write_text(
        '[{"title": "Paper A", "doi": "10.1000/1"}, {"title": "Paper A", "doi": "10.1000/1"}]'
    )
    output_file = tmp_path / "deduped.json"

    # Test import command
    result_import = runner.invoke(
        app, ["import", str(input_file), "--output", str(output_file)]
    )
    assert result_import.exit_code == 0
    assert "Loaded 2 records" in result_import.stdout

    # Test dedup command
    result_dedup = runner.invoke(
        app, ["dedup", str(input_file), "--output", str(output_file)]
    )
    assert result_dedup.exit_code == 0
    assert "Unique documents: 1" in result_dedup.stdout
