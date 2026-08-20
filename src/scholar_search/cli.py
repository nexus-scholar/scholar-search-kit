"""Small CLI proving the package can be used as a deterministic tool."""

import argparse

from .dedup import Deduplicator
from .models import Document, ExternalIds


def main() -> None:
    parser = argparse.ArgumentParser(prog="scholar-search")
    subparsers = parser.add_subparsers(dest="command", required=True)
    dedup = subparsers.add_parser("deduplicate")
    dedup.add_argument("titles", nargs="+")
    args = parser.parse_args()
    if args.command == "deduplicate":
        documents = [Document(title=title, external_ids=ExternalIds()) for title in args.titles]
        clusters = Deduplicator().deduplicate(documents)
        print(f"documents={len(documents)} unique={len(clusters)}")