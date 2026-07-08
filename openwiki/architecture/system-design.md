# System Design

A detailed breakdown of components, data flow, and APIs.

## Components

### Python Engine (analytics/)

| Component | File | Purpose |
|-----------|------|---------|
| **IntelligenceEngine** | `analytics/intelligence_engine.py` | Orchestrator. Loads data, standardizes, correlates, exports JSON/PNGs, writes reports. Entry point: `run_agentic_analysis()`. |
| **TopCVParser** | `analytics/topcv_parser.py` | Loads Vietnam job listings from CSVs matching `*topcv*.csv` pattern. Maps flexible column names (Job Title, Job title, job_title) to standardized schema. |
| **KaggleUnifier** | `analytics/kaggle_unifier.py` | Discovers and pools all global salary CSVs by pattern (`*ai_job*.csv`). Requires `job_title` and `salary_usd` columns. Cleans and groups by standardized role. |
| **Standardizer** | `analytics/standardizer.py` | Maps varied job titles to canonical roles (e.g., "Sr. Backend Engineer" → "Backend Developer"). Parses free-text experience and Vietnamese salaries. |
| **Visualizer** | `analytics/visualizer.py` | Generates matplotlib PNG charts: demand heatmaps, salary trends, automation-risk matrices, skill rankings, market-share pie, correlation scatter, market-regions, skills-evolution. |
| **SkillAnalyzer** | `analytics/skill_analyzer.py` | Extracts skill keywords from job titles/descriptions using regex patterns (SKILL_KEYWORDS). |
| **KaggleAnalyzer** | `analytics/kaggle_analyzer.py` | Standalone Kaggle insight suite (trend extraction, role classification). |

### Data Loaders (crawlers/, scripts/)

| Component | File | Purpose |
|-----------|------|---------|
| **ITviec Crawler** | `crawlers/itviec.py` | Scrapes ITviec job listings using `curl_cffi` (Cloudflare TLS bypass). Reads credentials from `ITVIEC_SESSION`/`ITVIEC_TOKEN` env. Outputs `data/itviec_jobs.csv`. |
| **Kaggle Downloader** | `scripts/download_kaggle_datasets.py` | Downloads 3 Kaggle datasets: TopCV (local), AI impact (automation risk), global IT salaries. Requires `KAGGLE_API_TOKEN`. |
| **SO Survey Fetcher** | `scripts/fetch_data.py` | Downloads Stack Overflow Developer Survey 2025, filters to SE roles, normalizes columns. No auth needed. |
| **Benchmark Generator** | `scripts/generate_benchmark_data.py` | Creates synthetic test data mimicking the structure of real datasets. |

### Next.js Dashboard (src/)

| Component | File | Purpose |
|-----------|------|---------|
| **Page (SSR)** | `src/app/page.tsx` | Server-renders the dashboard. Calls `getDashboardData()` to load `intelligence.json`. Passes data to `<RealTimeDashboard>`. |
| **RealTimeDashboard** | `src/components/RealTimeDashboard.tsx` | Client component with 5 tabs: local market, global, impact, skills, raw. Listens for `intel-sync-complete` event to hot-refresh. |
| **SyncTerminal** | `src/components/SyncTerminal.tsx` | Control panel. POSTs to `/api/sync*` endpoints. Fetches and renders latest markdown report. Rewrites image paths to `/api/report/image/<file>`. |
| **IntelligenceCharts** | `src/components/charts/IntelligenceCharts.tsx` | Recharts wrapper components. Defines TS types for all chart data. |
| **KaggleDataTable** | `src/components/KaggleDataTable.tsx` | Raw data tab. Displays standardized role data with salary/job-count columns. |

### API Layer

#### Next.js routes (src/app/api/)

| Endpoint | Method | Purpose | Environment |
|----------|--------|---------|-------------|
| `/api/report` | GET | Returns latest `analytics/reports/market_intelligence_*.md` content. | Next.js + Vercel |
| `/api/report/image/[filename]` | GET | Serves PNG from `analytics/reports/`. | Next.js + Vercel |
| `/api/run-script` | POST | Spawns `python3 main.py <command>` and streams stdout. Allowed: `--flow`, `--itviec`, `--extract`. Local-only (no Vercel). | Next.js dev only |

#### FastAPI routes (api/index.py)

| Endpoint | Method | Purpose | Environment |
|----------|--------|---------|-------------|
| `/api/market-data` | GET | Returns latest `intelligence.json` (fallback discovery). | FastAPI (Vercel prod + local dev) |
| `/api/sync` | POST | Triggers `python3 main.py --flow`. Returns operation status. | FastAPI |
| `/api/sync/itviec` | POST | Triggers `python3 main.py --itviec` + `--flow`. | FastAPI |
| `/api/sync/extract` | POST | Triggers `python3 main.py --extract`. | FastAPI |

**Routing logic:**
- **Production (Vercel):** `vercel.json` rewrites all `/api/(.*)` → `api/index.py` (FastAPI function).
- **Development:** `next.config.ts` rewrites `/api/sync*` and `/api/report/image/*` to `localhost:8000` (FastAPI) and `/api/report` to Next.js.

### Configuration (config/settings.py)

| Variable | Purpose |
|----------|---------|
| `BASE_DIR` | Repository root. |
| `DATA_DIR` | Input/output directory. On Vercel (`VERCEL=1`), switches to `/tmp/data`. |
| `RAW_DATA_DIR` | `data/raw/`. On Vercel, switches to `/tmp/data/raw`. |
| `OUTPUT_DIR` | `analytics/reports/`. On Vercel, switches to `/tmp/reports`. |
| `SYNC_DIR` | `data/sync/`. On Vercel, switches to `/tmp/sync`. |
| `PATTERNS` | Filename patterns for dataset discovery (`*topcv*`, `*ai_job*`, `*impact*`). |

