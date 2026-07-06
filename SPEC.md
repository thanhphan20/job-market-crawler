# Technical Specification — Job Market Intelligence

This document describes how the system is actually built, so an agent can reason about it without re-reading every file. It reflects the code as-is (including its rough edges). For a quick orientation and run commands, see [AGENTS.md](AGENTS.md); for a product-level pitch, see [README.md](README.md).

---

## 1. System overview

Two cooperating halves that communicate through a shared JSON file and (optionally) a Supabase Postgres database:

- **Intelligence Engine (Python)** — ingests job-market datasets, standardizes and correlates local vs. global data, and emits (a) a dashboard JSON blob, (b) Supabase rows, and (c) matplotlib PNG report images.
- **Dashboard (Next.js 16 + React 19)** — server-renders the latest intelligence and displays it as an "Intelligence Terminal" of charts. It can trigger engine actions on demand.

```
                        ┌─────────────────────────── Python ───────────────────────────┐
 data/raw/*.csv  ──►  TopCVParser ┐
 data/itviec_jobs.csv ─► (inline) ┼─► IntelligenceEngine._correlate_data ─► merged DataFrame
 data/raw/*kaggle*.csv ─► KaggleUnifier ┘                                          │
                                                                                   ├─► intelligence.json  (data/sync + public/data)
                                                                                   ├─► Supabase upsert (GlobalIntelligence, AIImpactMatrix, SalaryTrend)
                                                                                   └─► analytics/reports/*.png + market_intelligence_*.md
                        └───────────────────────────────────────────────────────────────┘
                        ┌─────────────────────────── Next.js ──────────────────────────┐
 src/app/page.tsx (SSR) ─► reads DB or JSON ─► <RealTimeDashboard> ─► Recharts components
 src/app/api/* + api/index.py (FastAPI) ─► trigger engine / serve data
                        └───────────────────────────────────────────────────────────────┘
```

---

## 2. The Intelligence Engine (Python)

