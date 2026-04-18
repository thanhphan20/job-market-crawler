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
├── data/                # Raw scraped data (CSV/JSON)
├── outputs/             # Generated graphs and reports
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

## Features

- **Automated Crawling**: Fetches job listings from ITviec for Backend, Fullstack, and Java queries.
- **Skill Analytics**: Scans job descriptions for key technologies (Spring Boot, SQL, AWS, etc.).
- **Market Visualization**: Generates ranking charts of the most in-demand skills.
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

> [!TIP]
> **Data & Messaging** (SQL, Kafka, Redis) and **Infrastructure** (AWS, Docker, K8s) are the most dominant requirements. A modern Java developer must look beyond the language to the surrounding ecosystem.

### Visual Analytics
- [Skill Network Map](./outputs/skill_network.png) - Shows how technologies cluster together.
- [Market Demand Chart](./outputs/market_groups.png) - Ranking of top technology groups.

### 🚀 Data-Driven Roadmap
Based on current data, we have generated a specialized learning path:
👉 **[View Full Java Roadmap](./outputs/java_roadmap.md)**

## Installation

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the complete pipeline:
```bash
python main.py
```

or

```bash
python crawlers/itviec.py
python analytics/skill_analyzer.py
```

After running, check:
- `data/itviec_jobs.csv`: Raw data.
- `outputs/java_skills_chart.png`: Visual skill ranking.

## Configuration

Update the `session` variable in `crawlers/itviec.py` with your `_ITViec_session` cookie string for the best results and to avoid 403 errors.
