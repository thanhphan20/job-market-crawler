# Architecture Overview

This document explains how the Job Market Intelligence system is organized at a high level.

## System architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Local Market: TopCV (Vietnam) + ITviec crawler                 │
│  Global Benchmarks: Stack Overflow survey + Kaggle datasets      │
│  Automation Risk: AI/job-risk dataset from Kaggle               │
│                                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ CSV files in data/raw/
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│           Python Intelligence Engine                             │
│                (analytics/ package)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Load & Parse:                                                │
│     ├─ TopCVParser: Read local Vietnam jobs                      │
│     ├─ KaggleUnifier: Pool global salary datasets                │
│     └─ Standardizer: Normalize titles, salaries, experience     │
│                                                                  │
│  2. Correlate:                                                   │
│     ├─ Merge local vs. global by standardized role              │
│     ├─ Calculate salary gaps and opportunities                  │
│     ├─ Derive skill rankings from job descriptions              │
│     └─ Assign automation risk per role                          │
│                                                                  │
│  3. Export & Visualize:                                         │
│     ├─ Write intelligence.json (data contract)                  │
│     ├─ Generate PNG charts (matplotlib)                         │
│     └─ Write markdown reports                                   │
│                                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ intelligence.json + PNG + markdown
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          Deployment & Serving                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FastAPI (api/index.py)              Next.js Dashboard (src/)   │
│  ├─ /api/market-data (get data)     ├─ SSR page load           │
│  ├─ /api/sync (trigger engine)      ├─ Charts (Recharts)       │
│  ├─ /api/sync/itviec (crawler)      ├─ Sync terminal            │
│  └─ /api/report/* (get reports)     └─ Raw data table           │
│                                                                  │
│  Vercel rewrites /api/* to FastAPI in production                │
│  next.config.ts rewrites subset to localhost:8000 in dev        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                       │
                       ▼
              Browser (user views dashboard)
```

## Two-part system

### Part 1: Python Intelligence Engine

**Purpose:** Ingest job data, standardize it, correlate against global benchmarks, and produce a JSON blob + visualizations.

**Location:** `analytics/`, `crawlers/`, `scripts/`, `main.py`, `api/index.py`

**Key components:**
- **Loaders** — TopCVParser, KaggleUnifier, ITviec crawler. They convert raw CSVs into standardized DataFrames.
- **Standardizer** — Maps varied job titles to canonical roles, parses free-text salaries and experience.
- **IntelligenceEngine** — Orchestrates loaders and standardizer; correlates data; exports JSON + visualizations.
- **Visualizer** — Generates matplotlib PNG charts (demand heatmaps, salary trends, risk matrices, etc.).

**Run it:** `python3 main.py --flow` (or via FastAPI `/api/sync`).

**Outputs:** `data/sync/intelligence.json`, `public/data/intelligence.json`, `analytics/reports/*.png`, `analytics/reports/*.md`.

### Part 2: Next.js Dashboard

**Purpose:** Visualize the JSON data in an interactive web UI. Allow users to trigger engine actions and browse reports.

**Location:** `src/`, `api/` (Next.js API routes)

**Key components:**
- **Page (SSR)** — `src/app/page.tsx`. Loads `intelligence.json` at build/request time and passes it to the dashboard component.
- **RealTimeDashboard** — Client component with tabs: local market, global benchmarks, automation risk, skills, raw data. Hot-refreshes on engine completion.
- **SyncTerminal** — Control panel to trigger `/api/sync` actions and display live reports.
- **Charts** — Recharts wrappers for the 8-vector visualization suite.
- **Next.js API routes** — `/api/report`, `/api/report/image/*` for serving markdown and PNGs.

**Run it:** `pnpm dev` (Next.js only) or `pnpm dev:all` (with FastAPI).

**Outputs:** HTML served on port 3000.

## Data contract: `intelligence.json`

The **single most critical interface**. The Python engine writes it; the Next.js dashboard reads it.

```json
{
  "intelligence": [
    {
      "tech": "Java",
      "demand": 42,
      "globalAvgSalary": 120000,
      "localAvgSalary": 50000,
      "resilienceScore": 0.75,
      "riskLevel": "MODERATE"
    }
  ],
  "trends": [
    { "year": 2020, "avgSalary": 80000 },
    { "year": 2025, "avgSalary": 120000 }
  ],
  "impact": [
    { "industry": "Backend Development", "status": "High Demand", "automationRisk": 0.35 }
  ],
  "skills": [
    { "skill": "Spring Boot", "relevance": 92, "growth": 15 }
  ],
  "correlation": [
    { "x": 85, "y": 55, "label": "Java Developer", "size": 150 }
  ],
  "marketShare": [
    { "name": "Backend", "value": 35 }
  ],
  "rawTable": [
    { "std_role": "Backend Developer", "global_salary_mean": 115000, "local_job_count": 42 }
  ],
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Produced by:** `IntelligenceEngine._export_dashboard_json()` in `analytics/intelligence_engine.py`  
**Consumed by:** `src/app/page.tsx` and `RealTimeDashboard.tsx`  
**If you change it:** Update both exporter and all consumers. See [Data Models: intelligence.json](../data-models/intelligence-json.md).

## Workflow: from data to dashboard

1. **User runs** `python3 main.py --flow` (or clicks `/api/sync` in the UI)
2. **Engine loads data:**
   - TopCV CSV (Vietnam job titles, salaries, experience)
   - Stack Overflow survey (global SE benchmarks)
   - Kaggle datasets (automation risk, global salaries)
   - ITviec crawler (if file exists)
3. **Engine correlates:**
   - Standardizes all titles to canonical roles (Backend Developer, Frontend Developer, etc.)
   - Groups by role, computes salary statistics (mean/median/min/max, job counts)
   - Calculates opportunity gaps (global salary - local salary)
   - Extracts skill keywords from job descriptions
   - Assigns automation risk per role
4. **Engine exports:**
   - Writes `intelligence.json` to both `data/sync/` and `public/data/`
   - Generates 8 PNG charts (heatmaps, trends, etc.) to `analytics/reports/`
   - Writes markdown report to `analytics/reports/market_intelligence_<timestamp>.md`
5. **Dashboard loads:**
   - Next.js SSR calls `getDashboardData()`, which reads `intelligence.json`
   - Returns JSON to the browser
6. **User sees:**
   - 8 Recharts visualizations (demand, salary, skills, risk, etc.)
   - Raw data table
   - Option to download reports or trigger new runs

## Key design decisions

- **No database** — All data is file-based (CSVs as input, JSON as output). This keeps the system simple and serverless-friendly (Vercel `$` function).
- **JSON is single source of truth** — There is no live database; the dashboard always reflects what's in the JSON file.
- **Engine is deterministic** — `--flow` produces the same JSON given the same input CSVs. This makes the system reproducible and testable.
- **AI layer is optional and decoupled** — `--ai-analyze` reads the JSON and calls LLMs for validation. It doesn't change the core data or contract. Failures in this step don't crash the run.
- **Path handling is Vercel-aware** — Writable paths switch to `/tmp` on Vercel. See `config/settings.py`.

## See also

- [System Design](system-design.md) — Detailed component breakdown and data flow
- [Workflows: Python Engine](../workflows/python-engine.md) — How `--flow` works step by step
- [Workflows: Dashboard](../workflows/dashboard.md) — How the Next.js UI works
- [Data Models: intelligence.json](../data-models/intelligence-json.md) — The contract in detail
