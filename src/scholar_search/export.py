"""Deterministic exporters for normalized documents."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import Document


class Exporter:
    """Export documents to JSON, JSONL, CSV, or RIS without provider-specific logic."""

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
                title = re.sub(
                    r"\s+",
                    " ",
                    re.sub(r"<[^>]+>", "", html.unescape(document.title or "Untitled")),
                ).strip()
                venue = re.sub(
                    r"\s+",
                    " ",
                    re.sub(r"<[^>]+>", "", html.unescape(document.venue or "")),
                ).strip()
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

    @staticmethod
    def _determine_ris_type(doc: Document) -> str:
        """Determine RIS type based on document metadata."""
        venue = (doc.venue or "").lower()
        if "journal" in venue or "trans" in venue:
            return "JOUR"
        elif "conf" in venue:
            return "CONF"
        return "GEN"

    def ris(self, documents: list[Document], output_file: str | Path) -> Path:
        """Export documents as RIS (Tagged) format for Rayyan/Covidence/EndNote/Zotero."""
        path = Path(output_file)
        if path.suffix != ".ris":
            path = path.with_suffix(".ris")
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        for doc in documents:
            ris_type = self._determine_ris_type(doc)
            lines.append(f"TY  - {ris_type}")

            if doc.title:
                lines.append(f"TI  - {doc.title}")

            for author in doc.authors:
                family = author.family_name or ""
                given = author.given_name or ""
                if family or given:
                    lines.append(f"AU  - {family}, {given}")

            if doc.year:
                lines.append(f"PY  - {doc.year}")

            if doc.venue:
                if ris_type == "JOUR":
                    lines.append(f"JO  - {doc.venue}")
                else:
                    lines.append(f"T2  - {doc.venue}")

            if doc.abstract:
                lines.append(f"AB  - {doc.abstract}")

            if doc.external_ids.doi:
                lines.append(f"DO  - {doc.external_ids.doi}")

            if doc.url:
                lines.append(f"UR  - {doc.url}")

            if doc.external_ids.arxiv_id:
                lines.append(f"C1  - arXiv:{doc.external_ids.arxiv_id}")

            provider = "nexus-scholar"
            if doc.sources:
                provider = doc.sources[0].get("provider", "nexus-scholar")
            lines.append(f"DB  - {provider}")

            lines.append("ER  - ")
            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
        return path
