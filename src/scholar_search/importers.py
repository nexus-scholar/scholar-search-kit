"""Importers for reading local files into the normalized Document model."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .models import Author, Document, ExternalIds


class RISImporter:
    """Parses standard RIS academic citation files."""

    def parse(self, filepath: str | Path) -> Iterator[Document]:
        current_record: dict[str, Any] = {}
        authors: list[Author] = []

        with Path(filepath).open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # End of Record
                if line.startswith("ER  -") or line.startswith("ER  -"):
                    if current_record:
                        yield self._build_document(current_record, authors)
                        current_record = {}
                        authors = []
                    continue

                # Parse tag
                if len(line) >= 6 and line[2:6] == "  - ":
                    tag = line[:2]
                    value = line[6:].strip()

                    if tag == "AU":
                        parts = value.split(",")
                        if len(parts) > 1:
                            authors.append(
                                Author(
                                    family_name=parts[0].strip(),
                                    given_name=parts[1].strip(),
                                )
                            )
                        else:
                            authors.append(Author(family_name=value))
                    else:
                        current_record[tag] = value

            if current_record:
                yield self._build_document(current_record, authors)

    def _build_document(self, record: dict, authors: list[Author]) -> Document:
        ext_ids = ExternalIds()
        if "DO" in record:
            ext_ids.doi = record["DO"]

        year = None
        if "PY" in record:
            try:
                year = int(record["PY"][:4])
            except (ValueError, IndexError):
                pass
        elif "Y1" in record:
            try:
                year = int(record["Y1"][:4])
            except (ValueError, IndexError):
                pass

        doc = Document(
            title=record.get("TI") or record.get("T1") or "Unknown Title",
            year=year,
            provider="local_ris",
            external_ids=ext_ids,
            abstract=record.get("AB") or record.get("N2"),
            authors=authors,
            venue=record.get("JO") or record.get("JF") or record.get("T2"),
        )
        doc.mark_retrieved()
        return doc


class JSONImporter:
    """Parses standard JSON array files into Document models."""

    def parse(self, filepath: str | Path) -> Iterator[Document]:
        with Path(filepath).open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # If wrapped in a top-level key like {"results": [...]} or {"papers": [...]}
            for key in ("results", "papers", "documents", "data"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                data = [data]

        for item in data:
            if not isinstance(item, dict):
                continue

            # Parse external IDs
            ext_data = item.get("external_ids", {})
            if not ext_data:
                # Handle flat doi keys
                ext_ids = ExternalIds(
                    doi=item.get("doi"),
                    arxiv_id=item.get("arxiv_id"),
                    pubmed_id=item.get("pubmed_id"),
                    openalex_id=item.get("openalex_id"),
                    s2_id=item.get("s2_id"),
                )
            else:
                ext_ids = ExternalIds(**ext_data)

            # Parse authors
            authors = []
            for a in item.get("authors", []):
                if isinstance(a, dict):
                    authors.append(Author(**a))
                elif isinstance(a, str):
                    authors.append(Author(family_name=a))

            doc = Document(
                title=item.get("title") or "Untitled",
                year=item.get("year"),
                provider=item.get("provider", "local_json"),
                provider_id=item.get("provider_id", ""),
                external_ids=ext_ids,
                abstract=item.get("abstract"),
                authors=authors,
                venue=item.get("venue"),
                url=item.get("url"),
                citations_count=item.get("citations_count"),
                references_count=item.get("references_count"),
                citation_intents=item.get("citation_intents", []),
                mesh_terms=item.get("mesh_terms", []),
                tldr=item.get("tldr"),
                query_id=item.get("query_id"),
            )
            doc.mark_retrieved()
            yield doc


class JSONLImporter:
    """Parses JSONL files into Document models."""

    def parse(self, filepath: str | Path) -> Iterator[Document]:
        with Path(filepath).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)

                ext_ids = ExternalIds(**data.get("external_ids", {}))
                authors = [Author(**a) for a in data.get("authors", [])]

                doc = Document(
                    title=data["title"],
                    year=data.get("year"),
                    provider=data.get("provider", "local_jsonl"),
                    provider_id=data.get("provider_id", ""),
                    external_ids=ext_ids,
                    abstract=data.get("abstract"),
                    authors=authors,
                    venue=data.get("venue"),
                    url=data.get("url"),
                    citations_count=data.get("citations_count"),
                    references_count=data.get("references_count"),
                    citation_intents=data.get("citation_intents", []),
                    mesh_terms=data.get("mesh_terms", []),
                    tldr=data.get("tldr"),
                    query_id=data.get("query_id"),
                )
                doc.mark_retrieved()
                yield doc
