# Job Market Crawler & Skill Analytics

A specialized toolkit to crawl job markets (starting with ITviec) and analyze technology trends. This project helps you identify the most essential skills and tools required for specific roles (e.g., Java Developer) by analyzing real-time job descriptions.

## Project Structure

```text
job-market-crawler/
├── main.py              # Orchestrates crawling and analysis
├── crawlers/            # Modular crawler scripts
│   └── itviec.py        # ITviec-specific scraping logic
├── analytics/           # Data processing & visualization
│   └── skill_analyzer.py# Trends analysis logic
│   └── kaggle_analyzer.py# Kaggle global trend insights
├── data/                # Raw scraped data (CSV/JSON)
├── outputs/             # Generated graphs and reports
├── requirements.txt     # Dependencies
└── README.md            # Documentation
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

2. **Fetch Global Benchmarks (SO 2025)**:
   ```bash
   python main.py --fetch
   ```

3. **Run Market Intelligence Analysis (Default)**:
   ```bash
   python main.py
   ```

4. **Scrap Fresh Local Data (Optional)**:
   ```bash
   python main.py --crawl --pages 15
   ```

5. **Run Kaggle Global Intelligence Suite**:
   ```bash
   python analytics/kaggle_analyzer.py
   ```

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
