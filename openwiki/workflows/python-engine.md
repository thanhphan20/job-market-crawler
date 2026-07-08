# Python Engine Workflows

How the Intelligence Engine works: data loading, correlation, and export.

## CLI entry points (main.py)

| Command | Purpose | Example |
|---------|---------|---------|
| `--flow` | Full analysis: load, correlate, export JSON + PNGs | `python3 main.py --flow` |
| `--download-datasets` | Download Kaggle datasets (TopCV, AI impact, global IT salaries) | `python3 main.py --download-datasets` |
| `--fetch` | Download Stack Overflow survey only (no Kaggle auth) | `python3 main.py --fetch` |
| `--extract` | Unzip datasets in `data/` → `data/raw/` | `python3 main.py --extract` |
| `--benchmark` | Generate synthetic test data | `python3 main.py --benchmark` |
| `--itviec` | Scrape live ITviec jobs | `python3 main.py --itviec` |
| `--ai-analyze` | Validate + analyze results with LLMs (Groq, OpenRouter, Gemini) | `python3 main.py --ai-analyze` |

**Options:**
- `--dir <path>` — Override data directory (default: `data/raw/`)
- `--limit <n>` — Limit rows loaded from each source (for testing)
- `--provider <name>` — For `--ai-analyze`, run only one LLM provider
- `--profile <desc>` — For `--ai-analyze`, custom career profile (default: "Java dev, HCMC, 5y")

## `--flow` workflow (main analysis)

```
main.py --flow
    │
    ├─ 1. Load all data sources
    │   ├─ TopCVParser.load() — Vietnam job listings (data/raw/*topcv*.csv)
    │   ├─ KaggleUnifier.load_all_sources() — Global salary datasets (data/raw/*ai_job*.csv)
    │   ├─ _load_impact_lookup() — Automation risk dataset (data/raw/*impact*.csv)
    │   └─ _load_itviec() — ITviec jobs if data/itviec_jobs.csv exists
    │
    ├─ 2. Standardize titles, salaries, experience
    │   ├─ standardize_title() — Map varied titles to canonical roles
    │   ├─ parse_salary_vnd() — Convert VND → USD
    │   └─ parse_experience() — Extract years from free text
    │
    ├─ 3. Correlate local vs. global
    │   ├─ Group local data by standardized_title
    │   ├─ Right-join onto global benchmarks by std_role
    │   ├─ Calculate opportunity gaps (global - local)
    │   └─ Sort by global_job_count (descending)
    │
    ├─ 4. Extract signals
    │   ├─ _extract_skill_matrix() — Top skills from job descriptions
    │   ├─ _build_salary_trends() — Multi-year SE salary evolution
    │   ├─ _risk_for_role() — Automation risk per role
    │   └─ _correlation_points() — Demand vs. local salary scatter
    │
    ├─ 5. Export JSON (data contract)
    │   ├─ Write data/sync/intelligence.json
    │   └─ Copy to public/data/intelligence.json
    │
    ├─ 6. Generate visualizations
    │   ├─ visualizer.plot_demand_heatmap()
    │   ├─ visualizer.plot_salary_trends()
    │   ├─ visualizer.plot_automation_risk()
    │   ├─ visualizer.plot_skills_heatmap()
    │   ├─ visualizer.plot_market_share()
    │   ├─ visualizer.plot_correlation()
    │   ├─ visualizer.plot_opportunity_gap()
    │   └─ visualizer.plot_skills_evolution()
    │
    └─ 7. Write markdown report
        └─ analytics/reports/market_intelligence_<timestamp>.md
```

## Data loading (load_all_sources)

### TopCV Parser

**File pattern:** `data/raw/*topcv*.csv`

**Expected columns:** (flexible mapping)
- Job title/Job Title/job_title → standardized as `standardized_title`
- Experience/experience_required → parsed as `min_years_exp`
- Salary/Salary Range/salary_min → parsed as `annual_salary_usd` (if VND, convert at 25000 VND/USD)

**Output schema:**
```python
{
  "standardized_title": "Backend Developer",
  "min_years_exp": 3,
  "annual_salary_usd": 50000,  # local estimate in USD
  "job_description": "full text",
  "source": "topcv",
  ... # other columns preserved
}
```

**Discovery:** Dynamic. If `data/raw/` contains `*topcv*.csv`, it's loaded. Multiple files are concatenated.

### Kaggle Unifier (Global Benchmarks)

**File pattern:** `data/raw/*ai_job*.csv`

**Required columns:** `job_title`, `salary_usd`

**Optional columns:** `required_skills`, `years_experience`, `job_location`, `job_count`

**Behavior:**
1. Discover all files matching `*ai_job*.csv`
2. Concatenate into single DataFrame
3. Standardize titles
4. Group by `standardized_title` (std_role)
5. Compute per-role statistics: salary mean/median/min/max, job count
6. Output: `global_benchmarks` dict keyed by std_role

**Sources (shipped by default):**
- **Stack Overflow 2025** → `ai_job_so_survey_2025.csv` (18k+ SE respondents)
- **Kaggle global IT salaries** → `ai_job_global_it_salary.csv` (56k+ rows)

Drop in any other `ai_job*.csv` with the required columns and it's pooled automatically.

### ITviec Crawler

**File:** `data/itviec_jobs.csv` (produced by `python3 main.py --itviec`)

**Schema:**
```csv
job_title,company,job_description,link,data-job-key
Backend Engineer,TechCorp,"We're hiring...",https://...,12345
...
```

