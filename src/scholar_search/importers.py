"""Importers for reading local files into the normalized Document model."""

import json
from pathlib import Path
from collections.abc import Iterator

from .models import Document, ExternalIds, Author


class RISImporter:
    """Parses standard RIS academic citation files."""

    def parse(self, filepath: str | Path) -> Iterator[Document]:
        current_record = {}
        authors = []
        
        with Path(filepath).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # End of Record
                if line.startswith("ER  -"):
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
                        # Simplistic author parsing for RIS (Last, First)
                        parts = value.split(",")
                        if len(parts) > 1:
                            authors.append(Author(family_name=parts[0].strip(), given_name=parts[1].strip()))
                        else:
                            authors.append(Author(family_name=value))
                    else:
                        current_record[tag] = value

    def _build_document(self, record: dict, authors: list[Author]) -> Document:
        ext_ids = ExternalIds()
        if "DO" in record:
            ext_ids.doi = record["DO"]
            
        year = None
        if "PY" in record:
            try:
                year = int(record["PY"])
            except ValueError:
                pass
                
        return Document(
            title=record.get("TI", "Unknown Title"),
            year=year,
            provider="local_ris",
            external_ids=ext_ids,
            abstract=record.get("AB"),
            authors=authors,
            venue=record.get("JO")
        )


class JSONLImporter:
    """Parses JSONL files created by our own exporter."""

    def parse(self, filepath: str | Path) -> Iterator[Document]:
        with Path(filepath).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                
                # Reconstruct models
                ext_ids = ExternalIds(**data.get("external_ids", {}))
                authors = [Author(**a) for a in data.get("authors", [])]
                
                yield Document(
                    title=data["title"],
                    year=data.get("year"),
                    provider=data.get("provider", "local_jsonl"),
                    provider_id=data.get("provider_id", ""),
                    external_ids=ext_ids,
                    abstract=data.get("abstract"),
                    authors=authors,
                    venue=data.get("venue"),
                    url=data.get("url"),
                    query_id=data.get("query_id")
                )
