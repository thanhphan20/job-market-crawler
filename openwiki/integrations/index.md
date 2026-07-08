# Integrations

External data sources and services the system connects to.

## Overview

The Intelligence Engine pulls data from multiple sources:

| Source | Type | Auth | Purpose | File Pattern |
|--------|------|------|---------|--------------|
| **TopCV** | Kaggle | `KAGGLE_API_TOKEN` | Vietnam IT job listings | `*topcv*.csv` |
| **Stack Overflow** | Public API | None | Global SE salaries + skills | `*ai_job*.csv` |
| **Kaggle (global IT salaries)** | Kaggle | `KAGGLE_API_TOKEN` | Global salary benchmarks | `*ai_job*.csv` |
| **Kaggle (AI risk)** | Kaggle | `KAGGLE_API_TOKEN` | Automation risk per role | `*impact*.csv` |
| **ITviec** | Web scraper | Browser cookies | Live Vietnam job postings | `itviec_jobs.csv` |
| **Groq/OpenRouter/Gemini** | LLM APIs | API keys (optional) | AI validation & analysis | — |

---

## Data sources by use case

### Local market (Vietnam)

**Files:** `*topcv*.csv` (required), `itviec_jobs.csv` (optional)

**Source:** 
- TopCV 2026 dataset (Kaggle)
- ITviec web scraper (optional)

**What:** Vietnamese IT job titles, salaries, required experience

**Schema:**
```csv
Job Title, Experience Required, Salary Range, Job Description, ...
Backend Engineer, 3 years, 30-50 triệu VND, We are looking for...
```

See [Integrations: TopCV](topcv.md).

### Global benchmarks

**Files:** `*ai_job*.csv` (required)

**Sources:**
- Stack Overflow Developer Survey 2025
- Kaggle: global-ai-and-data-jobs-salary-dataset

**What:** Global SE salaries, required skills, role distribution

**Schema:**
```csv
Job Title, Salary USD, Required Skills, Years of Experience, ...
Backend Developer, 115000, Python;Java;SQL, 5, ...
```

See [Integrations: Stack Overflow](stackoverflow.md).

### Automation risk

**Files:** `*impact*.csv` (optional but recommended)

**Source:** Kaggle: ai-job-risk-and-salary-dataset

**What:** Automation risk % per tech role, 2015–2035 trends

**Schema:**
```csv
Job Title, Automation Risk (%), Year, Salary Trend, ...
Data Scientist, 68, 2025, ...
```

See [Integrations: Kaggle](kaggle.md).

### Live scraping (optional)

**Source:** ITviec web scraper

**What:** Live job postings from ITviec (updated daily)

**Requires:** `ITVIEC_SESSION` and `ITVIEC_TOKEN` in `.env`

See [Integrations: ITviec Scraper](itviec.md).

---

## LLM providers (optional analysis)

After running `--flow`, you can validate results with AI:

```bash
python3 main.py --ai-analyze
```

**Providers:**
- **Groq** — Fast, free tier
- **OpenRouter** — Multi-model, free tier
- **Gemini** — Google's LLM, free tier

**What:** LLMs validate data plausibility, generate career strategy insights

**Output:** `analytics/reports/ai_analysis_*.md` (side-by-side provider comparison)

See [Integrations: LLM Providers](llms.md).

---

## Configuration

All integrations are configured via environment variables (`.env`):

```bash
# Kaggle (required for --download-datasets)
KAGGLE_API_TOKEN=KGAT_xxx...

# ITviec (optional, only if using --itviec)
ITVIEC_SESSION=...
ITVIEC_TOKEN=...

# LLM providers (optional, for --ai-analyze)
GROQ_API_KEY=gsk_xxx...
OPENROUTER_API_KEY=sk-xxx...
GEMINI_API_KEY=AIzaSyDxxx...
```

See [Operations: Setup](../operations/setup.md) for detailed setup.

---

## See also

- [Integrations: Kaggle](kaggle.md) — Dataset details
- [Integrations: Stack Overflow](stackoverflow.md) — SO survey details
- [Integrations: ITviec](itviec.md) — Scraper setup
- [Integrations: LLM Providers](llms.md) — AI validation setup
