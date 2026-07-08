# Operations: Setup

How to set up the repository locally and prepare to run the engine.

## Prerequisites

- **Python 3.10+** — For the Intelligence Engine
- **Node.js 18+** (with pnpm) — For the Next.js dashboard
- **Git** — For version control
- **~5 GB disk space** — For datasets (Kaggle + Stack Overflow)

## Quick start (3 steps)

### 1. Install dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (if running dashboard)
pnpm install
```

### 2. Set up Kaggle credentials (optional but recommended)

To download datasets, you need a Kaggle API token.

1. Go to https://www.kaggle.com/settings/account
2. Click "Create New API Token"
3. Copy the token value (starts with `KGAT_`)
4. Add to `.env`:
   ```bash
   KAGGLE_API_TOKEN=KGAT_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 3. Download datasets and run analysis

```bash
# Download Kaggle datasets + Stack Overflow survey
python3 main.py --download-datasets

# Run the full analysis
python3 main.py --flow

# View the output
cat analytics/reports/market_intelligence_*.md
```

That's it! Your first analysis is complete.

---

## Detailed setup

### Python environment (recommended: virtual env)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Node environment (pnpm)

If you don't have pnpm, install it globally:
```bash
npm install -g pnpm
```

Then install dependencies:
```bash
pnpm install
```

### Configuration file (.env)

Create a `.env` file in the repository root (copy from `.env.example` and fill in secrets):

```bash
# Kaggle API (required for --download-datasets)
KAGGLE_API_TOKEN=KGAT_xxx...

# ITviec scraper (optional, only if using --itviec)
ITVIEC_SESSION=_ITViec_session=...
ITVIEC_TOKEN=...

# LLM providers (optional, for --ai-analyze)
GROQ_API_KEY=gsk_xxx...
OPENROUTER_API_KEY=sk-xxx...
GEMINI_API_KEY=AIzaSyDxxx...
```

**Secrets:** `.env` is gitignored. Never commit it.

---

## Dataset preparation

### Option A: Automatic download (recommended)

```bash
python3 main.py --download-datasets
```

This downloads:
- **TopCV 2026** (Vietnam IT jobs) — From Kaggle, needs `KAGGLE_API_TOKEN`
- **Stack Overflow Developer Survey 2025** — Public download, no auth
- **Global AI/IT salary dataset** — From Kaggle, needs `KAGGLE_API_TOKEN`
- **AI job risk dataset** — From Kaggle, needs `KAGGLE_API_TOKEN`

**Output:** Files in `data/raw/`

**Time:** ~5–10 min depending on download speed.

### Option B: Manual download

Download datasets manually from Kaggle and unzip:

1. Go to https://www.kaggle.com/datasets/baocgb/vietnam-it-jobs-raw-data-from-topcv-2026
2. Click "Download"
3. Move the ZIP to `data/` and unzip:
   ```bash
   unzip -d data/raw data/topcv_jobs.zip
   ```

Repeat for the other datasets:
- `mohankrishnathalla/global-ai-and-data-jobs-salary-dataset`
- `shree0910/ai-job-risk-and-salary-dataset`

Then fetch the SO survey (no auth needed):
```bash
python3 main.py --fetch
```

### Option C: Generate synthetic data (for testing)

```bash
python3 main.py --benchmark
```

This creates fake data matching the schema. Good for testing the engine locally without downloading large files.

---

## Extracting datasets

If you downloaded ZIPs manually, extract them:

```bash
python3 main.py --extract
```

This unzips all `.zip` files in `data/` to `data/raw/`.

---

## Verify setup

Check that the engine can find data:

```bash
python3 main.py --flow --limit 5
```

The `--limit 5` flag loads only 5 rows from each source (fast test).

**Expected output:**
```
--- Intelligence Engine: Syncing Full Flow ---
[*] Parsing TopCV: data/raw/topcv_vietnam_it_jobs_2026.csv
[CLEAN] Kaggle Data: 5/5 records retained
[DONE] Full Knowledge Base Synchronized. Total Local Records: 10
[DASHBOARD] Exported to data/sync/intelligence.json
```

**Check results:**
```bash
ls -la data/sync/
cat data/sync/intelligence.json | jq .
```

You should see `intelligence.json` with 8 vectors.

---

## ITviec scraper setup (optional)

If you want live ITviec job data:

