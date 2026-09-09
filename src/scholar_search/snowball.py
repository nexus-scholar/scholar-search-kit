"""Multi-hop citation snowballing (forward/backward) with BFS traversal."""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .engine import SearchEngine

from .dedup import Deduplicator
from .models import Document

logger = logging.getLogger(__name__)

Direction = Literal["forward", "backward"]

_OPENALEX_PREFIXES = ("https://openalex.org/", "https://api.openalex.org/works/")

_SANDBOX_LIMITS = {
    "max_depth": 5,
    "max_per_node": 500,
    "max_total": 2000,
}


def _normalize_doc_id(doc_id: str) -> str:
    """Strip provider URL prefix to produce the short id used in API paths/filters."""
    for prefix in _OPENALEX_PREFIXES:
        if doc_id.startswith(prefix):
            return doc_id[len(prefix) :]
    return doc_id


def _canonical_keys(doc: Document) -> set[str]:
    """Return a set of stable identity keys for dedup across hops."""
    keys: set[str] = set()
    pid = doc.provider_id
    if pid:
        keys.add(_normalize_doc_id(pid))
        keys.add(pid)
    eid = doc.external_ids
    if eid.doi:
        keys.add(eid.doi.lower())
    if eid.openalex_id:
        keys.add(_normalize_doc_id(eid.openalex_id))
    if eid.pubmed_id:
        keys.add(eid.pubmed_id)
    if eid.s2_id:
        keys.add(eid.s2_id)
    if eid.arxiv_id:
        keys.add(eid.arxiv_id)
    if keys:
        return keys
    return {f"fallback:{doc.title.lower().strip()}:{doc.year or 0}"}


@dataclass
class CitationEdge:
    """A directed citation link discovered during snowballing."""

    source_id: str
    target_id: str
    direction: Direction
    hop: int
    provider: str


@dataclass
class ChainingResult:
    """Outcome of a multi-hop snowball traversal."""

    documents: list[Document] = field(default_factory=list)
    edges: list[CitationEdge] = field(default_factory=list)
    visited_ids: set[str] = field(default_factory=set)
    stats: dict[str, Any] = field(default_factory=dict)


class CitationChainer:
    """Performs breadth-first citation snowballing across one or more seed ids.

    Expansion uses a single provider (OpenAlex for open-access breadth, S2 for
    richer metadata). Each hop can run in *forward* (papers citing the current
    node), *backward* (papers the current node cites), or *both* directions. A
    deduplicated frontier prevents cycles.
    """

    def __init__(self, engine: SearchEngine | None = None):
        from .engine import SearchEngine as _SE

        self.engine = engine or _SE()
        self._dedup = Deduplicator()

    def _provider(self, provider_name: str):
        for provider in self.engine.providers:
            if provider.name.lower() == provider_name.lower():
                return provider
        raise ValueError(
            f"Provider '{provider_name}' not found in engine providers. "
            f"Available: {[p.name for p in self.engine.providers]}"
        )

    async def chain(
        self,
        seeds: list[str],
        provider: str = "openalex",
        directions: list[Direction] | None = None,
        max_depth: int = 1,
        max_per_node: int = 200,
        max_total: int = 500,
        year_min: int | None = None,
        year_max: int | None = None,
        progress_callback: Any = None,
    ) -> ChainingResult:
        """Run BFS snowballing starting from *seeds*.

        Parameters
        ----------
        seeds:
            Provider-specific document ids (e.g. ``"W2741809807"`` for
            OpenAlex, ``"DOI:10.xxxx/yyyy"`` for S2).
        provider:
            Name of an engine-registered provider used for citation lookups.
        directions:
            Directions to expand at each hop. Defaults to ``["backward"]``
            (classic PRISMA reference chaining).
        max_depth:
            Hops away from the seed to explore. ``1`` = direct neighbours only,
            ``2`` = neighbours-of-neighbours, etc. (hard cap: 5).
        max_per_node:
            Hard cap on citations/references fetched per individual node.
        max_total:
            Global cap on the total number of documents collected.
        year_min / year_max:
            Optional publication-year bounds applied to every discovered doc.
        progress_callback:
            ``Callable(provider_name, count)`` invoked per newly collected doc.

        Returns
        -------
        ChainingResult
            Deduplicated documents, the citation-edge manifest, visited ids,
            and traversal stats.
        """
        if directions is None:
            directions = ["backward"]

        max_depth = min(max(1, max_depth), _SANDBOX_LIMITS["max_depth"])
        max_per_node = min(max(1, max_per_node), _SANDBOX_LIMITS["max_per_node"])
        max_total = min(max(1, max_total), _SANDBOX_LIMITS["max_total"])

        provider_inst = self._provider(provider)

        all_docs: list[Document] = []
        all_edges: list[CitationEdge] = []
        visited: set[str] = set()
        for s in seeds:
            visited.add(_normalize_doc_id(s))
            visited.add(s)

        queue: deque[tuple[str, int]] = deque((s, 0) for s in seeds)

        hop_counts: dict[int, int] = {}

        while queue and len(all_docs) < max_total:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            next_depth = depth + 1

            for direction in directions:
                if direction == "forward":
                    gen = provider_inst.get_citations(node_id)
                else:
                    gen = provider_inst.get_references(node_id)

                count = 0
                async for doc in gen:
                    if count >= max_per_node or len(all_docs) >= max_total:
                        break
                    count += 1
                    hop_counts[next_depth] = hop_counts.get(next_depth, 0) + 1

                    if year_min and doc.year and doc.year < year_min:
                        continue
                    if year_max and doc.year and doc.year > year_max:
                        continue

                    keys = _canonical_keys(doc)
                    if keys & visited:
                        continue

                    visited.update(keys)
                    doc.mark_retrieved()
                    all_docs.append(doc)

                    all_edges.append(
                        CitationEdge(
                            source_id=_normalize_doc_id(node_id),
                            target_id=_normalize_doc_id(doc.provider_id),
                            direction=direction,
                            hop=next_depth,
                            provider=provider,
                        )
                    )

                    if next_depth < max_depth:
                        queue.append((_normalize_doc_id(doc.provider_id), next_depth))

                    if progress_callback:
                        progress_callback(provider, len(all_docs))

        unique: list[Document] = []
        if all_docs:
            clusters = self._dedup.deduplicate(all_docs)
            unique = [cluster.representative for cluster in clusters]

        stats = {
            "seeds": [_normalize_doc_id(s) for s in seeds],
            "provider": provider,
            "directions": list(directions),
            "max_depth": max_depth,
            "total_raw": len(all_docs),
            "total_unique": len(unique),
            "edges": len(all_edges),
            "per_hop": hop_counts,
        }
        logger.info(
            "Chaining complete: %d unique docs from %d seeds (depth %d)",
            len(unique),
            len(seeds),
            max_depth,
        )

        return ChainingResult(
            documents=unique,
            edges=all_edges,
            visited_ids=visited,
            stats=stats,
        )