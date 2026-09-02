"""Command Line Interface for scholar-search-kit."""

import asyncio
import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Reconfigure stdout/stderr for UTF-8 on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from .dedup import Deduplicator
from .engine import SearchEngine
from .export import Exporter
from .importers import JSONImporter, JSONLImporter, RISImporter
from .models import Document, Query
from .providers import (
    ArxivProvider,
    BiorxivProvider,
    CrossrefProvider,
    OpenAlexProvider,
    PubMedProvider,
    SemanticScholarProvider,
)
from .verifier import DocumentVerifier

app = typer.Typer(
    name="scholar-search",
    help="Scholarly literature search, deduplication, verification, and export toolkit.",
    add_completion=False,
)
console = Console(soft_wrap=True)
logging.basicConfig(level=logging.WARNING)


def _get_provider_instance(name: str):
    name_clean = name.lower().strip()
    if name_clean == "openalex":
        return OpenAlexProvider()
    elif name_clean in ("s2", "semanticscholar", "semantic_scholar"):
        return SemanticScholarProvider()
    elif name_clean == "crossref":
        return CrossrefProvider()
    elif name_clean == "arxiv":
        return ArxivProvider()
    elif name_clean == "pubmed":
        return PubMedProvider()
    elif name_clean == "biorxiv":
        return BiorxivProvider()
    else:
        raise typer.BadParameter(
            f"Unknown provider '{name}'. Options: openalex, crossref, pubmed, arxiv, semanticscholar, biorxiv"
        )


def _save_output(documents: list[Document], output_path: Path, format_str: str) -> None:
    exporter = Exporter()
    format_clean = format_str.lower().strip()
    if format_clean == "json":
        exporter.json(documents, output_path)
    elif format_clean == "jsonl":
        exporter.jsonl(documents, output_path)
    elif format_clean == "csv":
        exporter.csv(documents, output_path)
    else:
        raise typer.BadParameter(
            f"Unsupported format '{format_str}'. Options: json, jsonl, csv"
        )
    console.print(
        f"[green]Saved {len(documents)} documents to {output_path} ({format_clean.upper()})[/green]"
    )


def _clean_str(text: str) -> str:
    """Safely normalizes problematic Unicode characters for standard console display."""
    return text.replace("\u2010", "-").replace("\u2013", "-").replace("\u2014", "--")


def _display_documents_table(
    documents: list[Document], title: str = "Search Results"
) -> None:
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Year", style="dim", width=6)
    table.add_column("Title", style="bold", min_width=30, max_width=60)
    table.add_column("Provider", width=12)
    table.add_column("DOI / ID", style="cyan", min_width=20)
    table.add_column("Citations", justify="right", width=10)

    for doc in documents[:25]:
        doi_or_id = (
            doc.external_ids.doi
            or doc.external_ids.arxiv_id
            or doc.external_ids.pubmed_id
            or doc.provider_id
            or "N/A"
        )
        cites = str(doc.citations_count) if doc.citations_count is not None else "-"
        year = str(doc.year) if doc.year else "N/A"
        clean_title = _clean_str(doc.title)
        table.add_row(year, clean_title, doc.provider, doi_or_id, cites)

    console.print(table)
    if len(documents) > 25:
        console.print(f"[dim]... and {len(documents) - 25} more documents.[/dim]")


from .protocol_adapter import compile_protocol_search


