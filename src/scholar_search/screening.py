"""PRISMA 2020 Title/Abstract screening engine and flow accounting."""

import asyncio
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from .models import Document

logger = logging.getLogger(__name__)


@dataclass
class ScreeningDecision:
    workspace_id: str
    decision: Literal["INCLUDE", "EXCLUDE"]
    confidence: float
    screening_reasoning: str
    matched_inclusion_criteria: list[str] = field(default_factory=list)
    violated_exclusion_criteria: list[str] = field(default_factory=list)
    relevant_rqs: list[str] = field(default_factory=list)
    document_title: str = ""
    doi: str | None = None


@dataclass
class PrismaFlowReport:
    total_identified: int
    duplicates_removed: int
    records_screened: int
    records_excluded: int
    records_included: int
    conflicts_flagged: int
    exclusion_reasons_breakdown: dict[str, int] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Renders PRISMA 2020 Title/Abstract screening flow as Markdown."""
        lines = [
            "# PRISMA 2020 Literature Screening Flow Report",
            "",
            "## 1. Identification Phase",
            f"- **Total Records Identified (Federated Search)**: `{self.total_identified}`",
            f"- **Duplicate Records Removed**: `{self.duplicates_removed}`",
            f"- **Unique Records Retained for Screening**: `{self.records_screened}`",
            "",
            "## 2. Screening Phase (Title & Abstract)",
            f"- **Records Screened**: `{self.records_screened}`",
            f"- **Records Excluded**: `{self.records_excluded}`",
            f"- **Records Eligible for Full-Text Retrieval**: `{self.records_included}`",
            f"- **Borderline Conflicts Flagged for Human Audit**: `{self.conflicts_flagged}`",
            "",
            "### Exclusion Reasons Breakdown",
            "| Exclusion Code | Description / Category | Count |",
            "| :--- | :--- | :--- |",
        ]

        if not self.exclusion_reasons_breakdown:
            lines.append("| *None* | No records excluded | 0 |")
        else:
            for code, count in sorted(self.exclusion_reasons_breakdown.items()):
                lines.append(f"| `{code}` | Systematic Exclusion Rule | {count} |")

        lines.extend([
            "",
            "---",
            f"**Conversion Rate**: {(self.records_included / max(1, self.records_screened)):.1%} of screened records advanced to PDF harvesting.",
            "",
        ])
        return "\n".join(lines)


def batch_partition(documents: list[Document], batch_size: int = 50) -> list[list[Document]]:
    """Partitions documents into discrete batches for LLM evaluation."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    return [documents[i : i + batch_size] for i in range(0, len(documents), batch_size)]


