# Operations: Running Locally

How to start the servers and develop/test locally.

## Python engine only (no frontend)

For testing the engine or running analysis:

```bash
# Full analysis (load, correlate, export JSON + PNGs)
python3 main.py --flow

# With synthetic data (no Kaggle download needed)
python3 main.py --benchmark && python3 main.py --flow

# With row limit (fast testing)
python3 main.py --flow --limit 30

# LLM validation (after --flow)
python3 main.py --ai-analyze

# Live ITviec scraper
python3 main.py --itviec && python3 main.py --flow
```

**Outputs:**
- `data/sync/intelligence.json` — Dashboard data
- `analytics/reports/market_intelligence_*.md` — Markdown report
- `analytics/reports/*.png` — PNG charts

---

## Next.js dashboard only (frontend)

For UI development without the Python engine:

```bash
pnpm dev
```

Runs on http://localhost:3000

**Note:** The dashboard will load cached `intelligence.json`. Any `/api/sync` clicks will fail (no backend). Good for:
- CSS/UI changes
- Testing chart rendering
- Mobile responsive design

---

## Full stack (frontend + backend)

For testing API integrations and sync buttons:

```bash
# Terminal 1: Python backend
uvicorn api.index:app --reload --port 8000

# Terminal 2: Next.js frontend
pnpm dev

# Terminal 3: (optional) Watch the engine
watch -n 5 'ls -lh data/sync/intelligence.json'
```

**Frontend:** http://localhost:3000  
**Backend API:** http://localhost:8000

**What works now:**
- Dashboard loads and renders
- Click "Full Sync" button → runs `/api/sync` → triggers `python3 main.py --flow`
- Charts auto-refresh after sync completes
- Report display with embedded images

---

## One-command setup (dev all)

Convenience script to start both servers together:

```bash
pnpm dev:all
```

This runs:
```bash
concurrently \
  "pnpm dev" \
  "uvicorn api.index:app --reload --port 8000"
```

**Frontend:** http://localhost:3000  
**Backend:** http://localhost:8000  

Both start in the same terminal (use Ctrl+C to stop both).

---

## Running individual commands

### Quick tests

```bash
# Benchmark: Generate synthetic data
python3 main.py --benchmark

# Small load: Only 10 rows
python3 main.py --flow --limit 10

# Scrape ITviec (requires credentials in .env)
python3 main.py --itviec

# Extract ZIPs
python3 main.py --extract

# Fetch SO survey only (no Kaggle auth)
python3 main.py --fetch

# Download all Kaggle datasets
python3 main.py --download-datasets

# LLM analysis (after --flow)
python3 main.py --ai-analyze --provider groq --profile "Java dev, HCMC"
```

### Help

```bash
python3 main.py --help
pnpm dev --help
uvicorn --help
```

---

## Logs and debugging

### Python engine

```bash
# Verbose output (already enabled by default in --flow)
python3 main.py --flow 2>&1 | tee engine.log

# Check latest report
tail -50 analytics/reports/market_intelligence_*.md

# Inspect JSON structure
jq . data/sync/intelligence.json | less
jq '.skills | length' data/sync/intelligence.json
```

### Next.js frontend

```bash
# Build logs during development
pnpm dev

# Check for TypeScript errors
pnpm type-check

# Lint code
pnpm lint
```

### FastAPI backend

```bash
# Start with verbose logging
uvicorn api.index:app --reload --port 8000 --log-level debug

# Check API endpoint
curl http://localhost:8000/api/market-data | jq .

# Check backend health
curl -I http://localhost:8000/api/market-data
```

---

## Common dev workflows

### Scenario 1: Testing engine changes

```bash
# Make changes to analytics/
python3 main.py --benchmark    # Generate test data
python3 main.py --flow         # Run engine with changes
cat data/sync/intelligence.json | jq .intelligence[0]  # Inspect output
```

### Scenario 2: Testing UI changes

```bash
pnpm dev
# Open http://localhost:3000
# Make changes to src/components/
# Save → hot-reload (browser auto-refreshes)
```

### Scenario 3: Testing API integration

```bash
# Terminal 1
uvicorn api.index:app --reload --port 8000

# Terminal 2
pnpm dev

# Test in browser: Click "Full Sync" button
# Watch logs in Terminal 1 for Python subprocess output
```

### Scenario 4: Testing data sync

```bash
# Terminal 1
uvicorn api.index:app --reload --port 8000

# Terminal 2
pnpm dev

# Terminal 3 (watch)
watch -n 2 'ls -lh data/sync/ && wc -l data/sync/intelligence.json'

# Click "Full Sync" in browser, watch timestamps change in Terminal 3
```

---

## Performance tips

### Speed up engine runs

```bash
# Test with only 5 rows (seconds, not minutes)
python3 main.py --flow --limit 5

# Use benchmark data (no download needed)
python3 main.py --benchmark --flow --limit 10
```

### Speed up builds

```bash
# Skip TypeScript type-check during dev (faster HMR)
pnpm dev --experimental-app-dir

# Pre-build Next.js (testing production build)
pnpm build && pnpm start
```

### Reduce dataset size

Edit `config/settings.py` to limit rows:
```python
MAX_ROWS_PER_SOURCE = 50  # Default: unlimited
```

---

## Clean up and reset

### Delete generated outputs

```bash
rm -rf data/sync/*.json analytics/reports/*.png analytics/reports/*.md
```

### Delete all downloaded datasets

```bash
rm -rf data/raw/*
```

### Clean Node dependencies

```bash
rm -rf node_modules .next pnpm-lock.yaml
pnpm install
```

### Clean Python dependencies

```bash
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Vercel simulation

To test in Vercel-like conditions (writable `/tmp`, limited disk):

```bash
# Temporarily enable Vercel mode
VERCEL=1 python3 main.py --flow

# Check what writes to /tmp
ls -lh /tmp/sync/
ls -lh /tmp/data/
```

This triggers path fallbacks in `config/settings.py`.

---

## Debugging API routing

### Check which endpoint handler is active

**Development:**
```bash
# next.config.ts rewrites /api/sync to localhost:8000
curl http://localhost:3000/api/sync
# → Routed to uvicorn on localhost:8000
```

**Production (simulated):**
```bash
# vercel.json would route to Python FastAPI function
# You can't test this locally exactly, but the config is in vercel.json
```

---

## See also

- [Operations: Setup](setup.md) — Initial setup
- [Workflows: Python Engine](../workflows/python-engine.md) — Engine details
- [Workflows: Dashboard](../workflows/dashboard.md) — Frontend details
- [Workflows: Deployment](../workflows/deployment.md) — Production deployment
