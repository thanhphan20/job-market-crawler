# OpenWiki Quick Start — Job Market Intelligence

Welcome! This repository is a **two-part system** that crawls job markets and analyzes technology trends to identify in-demand skills.

## What is this?

A toolkit that:
1. **Crawls job markets** (ITviec, TopCV, Stack Overflow, Kaggle datasets) for real job postings
2. **Analyzes skill demand** by scanning job descriptions for technologies (Java, React, AWS, etc.)
3. **Correlates local trends** (Vietnam) against global salary/AI-risk benchmarks
4. **Generates visual reports** showing market gaps and ROI-ranked career paths
5. **Powers an interactive dashboard** (Next.js) to explore the data

See [README.md](/README.md) for the product overview, or [SETUP.md](/SETUP.md) for installation.

## Quick orientation

```
Data sources (CSV) ──► Python Intelligence Engine ──► intelligence.json ──► Next.js Dashboard
(Kaggle/TopCV/SO)    (correlate + visualize)        (shared data contract)   (charts/tables)
```

**Key files:**
- `main.py` — Python CLI entrypoint. Runs `--flow` (analyze), `--download-datasets` (fetch data), `--ai-analyze` (LLM validation).
- `analytics/intelligence_engine.py` — Core analyzer. Merges local job data with global salary benchmarks.
- `src/app/page.tsx` — Next.js dashboard. Reads `intelligence.json` and renders charts.
- `api/index.py` — FastAPI backend. Serves data and triggers engine actions from the UI.

## Next steps

**New to the codebase?**
- Start here: [Architecture Overview](architecture/overview.md) — How the Python engine and Next.js dashboard work together
- Then: [System Design](architecture/system-design.md) — Data flow, components, and API contracts

**Want to run it locally?**
- Follow [Operations: Setup](operations/setup.md) — Install dependencies, download datasets, run the engine

**Need to modify something?**
- [Workflows: Python Engine](workflows/python-engine.md) — How `--flow` and other CLI commands work
- [Workflows: Dashboard](workflows/dashboard.md) — How the Next.js frontend works and connects to the backend
- [Data Models](data-models/intelligence-json.md) — The `intelligence.json` contract (what the engine outputs, what the dashboard reads)

**Making changes to integrations or data sources?**
- [Integrations](integrations/) — Kaggle, Stack Overflow survey, ITviec scraper, LLM providers

**Testing or troubleshooting?**
- [Testing Guide](testing/guide.md) — How to validate changes and common issues

## Repository structure

```
job-market-crawler/
├── main.py                        # CLI entrypoint (argparse)
├── analytics/                     # Intelligence engine (Python)
│   ├── intelligence_engine.py     # Orchestrator: correlate data, export JSON, visualize
│   ├── kaggle_unifier.py          # Load global salary/automation-risk datasets
│   ├── topcv_parser.py            # Parse local Vietnam job listings
│   ├── standardizer.py            # Normalize titles, salaries, experience
│   ├── visualizer.py              # Generate PNG charts
│   └── skill_analyzer.py          # Extract skill keywords
├── crawlers/itviec.py             # ITviec scraper (curl-cffi, Cloudflare bypass)
├── config/settings.py             # Path config, Vercel-aware fallbacks
├── scripts/                       # Utilities: Kaggle download, benchmark gen, SO fetch
├── api/index.py                   # FastAPI server (Vercel serverless / local)
├── src/                           # Next.js 16 dashboard
│   ├── app/                       # App Router pages + API routes
│   ├── components/                # React UI (dashboard, charts, sync terminal)
│   └── globals.css                # Tailwind + global styles
├── data/                          # Input/output directories (gitignored)
├── openwiki/                      # This documentation
├── AGENTS.md                      # Agent orientation (deprecated, see OpenWiki)
├── SETUP.md                       # Setup instructions (still useful for detailed steps)
└── SPEC.md                        # Technical spec (still useful for deep dives)
```

## Important conventions

- **Data flows through `intelligence.json`** — The Python engine writes it; the Next.js dashboard reads it. If you change the JSON shape, update both the exporter and consumer.
- **Configuration is Vercel-aware** — Writable paths move to `/tmp` on Vercel. Always import paths from `config/settings.py`, never hardcode.
- **There is no database** — Data lives in CSV files and the resulting JSON. Git commits control versioning.
- **API is split in dev vs. prod** — In production, `vercel.json` routes all `/api/*` to the FastAPI function. In dev, `next.config.ts` routes a subset to `localhost:8000`. See [Workflows: Deployment](workflows/deployment.md).

## Common tasks

**Analyze job market data with real datasets:**
```bash
pip install -r requirements.txt
python3 main.py --download-datasets   # Fetch Kaggle + SO survey
python3 main.py --flow                # Run analysis
python3 main.py --ai-analyze          # LLM validation (optional)
```

**View the dashboard:**
```bash
pnpm install
pnpm dev:all    # Starts Next.js (3000) + FastAPI (8000)
# Visit http://localhost:3000
```

**Generate test data and run locally:**
```bash
python3 main.py --benchmark   # Synthetic data
python3 main.py --flow        # Analyze
pnpm dev                       # Dashboard only
```

**Scrape live ITviec jobs:**
```bash
# Add ITVIEC_SESSION and ITVIEC_TOKEN to .env
python3 main.py --itviec
python3 main.py --flow
```

## Help & troubleshooting

- **Setup issues?** → See [Operations: Setup](operations/setup.md) and [SETUP.md](/SETUP.md)
- **Code questions?** → Check [Workflows](workflows/) for how things work
- **API endpoints?** → See [System Design: API Routes](architecture/system-design.md#api-routes)
- **Data format questions?** → See [Data Models: intelligence.json](data-models/intelligence-json.md)

---

**Last updated:** OpenWiki auto-generated documentation. For the latest product overview, see [README.md](/README.md). For full architecture, see [SPEC.md](/SPEC.md).
