"""Simple deterministic exporters for normalized documents."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import Document


class Exporter:
    """Export documents to CSV or JSONL without provider-specific logic."""

    def csv(self, documents: list[Document], output_file: str | Path) -> Path:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["title", "year", "provider", "doi"])
            writer.writeheader()
            for document in documents:
                writer.writerow({
                    "title": document.title,
                    "year": document.year,
                    "provider": document.provider,
                    "doi": document.external_ids.doi or "",
                })
        return path

    def jsonl(self, documents: list[Document], output_file: str | Path) -> Path:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for document in documents:
                handle.write(json.dumps(asdict(document), default=str) + "\n")
        return path