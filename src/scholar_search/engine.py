"""Search Engine Orchestrator for scholar-search-kit."""

import logging
from collections.abc import Iterator
from typing import List

from .models import Document, Query
from .providers import (
    SearchProvider,
    OpenAlexProvider,
    SemanticScholarProvider,
    CrossrefProvider,
    ArxivProvider,
    PubMedProvider,
    BiorxivProvider
)
from .dedup import Deduplicator

logger = logging.getLogger(__name__)

class SearchEngine:
    """Orchestrates search across multiple academic providers."""
    
    def __init__(self, providers: List[SearchProvider] = None):
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
                BiorxivProvider()
            ]
        else:
            self.providers = providers
            
        self.deduplicator = Deduplicator()
        
    def search_all(self, query: Query, dedup: bool = True) -> List[Document]:
        """
        Executes the query across all configured providers.
        Optionally deduplicates the results.
        """
        all_results: List[Document] = []
        
        for provider in self.providers:
            logger.info(f"Querying {provider.name}...")
            try:
                # We consume the generator here to aggregate
                provider_docs = list(provider.search(query))
                all_results.extend(provider_docs)
                logger.info(f"  -> Found {len(provider_docs)} documents.")
            except Exception as e:
                logger.error(f"Error querying {provider.name}: {e}")
                
        if not dedup or not all_results:
            return all_results
            
        logger.info(f"Deduplicating {len(all_results)} raw results...")
        clusters = self.deduplicator.deduplicate(all_results)
        
        unique_results = [cluster.representative for cluster in clusters]
        logger.info(f"  -> Reduced to {len(unique_results)} unique documents.")
        return unique_results

    def snowball_forward(self, document_id: str, provider_name: str) -> List[Document]:
        """Finds papers that cite the given document ID."""
        for provider in self.providers:
            if provider.name.lower() == provider_name.lower():
                logger.info(f"Forward snowballing on {provider.name} for {document_id}")
                return list(provider.get_citations(document_id))
        raise ValueError(f"Provider {provider_name} not found or not registered.")
        
    def snowball_backward(self, document_id: str, provider_name: str) -> List[Document]:
        """Finds papers that the given document cites."""
        for provider in self.providers:
            if provider.name.lower() == provider_name.lower():
                logger.info(f"Backward snowballing on {provider.name} for {document_id}")
                return list(provider.get_references(document_id))
        raise ValueError(f"Provider {provider_name} not found or not registered.")