@app.command()
def search(
    query_text: str | None = typer.Argument(
        None, help="Search query (e.g. 'machine learning AND transformer')"
    ),
    protocol: Path | None = typer.Option(
        None, "--protocol", "-P", help="Path to protocol.json to drive search strategy"
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Specific provider (openalex, crossref, pubmed, arxiv, semanticscholar, biorxiv) or all",
    ),
    limit: int | None = typer.Option(
        None, "--limit", "-l", help="Maximum documents to retrieve"
    ),
    year_min: int | None = typer.Option(
        None, "--year-min", help="Earliest publication year"
    ),
    year_max: int | None = typer.Option(
        None, "--year-max", help="Latest publication year"
    ),
    dedup: bool = typer.Option(
        True, "--dedup/--no-dedup", help="Automatically cluster and deduplicate results"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Filepath to save results"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, jsonl, csv"
    ),
):
    """Search scholarly literature across multiple academic APIs."""
    target_providers = None

    if protocol:
        proto_query, proto_providers = compile_protocol_search(protocol)
        search_str = query_text or proto_query.text
        y_min = year_min if year_min is not None else proto_query.year_min
        y_max = year_max if year_max is not None else proto_query.year_max
        max_docs = limit if limit is not None else (proto_query.max_results or 100)
        target_providers = proto_providers
    elif query_text:
        search_str = query_text
        y_min = year_min
        y_max = year_max
        max_docs = limit if limit is not None else 20
    else:
        raise typer.BadParameter(
            "Must provide either a query string argument or a --protocol (-P) path."
        )

    q = Query(text=search_str, max_results=max_docs, year_min=y_min, year_max=y_max)

    async def run_search():
        if provider:
            providers = [_get_provider_instance(provider)]
        elif target_providers:
            providers = []
            for p_name in target_providers:
                try:
                    providers.append(_get_provider_instance(p_name))
                except Exception as e:
                    logger.warning(f"Could not instantiate provider '{p_name}': {e}")
            if not providers:
                providers = [OpenAlexProvider(), SemanticScholarProvider(), CrossrefProvider(), ArxivProvider()]
        else:
            providers = [
                OpenAlexProvider(),
                SemanticScholarProvider(),
                CrossrefProvider(),
                ArxivProvider(),
                PubMedProvider(),
            ]

        engine = SearchEngine(providers=providers)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Create a task for the overall orchestration
            main_task = progress.add_task(
                description=f"Querying academic providers for '{search_str}'...", total=None
            )

            task_map = {}

            def update_progress(provider_name: str, count: int):
                if provider_name not in task_map:
                    task_map[provider_name] = progress.add_task(
                        description=f"  {provider_name}: fetching...", total=None
                    )
                progress.update(task_map[provider_name], description=f"  {provider_name}: {count} docs")

            res = await engine.search_all(q, dedup=dedup, progress_callback=update_progress)
            await engine.close()
            return res

    results = asyncio.run(run_search())

    _display_documents_table(results, title=f"Search Results for: '{search_str}'")

    if output:
        _save_output(results, output, format)



@app.command()
def snowball(
    doc_id: str = typer.Argument(
        ...,
        help="Target document ID (e.g. OpenAlex ID like 'W2741809807' or Semantic Scholar Paper ID)",
    ),
    provider: str = typer.Option(
        "openalex",
        "--provider",
        "-p",
        help="Provider for snowballing (openalex, semanticscholar, pubmed)",
    ),
    direction: str = typer.Option(
        "forward",
        "--direction",
        "-d",
        help="Snowball direction: forward (citing papers) or backward (references)",
    ),
    limit: int = typer.Option(
        25, "--limit", "-l", help="Maximum citations/references to retrieve"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Filepath to save results"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, jsonl, csv"
    ),
):
    """Perform citation snowballing (forward citations or backward references)."""
    async def run_snowball():
        if provider:
            providers = [_get_provider_instance(provider)]
        else:
            providers = [OpenAlexProvider(), SemanticScholarProvider()]

        engine = SearchEngine(providers=providers)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task_map = {}

            def update_progress(provider_name: str, count: int):
                if provider_name not in task_map:
                    task_map[provider_name] = progress.add_task(
                        description=f"  {provider_name}: fetching...", total=None
                    )
                progress.update(task_map[provider_name], description=f"  {provider_name}: {count} docs")

            if direction.lower() == "forward":
                progress.add_task(
                    description=f"Finding papers citing {doc_id} on {provider}...",
                    total=None,
                )
                res = await engine.snowball_forward(doc_id, provider, progress_callback=update_progress)
            elif direction.lower() == "backward":
                progress.add_task(
                    description=f"Finding references cited by {doc_id} on {provider}...",
                    total=None,
                )
                res = await engine.snowball_backward(doc_id, provider, progress_callback=update_progress)
            else:
                raise typer.BadParameter("Direction must be 'forward' or 'backward'")

            await engine.close()
            return res
            
    results = asyncio.run(run_snowball())

    limited_results = results[:limit]
    _display_documents_table(
        limited_results,
        title=f"Snowball ({direction.capitalize()}) Results for: {doc_id}",
    )

    if output:
        _save_output(limited_results, output, format)


