import json
from pathlib import Path
from typer.testing import CliRunner

from scholar_search.cli import app
from scholar_search.models import Document, ExternalIds
from scholar_search.screening import (
    ScreeningDecision,
    batch_partition,
    evaluate_heuristic_screening,
    generate_batch_screening_prompt,
    partition_screening_results,
)

runner = CliRunner()


def test_batch_partition():
    docs = [Document(title=f"Paper {i}", workspace_id=f"SCI-{i:06d}") for i in range(125)]
    batches = batch_partition(docs, batch_size=50)
    assert len(batches) == 3
    assert len(batches[0]) == 50
    assert len(batches[1]) == 50
    assert len(batches[2]) == 25


def test_generate_batch_screening_prompt():
    protocol_data = {
        "research_questions": [{"id": "RQ1", "text": "How does RAG improve factual accuracy?"}],
        "screening_criteria": {
            "inclusion": [{"id": "INC-01", "criterion": "Evaluates RAG models on benchmarks"}],
            "exclusion": [{"id": "EXC-01", "criterion": "Non-English studies", "reason_category": "LANGUAGE"}],
        },
    }
    docs = [
        Document(
            title="Grounded RAG",
            workspace_id="SCI-000001",
            year=2024,
            abstract="Empirical evaluation on HotpotQA.",
        )
    ]
    prompt = generate_batch_screening_prompt(docs, protocol_data)

    assert "**RQ1**: How does RAG improve factual accuracy?" in prompt
    assert "**INC-01**: Evaluates RAG models on benchmarks" in prompt
    assert "**EXC-01** (LANGUAGE): Non-English studies" in prompt
    assert "SCI-000001" in prompt


def test_screening_and_prisma_reporting(tmp_path: Path):
    protocol_data = {
        "research_questions": [{"id": "RQ1", "text": "Code generation benchmarks"}],
        "screening_criteria": {
            "inclusion": [{"id": "INC-01", "criterion": "Paper presents code generation artifact"}],
            "exclusion": [{"id": "EXC-01", "criterion": "Opinion papers", "reason_category": "opinion"}],
        },
    }

    doc_inc = Document(
        title="Novel Code Generation Synthesis",
        abstract="We present an artifact for python code synthesis.",
        workspace_id="SCI-000001",
        external_ids=ExternalIds(doi="10.1000/1"),
    )
    doc_exc = Document(
        title="An Opinion on AI",
        abstract="An opinion editorial on AI progress.",
        workspace_id="SCI-000002",
        external_ids=ExternalIds(doi="10.1000/2"),
    )

    dec_inc = evaluate_heuristic_screening(doc_inc, protocol_data)
    dec_exc = evaluate_heuristic_screening(doc_exc, protocol_data)

    assert dec_inc.decision == "INCLUDE"
    assert dec_exc.decision == "EXCLUDE"

    included, excluded, conflicts, report = partition_screening_results(
        [doc_inc, doc_exc], [dec_inc, dec_exc], total_identified=10, duplicates_removed=2
    )

    assert len(included) == 1
    assert len(excluded) == 1
    assert report.total_identified == 10
    assert report.duplicates_removed == 2
    assert report.records_screened == 2
    assert report.records_included == 1
    assert report.records_excluded == 1

    md = report.to_markdown()
    assert "# PRISMA 2020 Literature Screening Flow Report" in md
    assert "**Total Records Identified (Federated Search)**: `10`" in md
    assert "**Records Eligible for Full-Text Retrieval**: `1" in md


def test_cli_screen_command(tmp_path: Path):
    candidates_file = tmp_path / "deduped.json"
    protocol_file = tmp_path / "protocol.json"
    output_dir = tmp_path / "literature"

    candidates_data = [
        {
            "workspace_id": "SCI-000001",
            "title": "Code Generation Benchmark",
            "year": 2023,
            "provider": "openalex",
            "external_ids": {"doi": "10.1000/1"},
            "abstract": "Empirical artifact evaluation of code synthesis.",
        }
    ]
    with open(candidates_file, "w", encoding="utf-8") as f:
        json.dump(candidates_data, f)

    protocol_data = {
        "research_questions": [{"id": "RQ1", "text": "Code generation"}],
        "screening_criteria": {
            "inclusion": [{"id": "INC-01", "criterion": "Code generation artifact"}],
            "exclusion": [],
        },
    }
    with open(protocol_file, "w", encoding="utf-8") as f:
        json.dump(protocol_data, f)

    result = runner.invoke(
        app,
        ["screen", "--input", str(candidates_file), "--protocol", str(protocol_file), "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "included.json").exists()
    assert (output_dir / "excluded.json").exists()
    assert (output_dir / "prisma_screening_report.md").exists()
