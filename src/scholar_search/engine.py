"""Search Engine Orchestrator for scholar-search-kit."""

import asyncio
import logging

from .dedup import Deduplicator
from .models import Document, Query
from .providers import (
    ArxivProvider,
    BiorxivProvider,
    CrossrefProvider,
    OpenAlexProvider,
    PubMedProvider,
    SearchProvider,
    SemanticScholarProvider,
)

logger = logging.getLogger(__name__)


class SearchEngine:
    """Orchestrates search across multiple academic providers."""

    def __init__(self, providers: list[SearchProvider] = None):
        """
        Initialize the search engine.
        If no providers are passed, loads a default production suite.
        """
        if providers is None:
            self.providers = [
                OpenAlexProvider(),
                SemanticScholarProvider(),
                CrossrefProvider(),
                ArxivProvider(),
                PubMedProvider(),
                BiorxivProvider(),
            ]
        else:
            self.providers = providers

        self.deduplicator = Deduplicator()

    async def search_all(self, query: Query, dedup: bool = True, progress_callback=None) -> list[Document]:
        """
        Executes the query across all configured providers concurrently.
        Optionally deduplicates the results.
        """
        all_results: list[Document] = []

        async def fetch_provider(provider: SearchProvider):
            logger.info(f"Querying {provider.name}...")
            count = 0
            try:
                async for doc in provider.search(query):
                    all_results.append(doc)
                    count += 1
                    if progress_callback:
                        progress_callback(provider.name, count)
                logger.info(f"  -> Found {count} documents from {provider.name}.")
            except Exception as e:
                logger.error(f"Error querying {provider.name}: {e}")

        await asyncio.gather(*(fetch_provider(p) for p in self.providers))

        if not dedup or not all_results:
            return all_results

        logger.info(f"Deduplicating {len(all_results)} raw results...")
        clusters = self.deduplicator.deduplicate(all_results)

        unique_results = [cluster.representative for cluster in clusters]
        logger.info(f"  -> Reduced to {len(unique_results)} unique documents.")
        return unique_results

    async def snowball_forward(self, document_id: str, provider_name: str, progress_callback=None) -> list[Document]:
        """Finds papers that cite the given document ID."""
        for provider in self.providers:
            if provider.name.lower() == provider_name.lower():
                logger.info(f"Forward snowballing on {provider.name} for {document_id}")
                results = []
                count = 0
                async for doc in provider.get_citations(document_id):
                    results.append(doc)
                    count += 1
                    if progress_callback:
                        progress_callback(provider.name, count)
                return results
        raise ValueError(f"Provider {provider_name} not found or not registered.")

    async def snowball_backward(self, document_id: str, provider_name: str, progress_callback=None) -> list[Document]:
        """Finds papers that the given document cites."""
        for provider in self.providers:
            if provider.name.lower() == provider_name.lower():
                logger.info(
                    f"Backward snowballing on {provider.name} for {document_id}"
                )
                results = []
                count = 0
                async for doc in provider.get_references(document_id):
                    results.append(doc)
                    count += 1
                    if progress_callback:
                        progress_callback(provider.name, count)
                return results
        raise ValueError(f"Provider {provider_name} not found or not registered.")

    async def close(self):
        """Close HTTP clients for all providers."""
        for provider in self.providers:
            if hasattr(provider, "client") and hasattr(provider.client, "close"):
                await getattr(provider.client, "close")()
