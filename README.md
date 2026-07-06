# Job Market Crawler & Skill Analytics

A specialized toolkit to crawl job markets (starting with ITviec) and analyze technology trends. This project helps you identify the most essential skills and tools required for specific roles (e.g., Java Developer) by analyzing real-time job descriptions.

> **Working on the code?** See [SETUP.md](SETUP.md) for quick-start, [AGENTS.md](AGENTS.md) for architecture, [SPEC.md](SPEC.md) for technical details. This README is a product overview.

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
- **Software-engineer focus**: Correlates the **Vietnam market (TopCV)** against a **global software-engineer salary benchmark**, surfacing roles like Backend, Fullstack, Java, DevOps.
- **Skill mining**: Extracts in-demand SE skills (Java, .NET/C#, Node.js, React, AWS, ...) directly from local job titles.
- **ROI Roadmaps**: Automated identification of "High ROI" skills (High Global Pay / Moderate Local Competition).
- **Advanced Extraction**: Regex-based parsing of salaries (USD/VND) and experience years from unstructured JD text.
- **AI Validation & Analysis**: Free LLMs (Groq/OpenRouter/Gemini) validate the numbers and generate career strategy.
- **Visual Analytics Heatmaps**: Market demand hierarchy and "Opportunity Gap" visualizations.

## 🛠 Tech Stack
- **Data**: Pandas, NumPy, Scikit-Learn
- **Visualization**: Matplotlib, Seaborn
- **Crawler**: curl-cffi (Cloudflare Bypass), BeautifulSoup4
- **Intelligence**: Custom correlation engine for market gaps.

## 🚀 Quick Start (3 commands)

### **With Real Kaggle Datasets**
```bash
# 1. Install
pip install -r requirements.txt

# 2. Add your Kaggle API token to .env:  KAGGLE_API_TOKEN=KGAT_xxx
#    (https://www.kaggle.com/settings/account -> Create New API Token)

# 3. Download datasets: Vietnam TopCV (Kaggle) + Stack Overflow survey (global SE benchmark)
python3 main.py --download-datasets
#    (or just the SO survey, no token needed:  python3 main.py --fetch)

# 4. Run analysis
python3 main.py --flow
```

📊 Reports generated in `analytics/reports/` and `data/sync/intelligence.json`

### **With Synthetic Data (Testing)**
```bash
python3 main.py --benchmark     # Generate test data
python3 main.py --flow          # Run analysis
```

### **Dashboard (Optional)**
```bash
pnpm install
pnpm dev        # http://localhost:3000
```

---

## 📋 Available Commands

| Command | Purpose |
|---------|---------|
| `--download-datasets` | Download real Kaggle datasets (automated) |
| `--flow` | Run full Intelligence Flow (analyze + export + visualize) |
| `--ai-analyze` | Validate + analyze the data with free LLMs (Groq/OpenRouter/Gemini) |
| `--benchmark` | Generate synthetic test data |
| `--extract` | Extract ZIP archives in `data/` to `data/raw/` |
| `--itviec` | Scrape live ITviec jobs (needs credentials) |

### 🤖 AI Validation & Analysis

After running `--flow`, feed the results to free LLMs to sanity-check the numbers and get career-strategy insight:

```bash
python3 main.py --ai-analyze                       # compare all providers with a key
python3 main.py --ai-analyze --provider gemini     # just one
python3 main.py --ai-analyze --profile "Java dev, HCMC, 5y"   # custom profile
```

Set any of `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY` in `.env` (all free — see `.env.example` for signup links). Outputs `data/sync/ai_analysis.json` + a readable `analytics/reports/ai_analysis_*.md` comparing each provider side by side.

See [SETUP.md](SETUP.md) for detailed setup instructions and troubleshooting.

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