1. **Get credentials:**
   - Visit https://itviec.com and log in
   - Open browser DevTools (F12)
   - Network tab → find a request
   - Copy `_ITViec_session` cookie value
   - Add to `.env`:
     ```bash
     ITVIEC_SESSION=<session_cookie>
     ITVIEC_TOKEN=<token>
     ```

2. **Run scraper:**
   ```bash
   python3 main.py --itviec
   ```

   Output: `data/itviec_jobs.csv` (1–2 min for ~500 jobs)

3. **Include in analysis:**
   ```bash
   python3 main.py --flow
   ```

   The engine automatically includes ITviec jobs if the file exists.

---

## LLM setup (optional)

For AI validation and analysis (`--ai-analyze`), set up free LLM providers:

### Groq

1. Go to https://console.groq.com/keys
2. Create API key
3. Add to `.env`:
   ```bash
   GROQ_API_KEY=gsk_xxx...
   ```

### OpenRouter

1. Go to https://openrouter.ai/keys
2. Create API key
3. Add to `.env`:
   ```bash
   OPENROUTER_API_KEY=sk-xxx...
   ```

### Gemini

1. Go to https://aistudio.google.com/app/apikey
2. Create API key
3. Add to `.env`:
   ```bash
   GEMINI_API_KEY=AIzaSyDxxx...
   ```

**Then:**
```bash
python3 main.py --ai-analyze
```

The script runs all keyed providers, skips the rest, and writes comparison to `analytics/reports/ai_analysis_*.md`.

---

## Directory structure after setup

```
job-market-crawler/
├── .env                       # Your secrets (gitignored)
├── venv/                      # Python virtual env (optional)
├── data/
│   ├── raw/                   # Downloaded datasets
│   │   ├── topcv_vietnam_it_jobs_2026.csv
│   │   ├── ai_job_so_survey_2025.csv
│   │   ├── ai_job_global_it_salary.csv
│   │   └── ai_impact_job_risk.csv
│   ├── sync/                  # Generated outputs
│   │   ├── intelligence.json
│   │   └── ai_analysis.json
│   └── itviec_jobs.csv        # (if --itviec was run)
├── analytics/
│   └── reports/
│       ├── market_intelligence_2025-01-15_10-30-45.md
│       ├── chart_demand_heatmap.png
│       ├── chart_salary_trends.png
│       └── ...
├── public/
│   └── data/
│       └── intelligence.json  # Copy for frontend
├── node_modules/              # Node.js dependencies
└── .next/                      # Next.js build (if pnpm build was run)
```

---

## Troubleshooting setup

### Issue: `ModuleNotFoundError: No module named 'pandas'`

**Fix:** Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Issue: `KAGGLE_API_TOKEN not found`

**Fix:** Add the token to `.env`:
```bash
echo "KAGGLE_API_TOKEN=KGAT_xxx..." >> .env
```

Or set as environment variable:
```bash
export KAGGLE_API_TOKEN=KGAT_xxx...
```

### Issue: `No such file or directory: data/raw/`

**Fix:** Create the directory:
```bash
mkdir -p data/raw
```

Then download datasets or use `--benchmark`.

### Issue: `403 Forbidden` from Kaggle

**Cause:** API token expired or has no access.

**Fix:**
1. Go to https://www.kaggle.com/settings/account
2. Delete old token
3. Create new token
4. Update `.env`

### Issue: `ModuleNotFoundError: No module named 'pnpm'`

**Fix:** Install pnpm globally:
```bash
npm install -g pnpm
pnpm install
```

### Issue: Stack Overflow dataset download fails

**Cause:** The SO survey URL may have changed.

**Fix:** Download manually from https://survey.stackoverflow.co/ and save to `data/raw/ai_job_so_survey_2025.csv`.

---

## Next steps

Once setup is complete:

- **Run locally:** See [Operations: Running Locally](running-locally.md)
- **Understand the engine:** See [Workflows: Python Engine](../workflows/python-engine.md)
- **View the dashboard:** See [Operations: Running Locally](running-locally.md#starting-the-dashboard)

---

## See also

- [SETUP.md](/SETUP.md) — Original setup guide (still useful for detailed steps)
- [Operations: Running Locally](running-locally.md) — How to start servers
- [Integrations: Kaggle](../integrations/kaggle.md) — Kaggle dataset details
