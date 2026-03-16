# ITViec Job Scraper

A specialized Python crawler designed to extract specific job details from [itviec.com](https://itviec.com), with a primary focus on the **"Your skills and experience"** section for Backend, Fullstack, and Java developers.

## Features

- **Focused Extraction**: Specifically targets the technical requirements and skills section of job listings.
- **Multi-Query Support**: Automatically crawls multiple categories:
  - Backend
  - Fullstack Developer
  - Java
- **Duplicate Prevention**: Intelligently tracks job IDs to ensure unique entries even if a job appears in multiple search categories.
- **Export Options**: Generates results in both **CSV** and **JSON** formats for easy analysis or integration.
- **Session Support**: Uses browser-like headers and session cookies to avoid `403 Forbidden` errors.

## Installation

1. **Clone the repository** (if applicable) or copy the files.
2. **Setup a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Configure Session (Optional but Recommended)
To ensure the most reliable results, update the `session` variable in `scraper.py` with your active `_ITViec_session` cookie from your browser.

### 2. Run the Crawler
Execute the main entry point:
```bash
python main.py
```

## Output Fields

The scraper exports the following fields:
- **Title**: The job position name.
- **Company**: The hiring organization.
- **Skills and Experience**: The full text extracted from the skills section of the JD.

## Project Structure

- `main.py`: The main execution script that runs the crawl and exports data.
- `scraper.py`: Core logic for fetching listings and individual job details.
- `requirements.txt`: Python package dependencies.
