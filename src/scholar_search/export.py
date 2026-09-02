"""Deterministic exporters for normalized documents."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import Document


class Exporter:
    """Export documents to JSON, JSONL, or CSV without provider-specific logic."""

    def json(
        self, documents: list[Document], output_file: str | Path, indent: int = 2
    ) -> Path:
        """Export documents as a clean, standardized JSON array."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(doc) for doc in documents]
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=indent, default=str)
        return path

    def jsonl(self, documents: list[Document], output_file: str | Path) -> Path:
        """Export documents line-by-line as JSONL."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for document in documents:
                handle.write(json.dumps(asdict(document), default=str) + "\n")
        return path

    def csv(self, documents: list[Document], output_file: str | Path) -> Path:
        """Export core metadata to CSV."""
        import html
        import re

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "workspace_id",
                    "title",
                    "year",
                    "provider",
                    "doi",
                    "arxiv_id",
                    "pubmed_id",
                    "openalex_id",
                    "venue",
                    "citations_count",
                ],
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            for document in documents:
                title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(document.title or "Untitled"))).strip()
                venue = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(document.venue or ""))).strip()
                writer.writerow(
                    {
                        "workspace_id": document.workspace_id or "",
                        "title": title,
                        "year": document.year,
                        "provider": document.provider,
                        "doi": document.external_ids.doi or "",
                        "arxiv_id": document.external_ids.arxiv_id or "",
                        "pubmed_id": document.external_ids.pubmed_id or "",
                        "openalex_id": document.external_ids.openalex_id or "",
                        "venue": venue,
                        "citations_count": document.citations_count or 0,
                    }
                )
        return path