### 2.1 Entry points
- `main.py` — argparse CLI. Actions: `--flow` (full analysis), `--extract`, `--benchmark`, `--itviec`. Options: `--dir`, `--limit`. With no args it prints help.
- `analytics/intelligence_engine.py` — `IntelligenceEngine`, the orchestrator. Also runnable directly (`__main__` runs a full flow *including* ITviec).
- `api/index.py` — FastAPI wrapper exposing the same actions as HTTP endpoints (for the dashboard's Sync buttons and Vercel).

### 2.2 Data flow inside `--flow`
1. `load_all_sources(skip_itviec=...)`
   - **TopCV** via `TopCVParser` — dynamic file discovery (`data/raw/**/*topcv*.csv`), flexible column mapping, produces standardized columns (`standardized_title`, `min_years_exp`, `annual_salary_usd`, ...).
   - **ITviec** — reads `data/itviec_jobs.csv` inline (only title is standardized; salary left null, exp hardcoded to 2). Skipped when `skip_itviec=True` (the API and `main.py --flow` both skip it).
   - **Global benchmark** via `KaggleUnifier` — discovers the global-salary CSV by pattern (`*ai_job*`, requires `job_title` + `salary_usd`; see `PATTERNS` in `config/settings.py`), cleans, groups by standardized role → `global_benchmarks` (salary mean/median/min/max, job count; automation risk/growth only if an impact/insights CSV is also present). The default source is the **Stack Overflow Developer Survey 2025**, fetched and reshaped by `scripts/fetch_data.py` into `data/raw/ai_job_so_survey_2025.csv` (real ~18k software-engineer rows: `job_title` from `DevType`, `salary_usd` from `ConvertedCompYearly`, `required_skills` from `LanguageHaveWorkedWith`). Only software-engineering `DevType`s are kept (see `DEVTYPE_MAP`), so the benchmark isn't diluted by data-science/non-tech respondents.
   - Local sources are concatenated into `self.local_data`. The default local source is the **Vietnam TopCV 2026** dataset (via Kaggle).
2. `run_agentic_analysis()`
   - `_correlate_data()` — groups local data by `standardized_title`, right-joins onto global benchmarks by `std_role`, sorts by `global_job_count`. This `merged` frame is the source of truth for exports.
   - `_export_dashboard_json(merged)` — builds the **data contract** (§4) and writes it to `SYNC_DIR/intelligence.json` and `public/data/intelligence.json`, then cloud-syncs. The `skills` vector comes from `_extract_skill_matrix()`: it prefers the real survey skills (`required_skills` / SO `LanguageHaveWorkedWith`) via `_skills_from_survey()`, and falls back to mining local job titles (`SKILL_KEYWORDS`) via `_skills_from_titles()`. Automation risk (`resilienceScore`/`riskLevel`/`impact`) comes from `_risk_for_role()`, which uses the real AI-impact dataset via `_load_impact_lookup()` (Kaggle `shree0910/ai-job-risk-and-salary-dataset`, normalized to `ai_impact_job_risk.csv` with an `Automation Risk (%)` column): real per-role risk where the role matches (e.g. DevOps, Cloud), else the dataset's software-engineer baseline anchored with relative role nuance, else a keyword heuristic as last resort.
   - `visualizer.plot_*` — generates the 8-vector PNG suite into `analytics/reports/` (or `/tmp/reports` on Vercel).
   - `_write_full_report()` — writes `market_intelligence_<timestamp>.md` referencing those PNGs.
   - `_sync_to_cloud()` — upserts `GlobalIntelligence`, `AIImpactMatrix`, `SalaryTrend` into Supabase (only if a client was created).

### 2.3 Standardization (`analytics/standardizer.py`)
`DataStandardizer` is the glue that lets local and global data merge:
- `standardize_title` — maps varied titles to canonical roles via a longest-match keyword table (`TITLE_MAP`); falls back to cleaning noise words. Everything joins on the result.
- `parse_experience` — first integer found in a free-text string.
- `parse_salary_vnd` — parses Vietnamese salary strings (`trieu` = million VND), converts to annual USD at `VND_USD_RATE = 25000`.

### 2.4 Configuration (`config/settings.py`)
- `BASE_DIR`, and Vercel-aware `DATA_DIR` / `RAW_DATA_DIR` / `OUTPUT_DIR` / `SYNC_DIR` (switch to `/tmp/*` when `VERCEL=1`).
- `PATTERNS` — filename substrings used for dynamic dataset discovery.
- Always import paths from here rather than hardcoding.

### 2.5 The crawler (`crawlers/itviec.py`)
- Uses `curl_cffi` with `impersonate="chrome"` to bypass Cloudflare TLS fingerprinting.
- Reads `ITVIEC_SESSION` / `ITVIEC_TOKEN` cookies from env.
- Scrapes queries `["backend", "fullstack-developer", "java", "software-engineer"]` across pages, dedupes by `data-job-key`, follows each JD link (with retry/backoff on 403), and saves to `data/itviec_jobs.csv`.

---

## 3. The Dashboard (Next.js)

### 3.1 Stack
Next.js 16 (App Router), React 19, Tailwind CSS v4, Recharts, Framer Motion, Prisma 6 (`@prisma/client`), Vercel Analytics. Package manager: **pnpm**.

### 3.2 Server-side data loading (`src/app/page.tsx`)
`getDashboardData()` loads the dashboard payload with environment-dependent priority:
- **Dev**: try local files (`public/data/intelligence.json`, then `data/sync/kaggle_insights.json`) → fall back to DB.
- **Prod**: try DB (Prisma) → fall back to files.
- Hardcoded default fallbacks exist for every vector so the UI never renders empty.

### 3.3 Components
- `RealTimeDashboard.tsx` — client component; tabs (`local | global | impact | skills | raw`); hot-refreshes from `/api/market-data` when a `intel-sync-complete` window event fires.
- `SyncTerminal.tsx` — the control panel; POSTs to `/api/sync`, `/api/sync/itviec`, `/api/sync/extract`; fetches and renders the latest markdown report (rewriting `![](file)` to `/api/report/image/<file>`).
- `charts/IntelligenceCharts.tsx` — all Recharts wrappers and the shared TS types (`TechStat`, `SalaryTrend`, `ImpactData`, `SkillStat`, `CorrelationPoint`, `MarketRegion`).
- `KaggleDataTable.tsx` — the "raw data" tab table.

### 3.4 Next.js API routes (`src/app/api/`)
| Route | Purpose |
| :--- | :--- |
| `GET /api/market-data` | Prisma read of intelligence/trends/impact; falls back to `public/data/intelligence.json`. |
| `GET /api/report` | Returns the latest `analytics/reports/market_intelligence_*.md` content. |
| `GET /api/report/image/[filename]` | Serves a PNG from `analytics/reports/`. |
| `POST /api/run-script` | Spawns `python3 main.py <command>` locally and streams stdout (allowed commands: `--flow`, `--itviec`, `--extract`). Local-only. |

### 3.5 Persistence (`src/lib/`)
- `db.ts` — Prisma client singleton (global-cached in non-prod).
- `cache-data.ts` — `unstable_cache`-wrapped Prisma reads (1h revalidate, tag `intelligence`). Note: currently imported by `page.tsx` but the active loader uses direct Prisma calls.

---

## 4. Data contract — `intelligence.json`

The single most important interface. Produced by `IntelligenceEngine._export_dashboard_json`, consumed by `src/app/page.tsx` and `RealTimeDashboard`. **Both sides must change together.**

```jsonc
{
  "intelligence": [ { "tech", "demand", "globalAvgSalary", "localAvgSalary", "resilienceScore", "riskLevel" } ],
  "trends":       [ { "year", "avgSalary" } ],
  "impact":       [ { "industry", "status", "automationRisk" } ],
  "skills":       [ { "skill", "relevance", "growth" } ],
  "correlation":  [ { "x", "y", "label", "size" } ],
  "marketShare":  [ { "name", "value" } ],
  "rawTable":     [ { "std_role", "global_salary_mean|median|min|max", "global_job_count", "local_salary_avg", "local_job_count" } ],
  "updated_at":   "ISO-8601 string"
}
```

`riskLevel` ∈ `LOW | MODERATE | HIGH`. Automation risk is derived from Kaggle data, with heuristic fallbacks by role keyword when missing.

---

## 4b. AI layer — `scripts/ai_analyzer.py` (`--ai-analyze`)

An **optional, decoupled** post-processing step. It never touches the data contract, `--flow`, or the frontend.

- **Input:** reads `data/sync/intelligence.json` (fallback `public/data/intelligence.json`). Errors if neither exists (run `--flow` first).
- **Digest:** `_build_digest()` extracts a compact top-~15-roles + trends + top-skills structure so requests stay inside free-tier limits and every provider sees identical input.
- **Providers:** `PROVIDERS` dict, two HTTP shapes via `requests` only (no SDKs):
  - `kind: "openai"` → OpenAI-compatible `/chat/completions` — covers **Groq** and **OpenRouter**.
  - `kind: "gemini"` → Google Generative Language `generateContent` REST — **Gemini**.
  - Each provider is gated on its key env (`GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`); missing keys are skipped, run errors only if zero configured. Model overridable via `*_MODEL` env.
- **Two calls per provider:** a **validate** step (structured JSON: `overall_confidence`, `flags[]` across plausibility/risk_sanity/standardization/consistency) and an **analyze** step (structured JSON: `market_summary`, `key_insights[]`, `opportunities[]`, `recommendations[]`, `risks[]`, anchored to a profile — default Vietnam backend/Java dev, overridable via `--profile`).
- **Robustness:** HTTP 429 → 3× exponential backoff; other errors captured per-provider; malformed JSON handled by `_extract_json` (direct → strip ``` fences → first`{`…last`}`), preserving `raw_response` on failure. The run always completes and writes both outputs.
- **Comparison:** default runs all keyed providers; `--provider <name>` forces one. `_agreement_summary()` tallies roles flagged by ≥2 providers; a metrics table records latency / #recommendations / parse success per provider.
- **Outputs:**
  - `data/sync/ai_analysis.json` — per-provider results + `agreement` + `metrics_table`.
  - `analytics/reports/ai_analysis_<timestamp>.md` — metrics table + side-by-side provider detail.

---

## 5. Database schema (`prisma/schema.prisma`)

Postgres (Supabase). `DATABASE_URL` (pooled, port 6543) for the app; `DIRECT_URL` (port 5432) for migrations.

- **`Job`** — raw crawled listings (title, company, salary range, skills[], source). Currently defined but not the primary path the dashboard reads.
- **`GlobalIntelligence`** — `tech` (unique), `demand`, `globalAvgSalary`, `localAvgSalary?`, `resilienceScore`, `riskLevel`. Upserted on `tech`.
- **`AIImpactMatrix`** — `industry` + `status` (unique together), `automationRisk`.
- **`SalaryTrend`** — `year` + `tech?` + `source` (unique together), `avgSalary`.

---

## 6. Deployment (Vercel)

- `vercel.json` rewrites **all** `/api/(.*)` → `/api/index.py` (the FastAPI function). This means in production the FastAPI app answers API traffic, not the Next.js route handlers.
- `next.config.ts` only rewrites a *subset* of `/api/*` paths to `localhost:8000` and only in development.
- Consequence: the effective API implementation differs between dev and prod. When debugging an endpoint, confirm which handler is live in your environment.
- Writable output paths shift to `/tmp` on Vercel (`config/settings.py`), since the deployment filesystem is read-only except `/tmp`.

---

## 7. Known inconsistencies (do not treat as intentional)

These exist in the current code; fix opportunistically or account for them, don't cargo-cult them.

1. **Duplicate `/api/market-data`** in both Next.js and FastAPI (§6).
2. **Env var mismatch** — engine reads `SUPABASE_URL`; `.env.example` defines `NEXT_PUBLIC_SUPABASE_URL`. Cloud sync silently disables when `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` are absent.
3. **Hardcoded Windows path** in `scripts/extract_datasets.py` (`e:\Repository\...`).
4. **Version label drift** — v2.0 / v6.0 / v6.1 appear in different files with no real meaning.
5. **README command drift** — historical README examples (`--fetch`, `--crawl`, `--pages`) predate the current `main.py` flags. Trust `main.py --help`.
6. **ITviec loading** hardcodes `min_years_exp = 2` and null salary, so ITviec rows contribute little to salary correlation.
