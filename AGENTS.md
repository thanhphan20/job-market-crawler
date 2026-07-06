<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

---

# Agent Guide — Job Market Intelligence

This repo is a **two-part system**: a Python data/intelligence engine and a Next.js 16 dashboard that visualizes what the engine produces. Read [SPEC.md](SPEC.md) for the full architecture and data contract before making structural changes.

## The 30-second mental model

```
Kaggle / TopCV / ITviec  ──►  Python IntelligenceEngine  ──►  intelligence.json  ──►  Next.js dashboard
   (raw CSV in data/raw)        (correlate + visualize)        + Supabase tables        (charts)
```

1. **Python side** crawls/loads job data, correlates local (Vietnam) roles against global (Kaggle) salary/AI-risk benchmarks, and writes results two ways: a JSON blob (`data/sync/intelligence.json` and `public/data/intelligence.json`) and, if configured, Supabase Postgres tables.
2. **Next.js side** reads that data (files or DB), and renders the "Intelligence Terminal" dashboard. It can also trigger the Python engine via API routes.

## Where things live

| Path | What it is |
| :--- | :--- |
| `main.py` | Python CLI entrypoint (argparse). The canonical list of engine actions. |
| `analytics/` | The engine. `intelligence_engine.py` orchestrates; `kaggle_unifier.py`, `topcv_parser.py`, `standardizer.py`, `visualizer.py` are its parts. |
| `crawlers/itviec.py` | Live ITviec scraper (curl-cffi, bypasses Cloudflare). |
| `config/settings.py` | Path config + Vercel `/tmp` fallbacks. **Read this to know where files go.** |
| `scripts/` | Utilities: dataset extraction, Kaggle download, benchmark generation, SO survey fetch, and `ai_analyzer.py` (LLM validate+analyze). |
| `api/index.py` | FastAPI app (Python serverless on Vercel; local uvicorn in dev). |
| `src/app/` | Next.js App Router pages + API routes. `page.tsx` is the SSR data loader. |
| `src/components/` | React dashboard: `RealTimeDashboard.tsx`, `SyncTerminal.tsx`, `charts/`. |
| `src/lib/` | `db.ts` (Prisma singleton), `cache-data.ts` (cached queries). |
| `prisma/schema.prisma` | DB schema: `Job`, `GlobalIntelligence`, `AIImpactMatrix`, `SalaryTrend`. |
| `data/raw/` | Input CSVs (gitignored). Engine discovers them by filename pattern (`PATTERNS` in `config/settings.py`): `*topcv*` = local Vietnam jobs (Kaggle: `baocgb/vietnam-it-jobs-raw-data-from-topcv-2026`), `*ai_job*` = global SE salary+skills benchmark from the **Stack Overflow Developer Survey** (`scripts/fetch_data.py` → `ai_job_so_survey_2025.csv`), `*impact*` = AI automation-risk per tech role (Kaggle: `shree0910/ai-job-risk-and-salary-dataset` → `ai_impact_job_risk.csv`, needs an `Automation Risk (%)` column). `scripts/download_kaggle_datasets.py` orchestrates all three. |

## Running things

**Python engine** (from repo root, needs `pip install -r requirements.txt`):
```bash
python main.py --flow        # Full correlation + report + JSON export (main action)
python main.py --download-datasets  # Vietnam TopCV (Kaggle, needs KAGGLE_API_TOKEN) + SO survey
python main.py --fetch       # Only fetch+normalize the SO survey global benchmark (no token)
python main.py --extract     # Unzip datasets in data/ into data/raw/
python main.py --benchmark   # Generate synthetic Kaggle test data
python main.py --itviec      # Run the live ITviec crawler
python main.py --ai-analyze  # LLM validate + analyze on intelligence.json (free providers)
python main.py --flow --limit 30 --dir ./data/raw   # options
python main.py --ai-analyze --provider gemini --profile "Java dev, HCMC"  # ai options
```

**Next.js dashboard**:
```bash
pnpm install
pnpm dev      # dev server on :3000
pnpm build    # runs `prisma generate && next build`
```

**FastAPI (only needed to test the `/api/sync*` buttons locally)** — `next.config.ts` rewrites `/api/sync`, `/api/market-data`, etc. to `localhost:8000` in dev:
```bash
uvicorn api.index:app --reload --port 8000
```

## Conventions & gotchas — read before editing

- **This is not vanilla Next.js.** Per the block above, check `node_modules/next/dist/docs/` before using any Next.js API.
- **The data contract is `intelligence.json`.** Its shape (`intelligence`, `trends`, `impact`, `skills`, `correlation`, `marketShare`, `rawTable`, `updated_at`) is produced in `IntelligenceEngine._export_dashboard_json` and consumed in `src/app/page.tsx` + `RealTimeDashboard.tsx`. **Change one side → change both.** See SPEC.md § Data Contract.
- **The AI layer is decoupled and optional.** `scripts/ai_analyzer.py` (`--ai-analyze`) *reads* `intelligence.json` and writes its own `data/sync/ai_analysis.json` + `analytics/reports/ai_analysis_*.md`. It does **not** touch the data contract, `--flow`, or the frontend. `--flow` stays offline/deterministic; the AI step is the only part that needs network + API keys. It runs every provider that has a key (`GROQ_API_KEY`/`OPENROUTER_API_KEY`/`GEMINI_API_KEY`), skips the rest, and never crashes the run on a provider error.
- **Two `/api/market-data` handlers exist** — a Next.js route (`src/app/api/market-data/route.ts`, Prisma→JSON fallback) and a FastAPI one (`api/index.py`). `vercel.json` rewrites *all* `/api/(.*)` to the Python function in production, while `next.config.ts` only rewrites specific paths in dev. This split is a live source of confusion; verify which one you're actually hitting before debugging an API.
- **Path handling is Vercel-aware.** On Vercel (`VERCEL=1`) writable paths move to `/tmp` (see `config/settings.py`). Don't hardcode `data/` paths in Python; import from `config.settings`.
- **Env var names are inconsistent.** The engine reads `SUPABASE_URL`, but `.env.example` only defines `NEXT_PUBLIC_SUPABASE_URL`. If cloud sync silently no-ops, this is why. Crawler auth uses `ITVIEC_SESSION` / `ITVIEC_TOKEN`.
- **Version strings drift.** You'll see "v2.0", "v6.0", "v6.1" across files — they're cosmetic labels, not real versioning. Don't trust them; trust the code.
- **`scripts/extract_datasets.py` has a hardcoded Windows path** (`e:\Repository\...`). It won't work as-is on this macOS environment — fix the path if you need it.
- **Secrets & data are gitignored** (`.env`, `data/`, `outputs/`, `reports/`). Don't commit them.

## When you change something

- Touching the engine's JSON output → update both the Python exporter and the TS consumers, and note it in SPEC.md.
- Touching `prisma/schema.prisma` → run `prisma generate` (or `pnpm build`) and update the Supabase upsert calls in `intelligence_engine.py._sync_to_cloud`.
- Adding a CLI action → update `main.py`, this file, and README.md so all three agree.
