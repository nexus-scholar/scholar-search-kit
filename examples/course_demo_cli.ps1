Write-Host "Starting Nexus Scholar CLI Demo..."

# 1. Multi-Provider Literature Search
Write-Host "Searching for papers on 'transformer attention mechanism'..."
uv run scholar-search search "transformer attention mechanism" --limit 15 --output raw_results.json

# 2. Deduplication
Write-Host "Deduplicating raw results..."
uv run scholar-search dedup raw_results.json --output deduped_results.json

# 3. Snowballing (Backward reference search on a specific OpenAlex ID)
# Assuming 'W2741809807' is "Attention Is All You Need"
Write-Host "Performing backward snowballing on 'Attention Is All You Need'..."
uv run scholar-search snowball W2741809807 --provider openalex --direction backward --limit 10 --output references.json

# 4. Verification and Hydration
Write-Host "Verifying references against Crossref and hydrating missing abstracts..."
uv run scholar-search import references.json --verify --enrich --output verified_references.json

Write-Host "Done! Output files generated:"
Write-Host "   - raw_results.json"
Write-Host "   - deduped_results.json"
Write-Host "   - references.json"
Write-Host "   - verified_references.json"
