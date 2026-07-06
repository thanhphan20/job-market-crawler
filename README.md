# Job Market Crawler & Skill Analytics

A specialized toolkit to crawl job markets (starting with ITviec) and analyze technology trends. This project helps you identify the most essential skills and tools required for specific roles (e.g., Java Developer) by analyzing real-time job descriptions.

> **Working on the code?** Read [AGENTS.md](AGENTS.md) for orientation and run commands, and [SPEC.md](SPEC.md) for the full architecture and data contract. This README is a product overview and some of its historical examples predate the current CLI — trust `python main.py --help`.

## Project Structure

```text
job-market-crawler/
├── main.py               # Python CLI entrypoint (argparse)
├── analytics/            # Intelligence engine
│   ├── intelligence_engine.py  # Orchestrator (correlate + export + report)
│   ├── kaggle_unifier.py       # Loads & unifies global Kaggle datasets
│   ├── topcv_parser.py         # Parses local TopCV data
│   ├── standardizer.py         # Title/salary/experience normalization
│   ├── visualizer.py           # Matplotlib chart generation
│   └── kaggle_analyzer.py      # Standalone Kaggle insights suite
├── crawlers/itviec.py    # ITviec scraper (curl-cffi, Cloudflare bypass)
├── config/settings.py    # Paths + Vercel-aware /tmp fallbacks
├── scripts/              # Utilities (dataset extract, benchmarks, SO fetch)
├── api/index.py         # FastAPI bridge (Python serverless / local uvicorn)
├── src/                 # Next.js 16 dashboard
│   ├── app/             #   App Router pages + API routes
│   ├── components/      #   React UI (dashboard, terminal, charts)
│   └── lib/             #   Prisma client + cached queries
├── prisma/schema.prisma # Supabase Postgres schema
├── data/                # Input CSVs & generated JSON (gitignored)
├── requirements.txt     # Python dependencies
├── package.json         # Node dependencies
├── AGENTS.md            # Agent orientation guide
└── SPEC.md              # Full technical specification
```

## Features

- **Automated Crawling**: Fetches job listings from ITviec for Backend, Fullstack, and Java queries.
- **Skill Analytics**: Scans job descriptions for key technologies (Spring Boot, SQL, AWS, etc.).
- **Market Visualization**: Generates ranking charts of the most in-demand skills.
- **Kaggle Global Intelligence**: Integration with multiple Kaggle datasets to correlate local trends with global AI market forecasts (2020-2030).
- **Duplicate Prevention**: ensuring unique data across different search categories.

## 📊 Latest Market Insights (Data-Driven)

Analyzed from **131** live job postings on ITviec.

### Technology Demand
| Category | Job Mentions | Market Presence |
|----------|--------------|-----------------|
| **Data & Messaging** | 85 | 64.9% |
| **Infrastructure & DevOps** | 77 | 58.8% |
| **Architecture** | 55 | 42.0% |
| **Spring Ecosystem** | 29 | 22.1% |
| **Java Core** | 10 | 7.6% |

# 🚀 Agentic Job Market Intelligence Engine (v2.0)

A powerful data engine that correlates local job requirements with global industry benchmarks (Stack Overflow 2025) to generate high-ROI career roadmaps.

## 🌟 Key Features
- **Intelligence Engine**: Triangular correlation between Skills, Experience, and Global Salary Benchmarks.
- **ROI Roadmaps**: Automated identification of "High ROI" skills (High Global Pay / Moderate Local Competition).
- **Global Benchmarking**: Integrates official **Stack Overflow Developer Survey 2025** and **Kaggle AI Datasets**.
- **Advanced Extraction**: Regex-based parsing of salaries (USD/VND) and experience years from unstructured JD text.
- **AI Impact Profiling**: Automation risk analysis by industry using global research data.
- **Visual Analytics Heatmaps**: Market demand hierarchy and "Opportunity Gap" visualizations.

## 🛠 Tech Stack
- **Data**: Pandas, NumPy, Scikit-Learn
- **Visualization**: Matplotlib, Seaborn
- **Crawler**: curl-cffi (Cloudflare Bypass), BeautifulSoup4
- **Intelligence**: Custom correlation engine for market gaps.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Extract raw datasets** (unzips archives in `data/` into `data/raw/`):
   ```bash
   python main.py --extract
   ```

3. **Run the full Market Intelligence flow** (correlate + export JSON + generate reports):
   ```bash
   python main.py --flow
   ```

4. **Scrape fresh local data (optional)** — needs `ITVIEC_SESSION` / `ITVIEC_TOKEN` in `.env`:
   ```bash
   python main.py --itviec --limit 30
   ```

5. **Generate synthetic benchmark data (for testing)**:
   ```bash
   python main.py --benchmark
   ```

Run `python main.py --help` for the authoritative list of actions and options.

### 🖥️ Dashboard (Next.js)

```bash
pnpm install
pnpm dev        # http://localhost:3000
```

The dashboard reads the intelligence data produced by `python main.py --flow`. To exercise the in-app "Sync" buttons locally, also run the FastAPI bridge: `uvicorn api.index:app --reload --port 8000`. See [SPEC.md](SPEC.md) for how the two halves connect.

## 📊 Outputs
- **`analytics/reports/market_intelligence_*.md`**: Detailed insight report with ROI analysis.
- **`analytics/reports/*.png`**: Visual heatmaps of demand and salary gaps.
- **`outputs/kaggle_reports/`**: Global AI trends, automation risk matrices, and global salary evolution charts.

## 🧠 Intelligence Logic
The system analyzes the **Opportunity Gap** using the following formula:
`Gap = Global_Median_Salary - Local_Estimate`
Skills with the largest positive gap and high local demand are tagged as **🚀 High ROI**.

## Configuration

Update the `session` variable in `crawlers/itviec.py` with your `_ITViec_session` cookie string for the best results and to avoid 403 errors.