**Key rule:** Always import paths from `config.settings`, never hardcode `data/` paths.

## Data flow: `--flow` (full analysis)

```
User runs: python3 main.py --flow
           (or POST /api/sync)
           │
           ▼
   IntelligenceEngine.run_agentic_analysis()
           │
       ┌───┴───────────────┬────────────────┐
       ▼                   ▼                ▼
   load_all_sources()    _correlate_data()  (exports + visualizes)
       │                     │                 │
   ┌───┴────────────┐     ┌─┴──────────────┐  │
   ▼   ▼   ▼   ▼   ▼     ▼   ▼   ▼   ▼   ▼  │
TopCV Kaggle ITviec Standard Standardize      │
(local)(global)(live)  (merge by title)     │
   │   │   │   │ │     │ │ │ │ │             │
   └───┴───┴───┴─┴─────┴─┴─┴─┴─┴─────────────┘
                       │
                       ▼ merged DataFrame
           _export_dashboard_json(merged)
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
       intelligence  visualizer  _write_full_report()
           .json      .plot_*()       │
           │              │          ▼
           │              ▼      market_intelligence_
           │           *.png       <ts>.md
           ▼
    data/sync/intelligence.json
    public/data/intelligence.json
```

## Data flow: user clicks "Sync" in dashboard

```
Browser POST /api/sync
       │
       ▼ (routing)
       ├─ Vercel prod → FastAPI /api/sync
       └─ Dev → localhost:8000 /api/sync
                       │
                       ▼
        FastAPI.sync() (api/index.py)
                       │
                       ▼
        subprocess("python3 main.py --flow")
                       │
                       ▼ (after completion)
        window.postMessage('intel-sync-complete')
                       │
                       ▼ (browser receives)
        RealTimeDashboard.useEffect()
                       │
                       ▼
        fetch('/api/market-data')
                       │
                       ▼
        RealTimeDashboard state updates
                       │
                       ▼
        Charts re-render with fresh data
```

## Data standardization pipeline

```
Raw job title (TopCV)          Raw job title (Stack Overflow)
      │                                │
      ├─ "Backend Engineer"       ├─ "Backend Developer"
      ├─ "Java Developer"         ├─ "Java/Spring Backend"
      └─ "Sr. Backend Dev"        └─ "Software Engineer (Backend)"
                 │                          │
                 └──────────┬───────────────┘
                            ▼
          Standardizer.standardize_title()
                            │
              ┌─────────────┴─────────────┐
              │ (longest-match keyword    │
              │  table TITLE_MAP)         │
              └─────────────┬─────────────┘
                            ▼
                    "Backend Developer"
                    (canonical role)
                            │
                            ▼
        (used as JOIN key with global benchmarks)
```

## intelligence.json: exported vectors

| Vector | Source | Shape |
|--------|--------|-------|
| `intelligence` | Merged local/global correlations | Array of {tech, demand, globalAvgSalary, localAvgSalary, resilienceScore, riskLevel} |
| `trends` | Multi-year salary evolution for SE roles | Array of {year, avgSalary} |
| `impact` | Automation risk per industry | Array of {industry, status, automationRisk} |
| `skills` | Top skill keywords + growth trends | Array of {skill, relevance, growth} |
| `correlation` | Scatter-plot data (demand vs. local salary) | Array of {x, y, label, size} |
| `marketShare` | Pie-chart distribution | Array of {name, value} |
| `rawTable` | Full standardized data for browsing | Array of {std_role, global_salary_mean/median/min/max, global_job_count, local_salary_avg, local_job_count} |
| `updated_at` | Timestamp | ISO-8601 string |

See [Data Models: intelligence.json](../data-models/intelligence-json.md) for detail.

## Automation risk assignment

Priority order:

1. **Real Kaggle dataset** (if available) — Use `ai_impact_job_risk.csv` with `Automation Risk (%)` column. Match role by keyword (e.g., "DevOps" → "DevOps Engineer").
2. **Software-engineer baseline** — If role matches "Backend" or "Frontend", use the SE baseline from the dataset with relative adjustment by role keyword.
3. **Heuristic fallback** — If no dataset, use keyword-based risk scoring (e.g., high-level languages = lower risk, infrastructure = higher risk).

Result: `riskLevel` ∈ {LOW, MODERATE, HIGH}.

## Skill extraction

Priority order:

1. **Survey data** — If `required_skills` or `LanguageHaveWorkedWith` column exists, extract real skills from job descriptions.
2. **Title mining** — Extract keywords from local job titles using regex patterns (SKILL_KEYWORDS: Java, Spring, React, AWS, etc.).
3. **Frequency ranking** — Rank by job-count mentions and growth trend year-over-year.

Result: Top ~30 skills with relevance (0-100) and growth (% change).

## Vercel deployment notes

- **Read-only filesystem:** Writable paths move to `/tmp` via `config/settings.py` when `VERCEL=1`.
- **API routing:** `vercel.json` sends all `/api/(.*)` → Python FastAPI function. This is different from dev routing.
- **No persistent disk:** Data only updates on redeploy. To refresh data, run the engine and commit the updated JSON.
- **Cold start:** First request may take 10–30s as the Python process initializes.

---

## See also

- [Architecture: Overview](overview.md) — High-level system design
- [Workflows: Python Engine](../workflows/python-engine.md) — How --flow works internally
- [Data Models: intelligence.json](../data-models/intelligence-json.md) — Data contract detail
- [Operations: Setup](../operations/setup.md) — How to run locally