def generate_batch_screening_prompt(
    batch: list[Document],
    protocol_data: dict[str, Any],
) -> str:
    """
    Generates a structured screening system prompt for LLM evaluation.
    Injects research questions, inclusion criteria, exclusion criteria, and the document batch.
    """
    rqs = protocol_data.get("research_questions", [])
    criteria = protocol_data.get("screening_criteria", {})
    inclusions = criteria.get("inclusion", [])
    exclusions = criteria.get("exclusion", [])

    lines = [
        "You are an expert academic systematic reviewer performing PRISMA 2020 Title & Abstract screening.",
        "",
        "### Research Questions",
    ]
    for rq in rqs:
        lines.append(f"- **{rq.get('id', 'RQ')}**: {rq.get('text', '')}")

    lines.extend(["", "### Inclusion Criteria (ALL must be satisfied to INCLUDE)"])
    for inc in inclusions:
        lines.append(f"- **{inc.get('id', 'INC')}**: {inc.get('criterion', '')}")

    lines.extend(["", "### Exclusion Criteria (ANY satisfied triggers EXCLUDE)"])
    for exc in exclusions:
        code = exc.get('id', 'EXC')
        reason_cat = exc.get('reason_category', '')
        desc = f" ({reason_cat})" if reason_cat else ""
        lines.append(f"- **{code}**{desc}: {exc.get('criterion', '')}")

    lines.extend([
        "",
        "### Candidate Papers to Screen",
        "```json",
    ])

    batch_payload = [
        {
            "workspace_id": doc.workspace_id or f"DOC-{idx+1:04d}",
            "title": doc.title,
            "year": doc.year,
            "abstract": doc.abstract or "No abstract available.",
            "venue": doc.venue,
        }
        for idx, doc in enumerate(batch)
    ]
    lines.append(json.dumps(batch_payload, indent=2))
    lines.extend([
        "```",
        "",
        "### Instructions",
        "Evaluate each candidate paper. Return a strict JSON array of objects with schema:",
        "- `workspace_id`: string",
        "- `decision`: 'INCLUDE' or 'EXCLUDE'",
        "- `confidence`: float between 0.0 and 1.0",
        "- `matched_inclusion_criteria`: list of satisfied INC codes",
        "- `violated_exclusion_criteria`: list of triggered EXC codes",
        "- `relevant_rqs`: list of relevant RQ IDs",
        "- `screening_reasoning`: 1-2 sentence rationale",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Reason-category -> disqualifying phrase signals
# These phrases represent *positive surface forms* that indicate a disqualifying paper.
# The exclusion criterion texts are NEGATION-based ("RGB-only studies that do NOT evaluate X"),
# so we cannot extract keywords from the criterion text directly — doing so hits valid
# inclusion-domain words (spectral, detection, weed) in good papers.
# ---------------------------------------------------------------------------
_EXC_PHRASE_SIGNALS: dict[str, list[str]] = {
    # Papers about satellite / coarse-resolution remote sensing (not UAV-scale)
    "OUT_OF_SCOPE_RESOLUTION": [
        "satellite imagery",
        "satellite remote sensing",
        "landsat",
        "sentinel-2",
        "modis",
        "copernicus",
        "medium resolution",
        "coarse resolution",
        "global scale",
        "regional scale",
        "macro-scale",
        "high altitude aircraft",
    ],
    # Papers that are purely RGB — no spectral band fusion, no NIR, no multispectral mention
    "OUT_OF_SCOPE_MODALITY": [
        "rgb only",
        "rgb-only",
        "rgb images only",
        "visible spectrum only",
        "no spectral",
        "without spectral",
        "rgb camera only",
        "purely rgb",
        "single-channel",
        "grayscale only",
    ],
    # Pure survey / review papers with no algorithm or benchmark
    "NO_EMPIRICAL_EVALUATION": [
        "literature review",
        "systematic review",
        "bibliometric analysis",
        "no experiment",
        "no implementation",
        "no benchmark",
        "no algorithmic",
        "conceptual framework only",
        "comprehensive survey",
        "review of literature",
        "survey paper",
        "no quantitative",
    ],
    # Non-English or abstract-only
    "LANGUAGE_OR_FORMAT": [
        "non-english",
        "abstract only",
        "unverified abstract",
    ],
}


def evaluate_heuristic_screening(
    doc: Document,
    protocol_data: dict[str, Any],
) -> ScreeningDecision:
    """
    Deterministic rule-based baseline screener (used when offline or as a fast pre-filter).
    Checks keywords from inclusion criteria and disqualifying phrases for exclusion criteria
    against the document title and abstract.

    Matching strategy:
    - INCLUSION: Extract meaningful words (len >= 4) from each criterion and match against
      the full text (title + abstract). Multiple criterion words hitting = stronger match.
    - EXCLUSION: Use reason_category-dispatched phrase lists of *disqualifying surface forms*
      rather than extracting words from the criterion text directly (which would match valid
      inclusion-domain terminology in good papers).
    - Decision: INCLUDE if inclusion matches and no exclusion phrase found; EXCLUDE if a clear
      disqualifying phrase found; CONFLICT (conf 0.55) if both matched.
    """
    workspace_id = doc.workspace_id or "SCI-000000"
    title_text = (doc.title or "").lower()
    abstract_text = (doc.abstract or "").lower()
    full_corpus = f"{title_text} {abstract_text}"
    abstract_available = bool(abstract_text.strip())

    criteria = protocol_data.get("screening_criteria", {})
    inclusions = criteria.get("inclusion", [])
    exclusions = criteria.get("exclusion", [])

    # --- INCLUSION matching: keywords from criterion text ---
    _INC_STOPWORDS = {
        "that", "this", "with", "from", "have", "been", "such", "their", "will", "which",
        "without", "used", "uses", "include", "including", "studies", "study",
        "report", "reports", "using", "provide", "provides", "based",
    }
    matched_inc: list[str] = []
    inc_evidence: list[str] = []
    for inc in inclusions:
        criterion_text = inc.get("criterion", "").lower()
        words = [w.strip(".,;:()") for w in criterion_text.split()
                 if len(w) >= 4 and w.strip(".,;:()") not in _INC_STOPWORDS]
        matched_words = [w for w in words if w in full_corpus]
        if matched_words:
            matched_inc.append(inc.get("id", "INC-01"))
            inc_evidence.extend(matched_words[:3])

    # --- EXCLUSION matching: reason_category-dispatched disqualifying phrase lists ---
    triggered_exc: list[str] = []
    exc_evidence: list[str] = []
    for exc in exclusions:
        exc_id = exc.get("id", "EXC-01")
        reason_cat = (exc.get("reason_category") or "").upper()
        signal_phrases = list(_EXC_PHRASE_SIGNALS.get(reason_cat, []))
        # Allow protocol to extend with its own negative_signals list
        signal_phrases.extend(s.lower() for s in exc.get("negative_signals", []))

        hit_phrases = [phrase for phrase in signal_phrases if phrase in full_corpus]
        if hit_phrases:
            triggered_exc.append(exc_id)
            exc_evidence.append(f"{exc_id}({hit_phrases[0]!r})")

    # --- Decision logic ---
    # Clear exclusion: phrase found AND nothing in the corpus matches inclusion criteria
    if triggered_exc and not matched_inc:
        return ScreeningDecision(
            workspace_id=workspace_id,
            decision="EXCLUDE",
            confidence=0.85,
            matched_inclusion_criteria=matched_inc,
            violated_exclusion_criteria=triggered_exc,
            relevant_rqs=[],
            screening_reasoning=(
                f"Triggered exclusion criteria: {triggered_exc}. "
                f"Disqualifying phrase(s): {exc_evidence}. No inclusion criteria matched."
            ),
            document_title=doc.title,
            doi=doc.external_ids.doi,
        )

    # Mixed signal: inclusion matched but a disqualifying phrase was also found
    if triggered_exc and matched_inc:
        return ScreeningDecision(
            workspace_id=workspace_id,
            decision="EXCLUDE",
            confidence=0.55,  # borderline — flagged as conflict for human audit
            matched_inclusion_criteria=matched_inc,
            violated_exclusion_criteria=triggered_exc,
            relevant_rqs=[rq.get("id", "RQ1") for rq in protocol_data.get("research_questions", [])],
            screening_reasoning=(
                f"Conflicting signals: inclusion criteria {matched_inc} matched, "
                f"but disqualifying phrase(s) {exc_evidence} also found. Human audit recommended."
            ),
            document_title=doc.title,
            doi=doc.external_ids.doi,
        )

    # No exclusion phrase found — decide based on inclusion
    if matched_inc:
        confidence = 0.80 if abstract_available else 0.65
        reasoning = (
            f"Matched inclusion criteria {matched_inc} via "
            f"{'title+abstract' if abstract_available else 'title only (no abstract)'}: "
            f"evidence={inc_evidence}."
        )
        return ScreeningDecision(
            workspace_id=workspace_id,
            decision="INCLUDE",
            confidence=confidence,
            matched_inclusion_criteria=matched_inc,
            violated_exclusion_criteria=[],
            relevant_rqs=[rq.get("id", "RQ1") for rq in protocol_data.get("research_questions", [])],
            screening_reasoning=reasoning,
            document_title=doc.title,
            doi=doc.external_ids.doi,
        )

    # No inclusion match found
    confidence = 0.45  # low confidence — borderline for human review
    reasoning = (
        f"No inclusion criteria matched in "
        f"{'title+abstract' if abstract_available else 'title only'}. "
        f"Protocol has {len(inclusions)} inclusion criteria. Flagged for audit."
    )
    return ScreeningDecision(
        workspace_id=workspace_id,
        decision="EXCLUDE" if inclusions else "INCLUDE",
        confidence=confidence,
        matched_inclusion_criteria=[],
        violated_exclusion_criteria=[],
        relevant_rqs=[rq.get("id", "RQ1") for rq in protocol_data.get("research_questions", [])],
        screening_reasoning=reasoning,
        document_title=doc.title,
        doi=doc.external_ids.doi,
    )


def partition_screening_results(
    documents: list[Document],
    decisions: list[ScreeningDecision],
    total_identified: int = 0,
    duplicates_removed: int = 0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], PrismaFlowReport]:
    """
    Partitions screened documents into included, excluded, and conflicts sets, and compiles the PRISMA report.

    Bug fix: Build doc_map with DOI as a secondary fallback key so that documents
    whose workspace_id was not assigned (None) during the pipeline can still be
    matched by their DOI, preserving their full metadata (especially abstract).
    """
    # Primary key: workspace_id. Secondary fallback: DOI.
    doc_map_by_wsid: dict[str, Document] = {}
    doc_map_by_doi: dict[str, Document] = {}
    for doc in documents:
        if doc.workspace_id:
            doc_map_by_wsid[doc.workspace_id] = doc
        doi = doc.external_ids.doi if doc.external_ids else None
        if doi:
            doc_map_by_doi[doi] = doc

    included_items: list[dict[str, Any]] = []
    excluded_items: list[dict[str, Any]] = []
    conflict_items: list[dict[str, Any]] = []
    reason_counts: dict[str, int] = {}

    for dec in decisions:
        # Try workspace_id first, then DOI, then bare skeleton
        doc = doc_map_by_wsid.get(dec.workspace_id or "")
        if doc is None and dec.doi:
            doc = doc_map_by_doi.get(dec.doi)
        if doc is None:
            doc_dict: dict[str, Any] = {
                "workspace_id": dec.workspace_id,
                "title": dec.document_title,
                "doi": dec.doi,
            }
        else:
            doc_dict = asdict(doc)

        doc_dict["screening"] = asdict(dec)

        # Flag borderline confidence (0.40-0.70) as conflict for human audit
        if 0.40 <= dec.confidence <= 0.70:
            conflict_items.append(doc_dict)

        if dec.decision == "INCLUDE":
            included_items.append(doc_dict)
        else:
            excluded_items.append(doc_dict)
            for exc_code in dec.violated_exclusion_criteria or ["UNSPECIFIED"]:
                reason_counts[exc_code] = reason_counts.get(exc_code, 0) + 1

    report = PrismaFlowReport(
        total_identified=total_identified or len(documents) + duplicates_removed,
        duplicates_removed=duplicates_removed,
        records_screened=len(decisions),
        records_excluded=len(excluded_items),
        records_included=len(included_items),
        conflicts_flagged=len(conflict_items),
        exclusion_reasons_breakdown=reason_counts,
    )

    return included_items, excluded_items, conflict_items, report


# ---------------------------------------------------------------------------
# LLM-Powered Batch Screener
# ---------------------------------------------------------------------------

def _parse_llm_screening_response(
    raw_text: str,
    batch: list[Document],
    protocol_data: dict[str, Any],
) -> list[ScreeningDecision]:
    """
    Parses a JSON array from the LLM response into ScreeningDecision objects.
    Falls back to heuristic screening for any document whose entry is malformed,
    missing, or whose workspace_id cannot be resolved.
    """
    # Strip markdown fences the model may wrap the JSON in
    stripped = raw_text.strip()
    json_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", stripped)
    if json_match:
        stripped = json_match.group(1).strip()
    # Attempt to find a bare JSON array if no fences
    arr_match = re.search(r"(\[\s*\{[\s\S]+\}\s*\])", stripped)
    if arr_match:
        stripped = arr_match.group(1)

    decisions: list[ScreeningDecision] = []
    parsed: list[dict[str, Any]] = []
    try:
        parsed = json.loads(stripped)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array")
    except Exception as exc:
        logger.warning("LLM response JSON parse failed (%s). Falling back to heuristic for entire batch.", exc)
        return [evaluate_heuristic_screening(doc, protocol_data) for doc in batch]

    wsid_to_doc = {doc.workspace_id or f"DOC-{i+1:04d}": doc for i, doc in enumerate(batch)}

    seen_wsids: set[str] = set()
    for entry in parsed:
        wsid = str(entry.get("workspace_id", ""))
        doc = wsid_to_doc.get(wsid)
        if doc is None:
            logger.debug("LLM returned unknown workspace_id %r — skipping.", wsid)
            continue
        seen_wsids.add(wsid)

        raw_decision = str(entry.get("decision", "INCLUDE")).upper()
        decision: Literal["INCLUDE", "EXCLUDE"] = "INCLUDE" if raw_decision == "INCLUDE" else "EXCLUDE"
        try:
            confidence = float(entry.get("confidence", 0.75))
        except (TypeError, ValueError):
            confidence = 0.75

        decisions.append(
            ScreeningDecision(
                workspace_id=wsid,
                decision=decision,
                confidence=confidence,
                matched_inclusion_criteria=list(entry.get("matched_inclusion_criteria") or []),
                violated_exclusion_criteria=list(entry.get("violated_exclusion_criteria") or []),
                relevant_rqs=list(entry.get("relevant_rqs") or []),
                screening_reasoning=str(entry.get("screening_reasoning", "LLM screened.")),
                document_title=doc.title,
                doi=doc.external_ids.doi,
            )
        )

    # Heuristic fallback for any docs the LLM did not return an entry for
    for i, doc in enumerate(batch):
        wsid = doc.workspace_id or f"DOC-{i+1:04d}"
        if wsid not in seen_wsids:
            logger.debug("LLM did not return entry for %r — using heuristic fallback.", wsid)
            decisions.append(evaluate_heuristic_screening(doc, protocol_data))

    return decisions


class LLMBatchScreener:
    """
    PRISMA 2020 Title/Abstract screener using a Gemini LLM as the decision engine.

    Documents are sent to the LLM in configurable batches (default 20). The model
    reads the protocol (research questions + inclusion/exclusion criteria) and
    returns a structured JSON array of screening decisions. If the LLM call fails
    for a batch, that batch falls back to `evaluate_heuristic_screening` per-document.

    Usage::

        screener = LLMBatchScreener(
            api_key=os.environ["GEMINI_API_KEY"],
            model="gemini-2.0-flash",
            batch_size=20,
        )
        decisions = await screener.screen(documents, protocol_data)
        inc, exc, conflicts, report = partition_screening_results(documents, decisions)
    """

    GEMINI_REST_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash",
        batch_size: int = 20,
        temperature: float = 0.1,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "No Gemini API key found. Set GEMINI_API_KEY env var or pass api_key=."
            )
        self.model = model
        self.batch_size = batch_size
        self.temperature = temperature
        self.timeout = timeout

    async def _call_gemini(self, prompt: str) -> str:
        """Send a single prompt to Gemini REST API and return the text response."""
        import httpx

        url = self.GEMINI_REST_URL.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "candidateCount": 1,
                "responseMimeType": "application/json",
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                url,
                json=payload,
                params={"key": self.api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            # Extract text from Gemini response structure
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini returned no candidates")
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)

    async def screen_batch(
        self,
        batch: list[Document],
        protocol_data: dict[str, Any],
        batch_index: int = 0,
    ) -> list[ScreeningDecision]:
        """
        Screen a single batch of documents using the LLM.
        Returns ScreeningDecision list; falls back to heuristic on any API error.
        """
        prompt = generate_batch_screening_prompt(batch, protocol_data)
        logger.info(
            "LLM screening batch %d (%d papers) via %s ...",
            batch_index + 1, len(batch), self.model,
        )
        try:
            raw_text = await self._call_gemini(prompt)
            decisions = _parse_llm_screening_response(raw_text, batch, protocol_data)
            logger.info(
                "Batch %d: %d INCLUDE, %d EXCLUDE",
                batch_index + 1,
                sum(1 for d in decisions if d.decision == "INCLUDE"),
                sum(1 for d in decisions if d.decision == "EXCLUDE"),
            )
            return decisions
        except Exception as exc:
            logger.warning(
                "LLM call failed for batch %d (%s). Falling back to heuristic.",
                batch_index + 1, exc,
            )
            return [evaluate_heuristic_screening(doc, protocol_data) for doc in batch]

    async def screen(
        self,
        documents: list[Document],
        protocol_data: dict[str, Any],
    ) -> list[ScreeningDecision]:
        """
        Screen all documents, chunked into batches of `self.batch_size`.
        Returns a flat list of ScreeningDecision objects in the same order as documents.
        """
        batches = [
            documents[i : i + self.batch_size]
            for i in range(0, len(documents), self.batch_size)
        ]
        total = len(batches)
        logger.info(
            "Starting LLM screening: %d documents in %d batches of %d.",
            len(documents), total, self.batch_size,
        )

        all_decisions: list[ScreeningDecision] = []
        for idx, batch in enumerate(batches):
            batch_decisions = await self.screen_batch(batch, protocol_data, batch_index=idx)
            all_decisions.extend(batch_decisions)
            # Small courtesy delay between batches to respect rate limits
            if idx < total - 1:
                await asyncio.sleep(1.0)

        logger.info(
            "LLM screening complete: %d INCLUDE, %d EXCLUDE out of %d total.",
            sum(1 for d in all_decisions if d.decision == "INCLUDE"),
            sum(1 for d in all_decisions if d.decision == "EXCLUDE"),
            len(all_decisions),
        )
        return all_decisions
