# Episode 8: Rate Limiting with Token Buckets

**Objective:** Protect public academic infrastructure with a polite, continuous-refill token bucket rate limiter.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Being a good scientific citizen means respecting API rate limits. | *Show Title Slide.* |
| 2 | **Episode Goal** | Prevent temporary IP bans by throttling outbound calls client-side. | *Highlight goal.* |
| 3 | **Token Bucket Math** | Tokens replenish continuously at `rate` tokens/sec up to `capacity`. Requests consume 1 token. | *Show formula diagram.* |
| 4 | **Implementation: `RateLimiter`** | Implemented inside `src/scholar_search/http_client.py` with `wait()` blocking logic. | *Show code snippet.* |
| 5 | **Provider Configurations** | OpenAlex gets 10 req/s, Crossref 5 req/s, arXiv 1 req/s, PubMed 3 req/s. | *Explain config mapping.* |
| 6 | **Verification** | Inspect rate limit throttling in action. | *Transition to code.* |

## Terminal & Code Walkthrough

1. **Show `http_client.py`**:
   - Open `src/scholar_search/http_client.py`.
   - Walk through the `RateLimiter` class and its `wait()` calculation.
2. **Show `config.py`**:
   - Show how default provider rate limits are configured.
