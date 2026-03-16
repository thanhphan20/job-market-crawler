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

After running, check:
- `data/itviec_jobs.csv`: Raw data.
- `outputs/java_skills_chart.png`: Visual skill ranking.

## Configuration

Update the `session` variable in `crawlers/itviec.py` with your `_ITViec_session` cookie string for the best results and to avoid 403 errors.
