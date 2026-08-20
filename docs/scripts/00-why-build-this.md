# Episode 0: Why Build This?
**Series:** Building a Reproducible Scholarly Search Toolkit
**Focus:** Scientific Need & The Problem with Proprietary Search

---

## Scene 1: The Problem
**[Visual]**  
- Show Slide 1 (Title) then transition to Slide 2 ("The Scientific Need").
- Highlight the phrase "Exploratory Research often relies on proprietary algorithms."

**[Audio / Voiceover]**  
"Welcome to the Scholar Search Kit series. If you've ever tried to conduct a systematic literature review, or even just map the background evidence for a thesis, you've hit a wall: the search algorithms are a black box. You search for 'machine learning in radiology' today, get 100 results, and tomorrow you get 112. Why? You have no idea. The tool inextricably couples the *mechanics* of the search with your *research methodology*."

---

## Scene 2: The Solution
**[Visual]**  
- Transition to Slide 3 ("The Goal of this Toolkit").

**[Audio / Voiceover]**  
"The goal of this series is to build our way out of that trap. We're going to build a modular, extensible, and mathematically auditable search toolkit in Python, completely from scratch. We will ingest from OpenAlex, Crossref, arXiv, and Semantic Scholar through a unified, reproducible interface."

---

## Scene 3: Building from First Principles
**[Visual]**  
- Transition to Slide 4 ("Why Build from Scratch?").
- Bring up the `strategy-pipeline/src/slr` repository on screen briefly to show the reference architecture.

**[Audio / Voiceover]**  
"Why build from scratch instead of just using a library? Because auditability is more important than convenience. We cannot scientifically trust what we cannot trace. By building from first principles, we guarantee the provenance of every single record. Along the way, we'll learn how to design resilient code with rate limiters and how to structure a project so clearly that an AI agent can reliably execute tasks within it."

---

## Scene 4: Roadmap
**[Visual]**  
- Transition to Slide 5 ("What to Expect").
- Flash the `docs/video-series.md` table on screen briefly.

**[Audio / Voiceover]**  
"Over the next 5 seasons, we will build out the models, the rate-limited provider ingestion, conservative deduplication, and finally, a CLI wrapped for AI agents. Let's get started."
