# Setup Guide — Job Market Intelligence

Quick-start guide to get the Intelligence Engine running with real Kaggle datasets.

---

## Option 1: Automatic Dataset Download (Recommended)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
pnpm install  # for Next.js (optional, only if running dashboard)
```

### 2️⃣ Setup Kaggle Credentials
The downloader authenticates with a Kaggle **API token** used as a Bearer credential — no `kaggle` CLI or `kaggle.json` file needed.

1. Go to https://www.kaggle.com/settings/account → **"Create New API Token"**.
2. Copy the `KGAT_...` token value into `.env`:
```bash
KAGGLE_API_TOKEN=KGAT_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3️⃣ Download the Datasets
```bash
python3 main.py --download-datasets
```

This fetches the two curated datasets (see table below), and automatically
normalizes the Glassdoor salary strings (e.g. `$68K - $94K`) into a numeric
`salary_usd` the engine can use.

| Slot | Kaggle dataset | Role |
| :--- | :--- | :--- |
| `salary` | [emreksz/software-engineer-jobs-and-salaries-2024](https://www.kaggle.com/datasets/emreksz/software-engineer-jobs-and-salaries-2024) | Global software-engineer salary benchmark |
| `topcv` | [baocgb/vietnam-it-jobs-raw-data-from-topcv-2026](https://www.kaggle.com/datasets/baocgb/vietnam-it-jobs-raw-data-from-topcv-2026) | Local Vietnam market (TopCV) |

**Output:**
```
============================================================
 KAGGLE DATASET DOWNLOADER
============================================================

[*] SALARY: Software Engineer Jobs & Salaries 2024 (global SE roles)
  ✓ Software Engineer Salaries.csv -> ai_job_software_engineer_2024.csv
  ✓ Normalized SE salaries: 740 rows with numeric salary_usd

[*] TOPCV: Vietnam IT Jobs raw data from TopCV 2026 (local market)
  ✓ topcv_jobs.csv -> topcv_vietnam_it_jobs_2026.csv
  ✓ Extracted and renamed to ai_data_science_2020_2026.csv

[SUCCESS] All datasets downloaded and ready!
Location: /path/to/data

Next: python3 main.py --flow
```

### 4️⃣ Run the Intelligence Flow
```bash
python3 main.py --flow
```

**Output:**
```
--- Intelligence Engine: Syncing Full Flow ---
[*] Parsing TopCV: data/raw/topcv_vietnam_it_jobs_2026.csv
[CLEAN] Kaggle Data: 740/740 records retained after strict filtering.
[DONE] Full Knowledge Base Synchronized. Total Local Records: 1550
[DASHBOARD] Exported to data/sync/intelligence.json
[*] Generating 8-Vector Visualization Suite...

========================================
 STRATEGIC MARKET SUMMARY
========================================
 > Software Engineer: Opportunity Gap +$118,000/year
 > Fullstack Developer: Opportunity Gap +$118,931/year
 > Backend Developer: Opportunity Gap +$106,774/year
========================================
```

The skill matrix is mined from the local TopCV job titles, so it reflects the
Vietnamese software-engineering market (Java, .NET/C#, Node.js, React, ...).

### 5️⃣ View the Dashboard (Optional)
```bash
pnpm dev  # Runs on http://localhost:3000
```

---

## Option 2: Manual Dataset Download

If automatic download fails, download these from Kaggle and place the CSVs in `data/raw/`:
1. **Software Engineer Jobs & Salaries 2024** — https://www.kaggle.com/datasets/emreksz/software-engineer-jobs-and-salaries-2024
2. **Vietnam IT Jobs (TopCV 2026)** — https://www.kaggle.com/datasets/baocgb/vietnam-it-jobs-raw-data-from-topcv-2026

### Rename to match the engine's discovery patterns
The engine finds files by filename substring (`config/settings.py` → `PATTERNS`):
- the **global salary** file must contain `ai_job` and have `job_title` + `salary_usd` columns
- the **local** file must contain `topcv`

```bash
mkdir -p data/raw
# global software-engineer salaries (rename so it contains "ai_job")
mv ~/Downloads/software-engineer*/*.csv data/raw/ai_job_software_engineer_2024.csv
# local Vietnam TopCV jobs (rename so it contains "topcv")
mv ~/Downloads/vietnam-it-jobs*/*.csv data/raw/topcv_vietnam_it_jobs_2026.csv
```
> The Glassdoor SE salary column is a string like `$68K - $94K`. The automatic
> downloader normalizes it to a numeric `salary_usd`; if you place the file
> manually you'll need to add a numeric `salary_usd` column yourself (or just use
> `--download-datasets`, which does it for you).

### Run the Flow
```bash
python3 main.py --flow
```

---

## Option 3: Use Synthetic Data (Testing Only)

If Kaggle datasets are unavailable, use synthetic test data:

```bash
python3 main.py --benchmark   # Generates synthetic data in data/
python3 main.py --flow        # Runs analysis on synthetic data
```

---

## 🤖 AI Analysis (Validate + Analyze with free LLMs)

After you've generated `intelligence.json` (via `--flow`), you can run free LLM providers to
**validate** the numbers (flag implausible salaries / risk scores / bad role names) and
**analyze** the market for you (career strategy, ROI, automation risk). It runs every provider
you have a key for and compares them side by side.

### 1️⃣ Get free API keys (set any subset)

| Provider | Get a free key | Default model |
| :--- | :--- | :--- |
| **Groq** | https://console.groq.com/keys | `llama-3.3-70b-versatile` |
| **OpenRouter** | https://openrouter.ai/keys | `deepseek/deepseek-chat:free` |
| **Google Gemini** | https://aistudio.google.com/app/apikey | `gemini-2.0-flash` |

### 2️⃣ Add them to `.env`
```bash
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```
You only need **one** — the command skips providers without a key. Set more to compare them.

### 3️⃣ Run it
```bash
# Compare every provider that has a key
python3 main.py --ai-analyze

# Only one provider
python3 main.py --ai-analyze --provider gemini

# Tailor the "for you" advice to a specific profile
python3 main.py --ai-analyze --profile "Senior Java backend dev, HCMC, 5 yrs"
```

### 4️⃣ Outputs
- **`data/sync/ai_analysis.json`** — machine-readable: each provider's validation flags + analysis,
  a cross-provider agreement tally, and a metrics table (latency, #recommendations, parse success).
- **`analytics/reports/ai_analysis_<timestamp>.md`** — readable report comparing providers side by side.

> **Notes:** Free tiers rate-limit; the tool retries on HTTP 429 (3× backoff) and captures any other
> error per-provider without crashing. If a model returns prose instead of JSON, the raw text is
> preserved in the output. The default analysis profile is a **Vietnam-based backend/Java developer**.

---

## Available Commands

```bash
# Download real Kaggle datasets
python3 main.py --download-datasets

# Generate synthetic test data
python3 main.py --benchmark

# Extract ZIPs from data/ to data/raw/
python3 main.py --extract

# Run the full Intelligence Flow
python3 main.py --flow

# Validate + analyze with free LLMs (Groq/OpenRouter/Gemini)
python3 main.py --ai-analyze

# Crawl live ITviec jobs (requires credentials)
python3 main.py --itviec --limit 30

# Show help
python3 main.py --help
```

---

## Troubleshooting

### ❌ "Kaggle CLI not installed"
```bash
pip install kaggle
```

### ❌ "Kaggle credentials not configured"
- Go to https://www.kaggle.com/settings/account
- Click "Create New API Token"
- Move `kaggle.json` to `~/.kaggle/` (see Step 2B above)
- Run: `chmod 600 ~/.kaggle/kaggle.json` (macOS/Linux)

### ❌ "Dataset not found on Kaggle"
- Kaggle datasets may have been renamed or removed
- Use synthetic data: `python3 main.py --benchmark`
- Or find alternative datasets and manually place them in `data/raw/`

### ❌ Python dependencies missing
```bash
pip install -r requirements.txt
```

### ❌ Next.js errors on localhost:3000
- Database not required for basic testing
- The dashboard falls back to JSON files and defaults
- Errors in browser console are expected during dev

---

## File Structure After Setup

```
job-market-crawler/
├── data/
│   └── raw/
│       ├── ai_job_market_2025.csv           # Downloaded from Kaggle
│       ├── ai_impact_2024_2030.csv          # Downloaded from Kaggle
│       └── ai_data_science_2020_2026.csv    # Downloaded from Kaggle
├── data/sync/
│   └── intelligence.json                     # Generated by --flow
├── public/data/
│   └── intelligence.json                     # Generated by --flow
├── analytics/reports/
│   ├── market_intelligence_*.md              # Generated report
│   ├── salary_distribution_insight_*.png     # Generated charts
│   ├── salary_evolution_*.png
│   ├── global_skills_ranking_*.png
│   └── skill_network_*.png
├── src/app/
│   └── page.tsx                              # Dashboard (reads intelligence.json)
└── main.py                                   # CLI entrypoint
```

---

## Next Steps

After setup is complete:

1. **Review the Report** — Check `analytics/reports/market_intelligence_*.md`
2. **View Charts** — Look at PNG files in `analytics/reports/`
3. **Run Dashboard** — `pnpm dev` to visualize data on localhost:3000
4. **Integrate Data** — Use `data/sync/intelligence.json` or `public/data/intelligence.json` in your own apps
5. **Extend Analysis** — Modify `analytics/intelligence_engine.py` to add custom metrics

---

## Support

For issues or questions:
- Check [AGENTS.md](AGENTS.md) for architecture overview
- Check [SPEC.md](SPEC.md) for technical details
- Run `python3 main.py --help` for command reference
