# Episode 13: Ingesting OpenAlex at Scale

**Objective:** Build a production-grade integration with the OpenAlex API, handling cursor pagination, inverted indexes, and polite pool headers.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | Time to plug in our first real data source: OpenAlex. | *Show Title Slide.* |
| 2 | **Episode Goal** | OpenAlex is incredible, but fetching 10,000 papers requires understanding their strict pagination limits and polite pool rules. | *Highlight the goal block.* |
| 3 | **Cursor Pagination** | Offset pagination breaks if the database updates. Cursor pagination acts as a stable bookmark. | *Point to the diagram.* |
| 4 | **Implementation: The Polite Pool** | By simply adding an email header, we get routed to a faster server. We also apply our retry decorators here. | *Explain header injection.* |
| 5 | **Implementation: Abstract Decompression** | OpenAlex saves bandwidth by sending abstracts inside-out as an inverted index. We have to reverse engineer it. | *Explain the reconstruction logic.* |
| 6 | **Verification** | Let's hit the mock server and watch the abstract re-assemble itself. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `openalex.py`**:
   - Open `src/scholar_search/providers/openalex.py`.
   - Walk through the `_fetch_page` generator and cursor logic.
2. **Show Abstract Reconstruction**:
   - Walk through `OpenAlexNormalizer._reconstruct_abstract`.
3. **Run the Tests**:
   - In the terminal, run: `pytest tests/providers/test_openalex.py`
   - Show how the mock `responses` library intercepts the HTTP call.
