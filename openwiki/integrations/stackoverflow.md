# Integrations: Stack Overflow

How the system fetches and uses the Stack Overflow Developer Survey.

## Stack Overflow Developer Survey

**What:** Annual global survey of ~18k software engineers asking about salaries, languages, tools, experience.

**Source:** https://survey.stackoverflow.co/ (public, no auth required)

**Year:** 2025 (the latest survey used)

**Size:** ~18k respondents (global), filtered to ~13k software-engineering roles

## Download

**Manual download:**
```bash
# Via website
# 1. Visit https://survey.stackoverflow.co/
# 2. Download CSV (~130 MB)
# 3. Save to data/so_survey_2025.csv
```

**Automatic download:**
```bash
python3 main.py --fetch
# or (as part of full dataset download):
python3 main.py --download-datasets
```

**Script:** `scripts/fetch_data.py`

**URL:** Downloaded from the SO survey website (URL may change; check if `--fetch` fails).

---

## Processing

After download, the survey is **filtered and normalized**:

1. **Filter to software-engineering roles only**
   - Keep: Backend, Frontend, Fullstack, Mobile, Embedded, DevOps, Cloud, ML, Data
   - Drop: Data science, QA, product management, sales, etc.
   - **Reason:** We focus on software engineer salary trends

2. **Normalize columns:**
   - `employment.type` → coding professional (full-time equivalent)
   - `salary.usd` → annual salary in USD
   - `work.languages_hobbies` → required skills

3. **Output:** `data/raw/ai_job_so_survey_2025.csv`

**Schema (after processing):**
```csv
job_title, salary_usd, required_skills, years_experience, work_experience, ...
Backend Developer, 115000, Python;Java;SQL, 5, Full-time, ...
Frontend Developer, 100000, JavaScript;React;TypeScript, 4, Full-time, ...
```

---

## Using SO data

The engine pools SO survey data with other global sources (Kaggle AI salary dataset) under the `*ai_job*.csv` pattern.

### KaggleUnifier discovery

In `analytics/kaggle_unifier.py`:

```python
# Discover all *ai_job*.csv files
global_files = find_files_by_pattern('*ai_job*')
# Returns: ['ai_job_so_survey_2025.csv', 'ai_job_global_it_salary.csv']

# Load and pool
dfs = [pd.read_csv(f) for f in global_files]
pooled = pd.concat(dfs)  # Combine into single DataFrame

# Standardize titles
pooled['std_role'] = pooled['job_title'].apply(standardize_title)

# Group by role → compute statistics
global_benchmarks = pooled.groupby('std_role').agg({
  'salary_usd': ['mean', 'median', 'min', 'max'],
  'job_title': 'count'  # job count per role
})
```

### Intelligence vector

SO data contributes to the `intelligence` vector:
- `globalAvgSalary` — SO survey mean salary
- `demand` — SO survey job count per role

### Skills extraction

If available, SO's `required_skills` or `work.languages_hobbies` columns are extracted as top technologies.

---

## Key fields

| Field | Description | Example |
|-------|-------------|---------|
| `job_title` / `DevType` | Role category | Backend Developer, Frontend Developer |
| `salary_usd` | Annual salary (USD) | 115000 |
| `work.years_coding` | Years of experience | 5 |
| `employment_type` | Full-time, part-time, etc. | Full-time |
| `LanguageHaveWorkedWith` | Semicolon-delimited languages | Java;Python;C# |
| `LanguageWantToWorkWith` | Desired languages | Go;Rust |

---

## Fallback if SO unavailable

If the SO survey download fails:

1. Engine logs warning
2. Falls back to **Kaggle global IT salary dataset only**
3. Analysis continues (less comprehensive, but functional)

**To force SO-only mode:**
```bash
python3 main.py --fetch  # Downloads SO only, no Kaggle
python3 main.py --flow   # Analyzes with SO data
```

---

## Historical surveys

Stack Overflow publishes new surveys annually. The system currently targets the **2025 survey**.

To use a different year:
1. Download the CSV from https://survey.stackoverflow.co/
2. Save to `data/raw/ai_job_so_survey_<year>.csv`
3. Run `python3 main.py --flow`

The engine will auto-discover and load it by the `*ai_job*` pattern.

---

## Data quality notes

**SO survey strengths:**
- Large sample size (~18k respondents)
- Global coverage
- Annual updates
- Real self-reported salaries

**SO survey limitations:**
- Self-reported (may have bias)
- Global average (Vietnam-specific may differ)
- Not all engineering roles represented
- Response bias (may skew toward higher salaries)

**Mitigation:** The engine pools SO data with **local data (TopCV)** and **other global sources (Kaggle)** to reduce bias.

---

## See also

- [Integrations: Kaggle](kaggle.md) — Kaggle dataset details
- [Workflows: Python Engine](../workflows/python-engine.md) — How data is loaded and standardized
- [Operations: Setup](../operations/setup.md) — Setup
