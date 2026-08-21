# Nexus Scholar Suite — Online Portal & Documentation Roadmap

This document outlines the architectural plan, domain configuration, and deployment strategy for hosting the Nexus Scholar documentation portal and interactive curriculum online at **`https://nexus.mouadh.org/`**.

---

## 1. Vision & Objectives

To deliver an open-source research and documentation portal that:
* **Showcases the Suite**: Unifies `scholar-search-kit`, `scholar-pdf-kit`, and future packages into a coherent developer portal.
* **Hosts the Complete Curriculum**: Presents all 23 lessons with syntax highlighting, search, and integrated PDF slide deck downloads.
* **Provides Interactive API & CLI Manuals**: Interactive, searchable API reference and copyable terminal recipes.
* **Integrates AI Agent Hub**: Hosts machine-readable agent skills (`SKILL.md`) for autonomous literature research.

---

## 2. Technology Stack & Template

* **UI Framework**: Next.js (Static Export mode via `output: 'export'`)
* **Styling**: Tailwind CSS + Typography plugin
* **Design Template**: **Tailwind UI "Syntax"** (Developer Documentation & Course Template)
* **Content Layer**: MDX (Markdown with embedded React components for slide previews, interactive widgets, and copy buttons)
* **Hosting**: GitHub Pages (via GitHub Actions automated static build)
* **Custom Domain**: `nexus.mouadh.org` (CNAME DNS mapping + GitHub SSL enforcement)

---

## 3. Information Architecture (`nexus.mouadh.org`)

```text
nexus.mouadh.org/
│
├── 🚀 Overview
│   ├── Introduction & Architecture
│   ├── Quickstart & Installation (uv, pip, git clone)
│   └── Multi-Provider Federation Guide
│
├── 📖 Course & Lessons (Episodes 00–22)
│   ├── Module 1: Canonical Data Models (Episodes 00–06)
│   ├── Module 2: Resilient Infrastructure & Caching (Episodes 07–09)
│   ├── Module 3: Lexing & Provider Adapters (Episodes 10–14)
│   ├── Module 4: 2-Phase Deduplication & Verification (Episodes 15–16b)
│   ├── Module 5: Modern CLI & File I/O (Episodes 17–18)
│   └── Module 6: End-to-End Pipeline & Packaging (Episodes 19–22)
│
├── 📚 API Reference
│   ├── SearchEngine (search, snowball, federation)
│   ├── DocumentVerifier (Crossref verification, OpenAlex hydration)
│   ├── Exporters (JSON, CSV, BibTeX)
│   ├── Importers (RIS, JSON, JSONL)
│   └── Data Models (Document, Author, ExternalIds, Query, DocumentCluster)
│
├── 🛠️ CLI Manual
│   ├── scholar-search search
│   ├── scholar-search snowball
│   ├── scholar-search import
│   ├── scholar-search dedup
│   └── scholar-search export
│
└── 🤖 AI Agent Skills
    ├── Antigravity Skill Integration
    └── Autonomous Search Recipes
```

---

## 4. DNS & Domain Configuration Blueprint

### Step 1: DNS Record (Registrar / Cloudflare)
| Type | Host / Name | Target / Value | TTL | Proxy Status |
|---|---|---|---|---|
| `CNAME` | `nexus` | `nexus-scholar-org.github.io.` | Auto / 1 hour | DNS Only (or Full Strict SSL) |

### Step 2: GitHub Repository Settings
* **Repository**: `nexus-scholar-org/nexus-docs` (or in-repo `docs-site/` published via GitHub Pages)
* **Branch**: `gh-pages` or GitHub Actions workflow
* **Custom Domain**: `nexus.mouadh.org`
* **HTTPS**: Enforce HTTPS checked.

---

## 5. Next.js Static Export Configuration

```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'out',
  images: {
    unoptimized: true,
  },
  basePath: '',
  trailingSlash: true,
}

export default nextConfig
```

---

## 6. GitHub Actions Deployment Workflow (`.github/workflows/deploy-portal.yml`)

```yaml
name: Deploy Nexus Portal to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Build Next.js Static Export
        run: npm run build

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 7. Execution Checklist (When Ready to Implement)

- [ ] Initialize Next.js app with Tailwind CSS and Tailwind UI "Syntax" template files.
- [ ] Ingest markdown lessons from `docs/lessons/` into MDX pages with frontmatter metadata.
- [ ] Ingest `docs/api_reference.md` and `docs/tutorial.md` into structured doc sections.
- [ ] Copy compiled PDF slide decks (`docs/presentations/pdf/*.pdf`) into public static folder for download and embedded viewing.
- [ ] Add `CNAME` with `nexus.mouadh.org`.
- [ ] Configure GitHub Actions workflow for automated deployment on push.
