# Integrations: Kaggle

How the system downloads and uses Kaggle datasets.

## Kaggle API authentication

The downloader uses the Kaggle **HTTP API** (not the CLI).

### Setup

1. Go to https://www.kaggle.com/settings/account
2. Click "Create New API Token"
3. A file `kaggle.json` downloads (or you can see the token in the prompt)
4. Copy the token value (starts with `KGAT_`)
5. Add to `.env`:
   ```bash
   KAGGLE_API_TOKEN=KGAT_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Note:** No `kaggle` CLI or `~/.kaggle/kaggle.json` needed. The token is used directly via HTTP.

---

## Datasets

### 1. TopCV 2026 (Local market)

**Dataset ID:** `baocgb/vietnam-it-jobs-raw-data-from-topcv-2026`

**What:** Vietnamese IT job listings with titles, salaries (in VND), required experience.

**Downloaded as:** `topcv_jobs.csv` → renamed to `topcv_vietnam_it_jobs_2026.csv`

**Schema:**
```csv
Job Title, Salary Range, Experience Required, Job Description, Company, Location, ...
Backend Engineer, 30-50 triệu VND, 3 years, We are hiring..., TechCorp, HCMC, ...
```

**Parser:** `TopCVParser` in `analytics/topcv_parser.py`

**Column mapping** (flexible — tries multiple names):
- Job title: `Job Title`, `Job title`, `job_title`
- Salary: `Salary Range`, `Salary`, `salary_min`, `salary_max`
- Experience: `Experience Required`, `experience_required`, `min_years_exp`

**Standardization:** Titles standardized to canonical roles (Backend Developer, Frontend Developer, etc.). Salaries converted from VND to USD at rate 25,000 VND/USD.

**Size:** ~740 rows (as of 2026)

### 2. AI Job Risk & Salary Trends

**Dataset ID:** `shree0910/ai-job-risk-and-salary-dataset` (or search "AI Job Risk and Salary Dataset 2015-2035")

**What:** Automation risk % per job role, multi-year salary trends (2015–2035).

**Downloaded as:** Unzipped file → renamed to `ai_impact_job_risk.csv`

**Schema:**
```csv
Job Title, Automation Risk (%), Year, Salary, Industry, Status, ...
Data Scientist, 68, 2025, 120000, AI/ML, High Risk, ...
Backend Engineer, 25, 2025, 115000, Software, Stable, ...
```

**Key column:** `Automation Risk (%)` — Percentage of automation risk (0–100).

**Used for:**
- `resilienceScore` in intelligence.json (inverse of automation risk)
- `riskLevel` (categorized as LOW/MODERATE/HIGH)
- `trends` vector (salary evolution)
- `impact` vector (risk per industry)

### 3. Global AI & IT Salaries

**Dataset ID:** `mohankrishnathalla/global-ai-and-data-jobs-salary-dataset`

**What:** Global IT/data-science job salaries by role.

**Downloaded as:** ZIP → unzipped → `ai_job_global_it_salary.csv`

**Schema:**
```csv
job_title, salary_usd, years_experience, job_location, ...
Backend Developer, 110000, 5, USA, ...
Senior Software Engineer, 145000, 8, Canada, ...
```

**Key columns:** `job_title`, `salary_usd`

**Used for:** Global salary benchmarks (pooled with SO survey).

---

## Download process

**Command:** `python3 main.py --download-datasets`

**Flow:**

1. **TopCV dataset**
   - Query Kaggle API: `baocgb/vietnam-it-jobs-raw-data-from-topcv-2026`
   - Download ZIP to `data/topcv_jobs.zip`
   - Unzip to `data/raw/`
   - Rename to `topcv_vietnam_it_jobs_2026.csv`

2. **AI impact dataset**
   - Query: `shree0910/ai-job-risk-and-salary-dataset`
   - Download ZIP
   - Unzip, find CSV with `Automation Risk (%)` column
   - Rename to `ai_impact_job_risk.csv`

3. **Global IT salary dataset**
   - Query: `mohankrishnathalla/global-ai-and-data-jobs-salary-dataset`
   - Download ZIP
   - Unzip to `ai_job_global_it_salary.csv`

4. **Stack Overflow survey**
   - Download publicly (no auth): https://survey.stackoverflow.co/
   - Unzip to `ai_job_so_survey_2025.csv`

**Output:**
```
data/raw/
├── topcv_vietnam_it_jobs_2026.csv
├── ai_impact_job_risk.csv
├── ai_job_global_it_salary.csv
└── ai_job_so_survey_2025.csv
```

---

## Dynamic discovery

The engine discovers datasets by **filename pattern**, not fixed names. This allows you to:
1. Add custom datasets in `data/raw/`
2. They're automatically loaded and pooled

**Patterns** (defined in `config/settings.py`):

| Pattern | Used for | Required columns |
|---------|----------|-------------------|
| `*topcv*` | Local Vietnam jobs | Job title, salary, experience |
| `*ai_job*` | Global salary benchmarks | `job_title`, `salary_usd` |
| `*impact*` | Automation risk | `Automation Risk (%)` |

**Example:** Drop a file `data/raw/custom_jobs_ai_job_2025.csv` with columns `job_title` and `salary_usd`, and it will be pooled with the global benchmarks on next `--flow`.

---

## Manual download (if automatic fails)

1. Go to each Kaggle dataset page
2. Click "Download"
3. Move ZIPs to `data/`
4. Run `python3 main.py --extract`

---

## Troubleshooting

### Issue: `403 Forbidden` from Kaggle API

**Cause:** Token invalid or expired.

**Fix:**
1. Go to https://www.kaggle.com/settings/account
2. Delete old token
3. Create new token
4. Update `.env`

### Issue: `File not found in archive`

**Cause:** Dataset structure changed; expected CSV not found.

**Fix:**
1. Download manually
2. Inspect the ZIP: `unzip -l <file>.zip`
3. Move/rename the CSV to match the pattern (`*topcv*`, `*ai_job*`, `*impact*`)

### Issue: `Automation Risk (%)` column missing

**Cause:** Wrong dataset or outdated version.

**Fix:**
1. Re-download: `python3 main.py --download-datasets`
2. Or manually download from Kaggle and ensure the CSV has the column

---

## Data privacy

All Kaggle data is downloaded and stored locally in `data/raw/`. No data is uploaded or shared externally (except to Vercel's `/tmp` if deployed).

`.gitignore` excludes `data/` so datasets aren't committed.

---

## See also

- [Integrations: Stack Overflow](stackoverflow.md) — SO survey details
- [Operations: Setup](../operations/setup.md) — Kaggle setup
- [Workflows: Python Engine](../workflows/python-engine.md) — How data is loaded