@app.command(name="import")
def import_citations(
    file_path: Path = typer.Argument(
        ..., help="Path to .ris, .json, or .jsonl citation file", exists=True
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        "-v",
        help="Verify existence against Crossref/OpenAlex and detect hallucinations",
    ),
    enrich: bool = typer.Option(
        False,
        "--enrich",
        "-e",
        help="Hydrate missing abstracts, venues, and citations from OpenAlex",
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Filepath to save normalized results"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, jsonl, csv"
    ),
):
    """Import citations from RIS or JSON files with optional verification and enrichment."""
    suffix = file_path.suffix.lower()
    if suffix == ".ris":
        documents = list(RISImporter().parse(file_path))
    elif suffix == ".jsonl":
        documents = list(JSONLImporter().parse(file_path))
    elif suffix == ".json":
        documents = list(JSONImporter().parse(file_path))
    else:
        raise typer.BadParameter(
            f"Unsupported file type '{suffix}'. Use .ris, .json, or .jsonl"
        )

    console.print(f"[bold]Loaded {len(documents)} records from {file_path}[/bold]")

    async def run_import():
        verifier = DocumentVerifier(
            crossref_provider=CrossrefProvider(),
            openalex_provider=OpenAlexProvider(),
        )
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description="Verifying and hydrating document metadata...", total=None
            )
            docs, aud = await verifier.process_batch(
                documents, verify=verify, enrich=enrich
            )
            await verifier.crossref.client.close()
            await verifier.openalex.client.close()
            return docs, aud
            
    documents, audit = asyncio.run(run_import())

    verified_count = sum(1 for a in audit if a["verified"])
    console.print(
        f"[green]Verified: {verified_count}/{len(documents)} documents confirmed real.[/green]"
    )
    if verified_count < len(documents):
        console.print(
            f"[yellow]Warning: {len(documents) - verified_count} records could not be verified in Crossref/OpenAlex.[/yellow]"
        )

    _display_documents_table(documents, title=f"Imported Documents ({file_path.name})")

    if output:
        _save_output(documents, output, format)


@app.command()
def dedup(
    input_file: Path = typer.Argument(
        ..., help="Path to input JSON, JSONL, or RIS file", exists=True
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Filepath to save deduplicated documents"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, jsonl, csv"
    ),
):
    """Cluster and deduplicate an existing document collection, merging metadata."""
    suffix = input_file.suffix.lower()
    if suffix == ".ris":
        documents = list(RISImporter().parse(input_file))
    elif suffix == ".jsonl":
        documents = list(JSONLImporter().parse(input_file))
    else:
        documents = list(JSONImporter().parse(input_file))

    deduplicator = Deduplicator()
    clusters = deduplicator.deduplicate(documents)
    stats = deduplicator.get_statistics(clusters)
    unique_docs = [c.representative for c in clusters]

    console.print("[bold]Deduplication Summary:[/bold]")
    console.print(f"  * Total input documents: {stats['total_documents']}")
    console.print(f"  * Unique documents: [green]{stats['unique_documents']}[/green]")
    console.print(
        f"  * Duplicates merged: [yellow]{stats['duplicates']} ({stats['duplicate_rate']:.1%})[/yellow]"
    )

    if output:
        _save_output(unique_docs, output, format)


@app.command()
def verify(
    input_file: Path = typer.Argument(
        ..., help="Path to input JSON, JSONL, or RIS file", exists=True
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Filepath to save verified documents"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, jsonl, csv"
    ),
    enrich: bool = typer.Option(
        False,
        "--enrich",
        "-e",
        help="Hydrate missing abstracts, venues, and citations from OpenAlex",
    ),
):
    """Verify citation authenticity against Crossref and OpenAlex, resolve canonical DOIs, and hydrate metadata."""
    suffix = input_file.suffix.lower()
    if suffix == ".ris":
        documents = list(RISImporter().parse(input_file))
    elif suffix == ".jsonl":
        documents = list(JSONLImporter().parse(input_file))
    else:
        documents = list(JSONImporter().parse(input_file))

    console.print(f"[bold]Loaded {len(documents)} records from {input_file}[/bold]")

    async def run_verify():
        verifier = DocumentVerifier(
            crossref_provider=CrossrefProvider(),
            openalex_provider=OpenAlexProvider(),
        )
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description="Verifying and hydrating document metadata...", total=None
            )
            docs, aud = await verifier.process_batch(
                documents, verify=True, enrich=enrich
            )
            await verifier.crossref.client.close()
            await verifier.openalex.client.close()
            return docs, aud

    documents, audit = asyncio.run(run_verify())

    verified_count = sum(1 for a in audit if a["verified"])
    console.print(
        f"[green]Verified: {verified_count}/{len(documents)} documents confirmed real.[/green]"
    )
    if verified_count < len(documents):
        console.print(
            f"[yellow]Warning: {len(documents) - verified_count} records could not be verified in Crossref/OpenAlex.[/yellow]"
        )

    _display_documents_table(documents, title=f"Verified Documents ({input_file.name})")

    if output:
        _save_output(documents, output, format)


