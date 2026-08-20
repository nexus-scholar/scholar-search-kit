# Episode 14: Ingesting Crossref DOIs & Metadata

**Objective:** Integrate the definitive source of DOI metadata, managing complex URL-encoded cursors and chaotic nested date schemas.

## 🎬 Presentation Script

| Slide | Title | Talking Points | Action |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | OpenAlex was our broad net. Crossref is our sniper rifle. | *Show Title Slide.* |
| 2 | **Episode Goal** | If a paper has a DOI, Crossref has its canonical metadata. We need to parse it cleanly. | *Highlight the goal block.* |
| 3 | **Deep Cursor Pagination** | Crossref cursors are heavily base64 encoded. If we don't URL-encode them properly, the `+` turns into a space and the loop breaks. | *Point to the diagram.* |
| 4 | **Implementation: `issued.date-parts`** | Crossref's date structure is infamous. We have to parse nested arrays that might randomly be missing elements. | *Explain the date fallback logic.* |
| 5 | **Implementation: The Polite Pool** | Again, providing an email gets us VIP server access. | *Reiterate etiquette.* |
| 6 | **Verification** | Let's feed our normalizer a fragmented date array and watch it safely extract the year. | *Transition to Terminal.* |

## 💻 Terminal & Code Walkthrough

1. **Show `crossref.py`**:
   - Open `src/scholar_search/providers/crossref.py`.
   - Walk through the `CrossrefNormalizer._parse_date` method.
2. **Show Author extraction**:
   - Show how `family` and `given` names are safely joined.
3. **Run the Tests**:
   - In the terminal, run: `pytest tests/providers/test_crossref.py`
   - Prove that the mock responses are normalized perfectly into `Document` models.
