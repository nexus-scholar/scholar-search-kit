# Master Strategy: Nexus Scholar Suite & Academia Online Portal

This strategy document defines the architecture, content federation, and deployment plan for the unified **Nexus Scholar Suite** developer portal and **Academia Course Platform** hosted under **`mouadh.org`** (or **`nexus.mouadh.org`**).

---

## 1. Executive Vision

To establish an internationally recognized, peerless open-source academic intelligence ecosystem that brings together:
1. **6 Modular Python Toolkits**:
   - `scholar-search-kit`: Federated multi-provider discovery & Crossref verification.
   - `scholar-pdf-kit`: Open-access PDF harvesting, hydration & parsing.
   - `scholar-rag-kit`: Academic chunking, embedding & vector retrieval.
   - `scholar-bib-kit`: Citation graph parsing & BibTeX/RIS reconciliation.
   - `scholar-eval-kit`: Benchmark datasets & hallucination scoring.
   - `scholar-agent-kit`: Autonomous research assistants & tool protocols.
2. **The Academia Full Course**:
   - A multi-module, graduate-level curriculum (23 episodes) with 16:9 vector slide decks, rigorous lessons, code contracts, and interactive exercises.
3. **The Research Lab & Personal Portfolio**:
   - Highlighting PhD research, scientific papers, and open-source contributions by Mouadh.

---

## 2. Tailwind UI Template Allocation Strategy

By combining specialized Tailwind UI templates, we achieve a tailored experience for every modality:

| Template | Section / Route | Purpose & Key Features |
|---|---|---|
| **Spotlight** | **Landing Page (`/`)** | **Suite Showcase & Research Portfolio**: Hero section with live search terminal demo, interactive cards for all 6 packages, publications list, and bio. |
| **Syntax** | **Documentation (`/docs/*`)** | **Multi-Package Documentation**: Package switcher dropdown, sticky sidebar navigation, instant client-side search (Pagefind), dark-mode code blocks, and copy buttons. |
| **Primer / Transmit** | **Academia Course (`/course` or `/academy`)** | **Interactive Curriculum**: 23-episode syllabus, video player / audio embeds, slide deck PDF viewer drawers, and lesson transcripts. |
| **Protocol** | **API Reference (`/api-reference`)** | **3-Column REST & Python API Reference**: Sidebar navigation $\cdot$ Signature explanation $\cdot$ Interactive code examples. |

---

## 3. Unified Information Architecture (`mouadh.org` / `nexus.mouadh.org`)

```text
nexus.mouadh.org/
│
├── 🌐 / (Landing Page — Powered by Spotlight)
│   ├── Hero: "The Clean-Room Academic Intelligence Suite"
│   ├── 6 Toolkit Cards (Search, PDF, RAG, Bib, Eval, Agent)
│   ├── Academia Course Teaser & Enrolment
│   └── Research Publications & GitHub Links
│
├── 📚 /docs (Documentation Portal — Powered by Syntax)
│   ├── /docs/search-kit/       (Federation, Crossref verification, Models, CLI)
│   ├── /docs/pdf-kit/          (Unpaywall, arXiv, PMC Open Access harvesting)
│   ├── /docs/rag-kit/          (Academic chunking, embedding, retrieval)
│   ├── /docs/bib-kit/          (Citation networks, BibTeX/RIS tools)
│   └── /docs/agent-kit/        (Antigravity skills, Autonomous workflows)
│
├── 🎓 /academy (Academia Full Course — Powered by Transmit/Syntax)
│   ├── Module 1: Models & Invariants (Episodes 00–06)
│   ├── Module 2: Resilient Infrastructure (Episodes 07–09)
│   ├── Module 3: Provider Subsystems (Episodes 10–14)
│   ├── Module 4: Deduplication & Verification (Episodes 15–16b)
│   ├── Module 5: Modern CLI & I/O (Episodes 17–18)
│   ├── Module 6: End-to-End Pipeline & CI (Episodes 19–22)
│   └── [Each episode includes: Markdown Lesson + Embedded 16:9 PDF Deck + Pytest Counterexamples]
│
└── 🤖 /skills (Autonomous Research Skills Hub)
    └── Machine-readable agent manifests and prompts
```

---

## 4. Repository & Deployment Architecture (Option B)

### Repository Name: `nexus-scholar-org/nexus-portal`

```text
nexus-portal/
├── app/                    # Next.js 15 App Router
│   ├── (marketing)/        # Landing page (Spotlight)
│   ├── docs/               # Documentation pages (Syntax)
│   │   ├── search-kit/
│   │   ├── pdf-kit/
│   │   └── ...
│   └── academy/            # Full Course syllabus & player (Syntax/Transmit)
├── content/                # MDX content files
│   ├── search-kit/         # Pulled/synchronized from scholar-search-kit
│   ├── pdf-kit/            # Pulled/synchronized from scholar-pdf-kit
│   └── academy/            # 23 lesson chapters & presentation notes
├── public/                 # Static assets
│   ├── slides/             # All 23 compiled 16:9 PDF slide decks
│   ├── brand/              # SVG Nexus logos & dark-mode icons
│   └── CNAME               # nexus.mouadh.org (or mouadh.org)
├── components/             # Tailwind UI React components
├── .github/workflows/      # Automated static build & GitHub Pages deploy
└── next.config.mjs         # Static export configuration (output: 'export')
```

---

## 5. Next Steps & Execution Plan

When you provide the template `.zip` archives:
1. **Phase 1: Portal Repository Setup**: Initialize `nexus-portal` repository with Next.js, Tailwind CSS, and the Tailwind UI component library.
2. **Phase 2: Content Ingestion Pipeline**: Ingest all 23 lessons, API reference, CLI guides, and 23 PDF slide decks from `scholar-search-kit`.
3. **Phase 3: Package Switcher & Search**: Wire up multi-package navigation switcher and fast client-side Pagefind search.
4. **Phase 4: Domain & CI/CD**: Configure GitHub Actions to automatically deploy to GitHub Pages under `nexus.mouadh.org` with HTTPS enforcement.