@app.command()
def export(
    input_file: Path = typer.Argument(
        ..., help="Input file path (.json, .jsonl, .ris)", exists=True
    ),
    output_file: Path = typer.Argument(..., help="Output destination file path"),
    format: str = typer.Option(
        "json", "--format", "-f", help="Target format: json, jsonl, csv"
    ),
):
    """Convert and export citation collections between formats."""
    suffix = input_file.suffix.lower()
    if suffix == ".ris":
        docs = list(RISImporter().parse(input_file))
    elif suffix == ".jsonl":
        docs = list(JSONLImporter().parse(input_file))
    else:
        docs = list(JSONImporter().parse(input_file))

    _save_output(docs, output_file, format)


@app.command()
def screen(
    input_file: Path = typer.Option(
        ..., "--input", "-i", help="Path to input candidate records (JSON, JSONL, RIS)", exists=True
    ),
    protocol: Path = typer.Option(
        ..., "--protocol", "-P", help="Path to protocol.json containing screening criteria", exists=True
    ),
    output_dir: Path = typer.Option(
        Path("literature"), "--output-dir", "-o", help="Directory to save screening results and PRISMA reports"
    ),
):
    """Screen candidate literature against protocol inclusion/exclusion criteria."""
    import json
    from dataclasses import asdict
    from .screening import evaluate_heuristic_screening, partition_screening_results

    # 1. Load documents
    suffix = input_file.suffix.lower()
    if suffix == ".ris":
        documents = list(RISImporter().parse(input_file))
    elif suffix == ".jsonl":
        documents = list(JSONLImporter().parse(input_file))
    else:
        documents = list(JSONImporter().parse(input_file))

    # 2. Load protocol
    with open(protocol, encoding="utf-8") as f:
        proto_data = json.load(f)

    console.print(f"[bold]Screening {len(documents)} papers against protocol: {protocol.name}...[/bold]")

    # 3. Evaluate documents
    decisions = [evaluate_heuristic_screening(doc, proto_data) for doc in documents]

    # 4. Partition and compile report
    included, excluded, conflicts, report = partition_screening_results(
        documents, decisions
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # 5. Save artifacts
    with open(output_dir / "included.json", "w", encoding="utf-8") as f:
        json.dump(included, f, indent=2, default=str)

    with open(output_dir / "excluded.json", "w", encoding="utf-8") as f:
        json.dump(excluded, f, indent=2, default=str)

    with open(output_dir / "conflicts.json", "w", encoding="utf-8") as f:
        json.dump(conflicts, f, indent=2, default=str)

    with open(output_dir / "prisma_report.json", "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, indent=2, default=str)

    with open(output_dir / "prisma_screening_report.md", "w", encoding="utf-8") as f:
        f.write(report.to_markdown())

    console.print(f"[green]Screening Complete![/green]")
    console.print(f"  [bold]Included[/bold]: {len(included)} papers -> {output_dir / 'included.json'}")
    console.print(f"  [bold]Excluded[/bold]: {len(excluded)} papers -> {output_dir / 'excluded.json'}")
    if conflicts:
        console.print(f"  [yellow]Conflicts / Borderline[/yellow]: {len(conflicts)} papers -> {output_dir / 'conflicts.json'}")
    console.print(f"  [bold]PRISMA Report[/bold]: {output_dir / 'prisma_screening_report.md'}")


def main():
    app()


if __name__ == "__main__":
    main()

