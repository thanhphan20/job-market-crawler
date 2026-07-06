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
The system will download datasets from Kaggle automatically. You need Kaggle API credentials:

**Step A:** Go to https://www.kaggle.com/settings/account and click **"Create New API Token"**
- This downloads `kaggle.json` to your Downloads folder

**Step B:** Move the credentials file to the correct location:
```bash
# macOS/Linux
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Windows
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

**Step C:** Verify setup:
```bash
kaggle --version  # Should show version
```

### 3️⃣ Download Real Datasets
```bash
python3 main.py --download-datasets
```

**Output:**
```
============================================================
 KAGGLE DATASET DOWNLOADER
============================================================

[✓] Kaggle CLI configured

[*] SALARY: Data Science Job Salaries (607 records with global salary data)
  Downloading ruchi798/data-science-job-salaries...
  Extracting ds_salaries.zip...
  ✓ Extracted and renamed to ai_job_market_2025.csv

[*] IMPACT: AI Impact & Automation Risk by Job/Industry
  Downloading bimarsalim/ai-powered-job-market-insights...
  ✓ Extracted and renamed to ai_impact_2024_2030.csv

[*] INSIGHTS: Data Science Salary Evolution (2020-2026 trends)
  Downloading cedricaubin/data-science-salary-2020-2026...
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
==================================================
 MARKET INTELLIGENCE ENGINE v6.1
==================================================

--- Intelligence Engine: Syncing Full Flow ---
[+] Cleaned 607/607 records from Kaggle.
[DONE] Full Knowledge Base Synchronized. Total Local Records: 0
[DASHBOARD] Exported to data/sync/intelligence.json
[*] Generating 8-Vector Visualization Suite...

========================================
 STRATEGIC MARKET SUMMARY
========================================
 > Data Scientist: Opportunity Gap +$125,400/year
 > ML Engineer: Opportunity Gap +$118,300/year
 > AI Researcher: Opportunity Gap +$142,600/year
========================================

[SUCCESS] Analysis Complete: analytics/reports/market_intelligence_20260706_112033.md
```

### 5️⃣ View the Dashboard (Optional)
```bash
pnpm dev  # Runs on http://localhost:3000
```

---

## Option 2: Manual Dataset Download

If automatic download fails, you can download manually:

### 1️⃣ Download Datasets
Visit Kaggle and download these three datasets:
1. **Data Science Job Salaries** — https://www.kaggle.com/datasets/ruchi798/data-science-job-salaries
2. **AI-Powered Job Market Insights** — https://www.kaggle.com/datasets/bimarsalim/ai-powered-job-market-insights
3. **Data Science Salary 2020-2026** — https://www.kaggle.com/datasets/cedricaubin/data-science-salary-2020-2026

### 2️⃣ Extract and Place in `data/raw/`
```bash
# Create data/raw directory
mkdir -p data/raw

# Extract all downloads to data/raw/
unzip ~/Downloads/data-science-job-salaries.zip -d data/raw/
unzip ~/Downloads/ai-powered-job-market-insights.zip -d data/raw/
unzip ~/Downloads/data-science-salary-2020-2026.zip -d data/raw/
```

### 3️⃣ Rename Files
The engine looks for specific filename patterns. Rename the CSV files:

```bash
cd data/raw

# Rename salary data (should contain: job_title, salary_usd, experience_level)
mv ds_salaries.csv ai_job_market_2025.csv

# Rename impact data (should contain: automation risk or impact)
mv *impact*.csv ai_impact_2024_2030.csv 2>/dev/null || mv *automation*.csv ai_impact_2024_2030.csv

# Rename trends data (should contain: work_year, salary)
mv *salary*.csv ai_data_science_2020_2026.csv 2>/dev/null || mv *2020*.csv ai_data_science_2020_2026.csv
```

### 4️⃣ Run the Flow
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