**Loaded as:**
```python
{
  "standardized_title": "Backend Developer",  # standardized from job_title
  "min_years_exp": 2,  # hardcoded
  "annual_salary_usd": None,  # not parsed from ITviec
  "job_description": "...",
  "source": "itviec"
}
```

**Note:** ITviec rows contribute little to salary analysis (no parsed salary), but provide skill/keyword signals.

### Automation Risk Dataset

**File pattern:** `data/raw/*impact*.csv`

**Required columns:** `Automation Risk (%)` (or equivalent)

**Optional columns:** `job_title`, `role`, `industry`, `year`, `salary`

**Loaded as:** Lookup table for `_risk_for_role()`.

Priority order:
1. Exact match on standardized title → use role's automation risk
2. No match → use "Software Engineer" baseline
3. Fallback → heuristic score by keyword

## Correlation (run_agentic_analysis)

### Step 1: Merge local and global

```python
merged = local_data.merge(
  global_benchmarks,
  left_on='standardized_title',
  right_on='std_role',
  how='right'  # Keep all global roles, even if no local jobs
)
```

Result: DataFrame with:
- Local columns: `standardized_title`, `min_years_exp`, `annual_salary_usd`, `job_description`, `source`
- Global columns: `std_role`, `global_salary_mean`, `global_salary_median`, `global_job_count`
- Computed: `opportunity_gap = global_salary_mean - annual_salary_usd` (if local salary exists)

### Step 2: Calculate opportunity gaps

Roles ranked by `opportunity_gap` descending. High gap + high local demand = "🚀 High ROI" skill.

### Step 3: Extract signals

**Skills:** Top keywords from job descriptions (via regex or survey data), ranked by frequency and growth trend.

**Trends:** Multi-year salary evolution. If AI impact dataset available, extract SE salary curve (2015–2035) and anchor to current SO benchmark. Fallback: single-year SO salary + linear projection.

**Risk:** Automation risk per role from dataset, else heuristic by keyword.

**Correlation:** X = local job demand (count), Y = average local salary, size = global demand. Used for scatter plot.

## Export JSON (data contract)

**Function:** `IntelligenceEngine._export_dashboard_json(merged)`

**Writes:**
- `data/sync/intelligence.json`
- `public/data/intelligence.json` (public in Next.js)

**Schema:** See [Data Models: intelligence.json](../data-models/intelligence-json.md)

**Fallback hardcodes:** If a vector is empty, the exporter writes a hardcoded default (e.g., a sample skill, sample trend) so the frontend never renders an empty array. This ensures graceful degradation if a data source is missing.

## Visualization (visualizer.py)

Generates 8 PNG charts to `analytics/reports/`:

| Chart | Purpose | X-axis | Y-axis |
|-------|---------|--------|--------|
| **Demand Heatmap** | Top roles by job count | Role | Job count |
| **Salary Trends** | SE salary evolution | Year | Salary (USD) |
| **Automation Risk** | Risk per industry | Industry | Automation risk (%) |
| **Skills Heatmap** | Top skills by relevance | Skill | Relevance (0–100) |
| **Market Share** | Pie chart of role distribution | Role | Count |
| **Correlation** | Scatter: demand vs. local salary | Local demand | Local salary |
| **Opportunity Gap** | Bar chart: role gaps ranked | Role | Gap (USD) |
| **Skills Evolution** | Line chart: skill growth over time | Skill | Growth (%) |

**Output:** PNG files named `chart_<name>.png`. Referenced in `market_intelligence_*.md` reports as `![](chart_<name>.png)`.

## Report generation

**Function:** `IntelligenceEngine._write_full_report(merged)`

**File:** `analytics/reports/market_intelligence_<timestamp>.md`

**Contents:**
- Title: "Market Intelligence Report"
- Timestamp
- Executive summary (top 5 roles, top 5 skills)
- Markdown table of standardized data
- Section for each PNG chart with commentary
- Footer with data source attribution

## Error handling

- **Missing source files:** Silently skip. If no TopCV found, load only global data. If no Kaggle, analyze TopCV alone.
- **Standardization failures:** Falls back to original title (no join, no correlation).
- **Salary parsing errors:** Leaves salary null. Null salaries don't enter salary statistics.
- **Export failures:** Writes fallback JSON with hardcoded defaults so frontend doesn't break.

## Performance considerations

- **CSV loading:** `pd.read_csv()` streams files. For large CSVs (100k+ rows), add `--limit <n>` to test with a subset.
- **Groupby/merge:** O(n log n) for standardization and groupby. Merges are inner/right joins, not cross-products.
- **PNG generation:** Matplotlib can be slow (1–5s per chart for 1k+ series). Run in parallel if needed (not currently threaded).
- **JSON export:** Fast (`json.dump`), typically <1s.

## Testing

- **Benchmark mode:** `python3 main.py --benchmark` generates synthetic data. Use this to test the engine in isolation without Kaggle auth or large downloads.
- **Limit mode:** `python3 main.py --flow --limit 30` loads only 30 rows from each source. Fast for debugging.
- **Local-only:** If no global datasets, the engine still runs and exports local data. Good for checking TopCV parsing.

---

## See also

- [Architecture: System Design](../architecture/system-design.md) — Data flow diagrams
- [Data Models: intelligence.json](../data-models/intelligence-json.md) — Output schema
- [Operations: Setup](../operations/setup.md) — How to run locally
- [Integrations: Kaggle](../integrations/kaggle.md) — Dataset details
