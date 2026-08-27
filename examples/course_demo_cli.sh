#!/bin/bash
# Nexus Scholar Suite - Course Demo (CLI)
# Module 02: Search & Discovery
#
# This script demonstrates the CLI workflow for scholar-search-kit

echo "Starting Nexus Scholar CLI Demo..."

# 1. Multi-Provider Literature Search
echo "Searching for papers on 'transformer attention mechanism'..."
uv run scholar-search search "transformer attention mechanism" --limit 15 --output raw_results.json

# 2. Deduplication
echo "Deduplicating raw results..."
uv run scholar-search dedup raw_results.json --output deduped_results.json

# 3. Snowballing (Backward reference search on a specific OpenAlex ID)
# Assuming 'W2741809807' is "Attention Is All You Need"
echo "Performing backward snowballing on 'Attention Is All You Need'..."
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --limit 10 --output references.json

# 4. Verification and Hydration
echo "Verifying references against Crossref and hydrating missing abstracts..."
uv run scholar-search import references.json --verify --enrich --output verified_references.json

echo "Done! Output files generated:"
echo "   - raw_results.json"
echo "   - deduped_results.json"
echo "   - references.json"
echo "   - verified_references.json"
