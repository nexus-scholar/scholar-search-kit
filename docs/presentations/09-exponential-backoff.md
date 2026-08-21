# Episode 9: Exponential Backoff & SQLite Response Caching

**Objective:** Combine SQLite local response caching, HTTP adapter retries, and socket timeouts into `AcademicHttpClient`.

## Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Making network calls reliable and cached. | *Show Title Slide.* |
| 2 | **Episode Goal** | Prevent re-querying identical papers and survive transient gateway errors. | *Highlight goal.* |
| 3 | **SQLite Caching** | Uses `requests_cache.CachedSession` to store HTTP 200 responses in a local `.cache/scholar_cache.sqlite` database. | *Show architecture diagram.* |
| 4 | **Exponential Backoff** | `urllib3.util.retry.Retry` automatically retries 429, 500, 502, 503, 504 errors with 2s, 4s, 8s backoff. | *Explain retry adapter.* |
| 5 | **Explicit Timeouts** | Default 30s timeout prevents hung sockets from blocking workflows indefinitely. | *Explain timeout defense.* |
| 6 | **Verification** | Demonstrate cache hits and fast response times. | *Transition to code.* |

## Terminal & Code Walkthrough

1. **Show `AcademicHttpClient` in `http_client.py`**:
   - Open `src/scholar_search/http_client.py`.
   - Walk through the session configuration, cache backend, and retry adapter mounting.
2. **Demonstrate Cache Hits**:
   - Show how repeat calls return `response.from_cache == True` in <1ms without hitting external servers.
