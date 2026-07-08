# Integrations: ITviec Scraper

How to scrape live job listings from ITviec.

## ITviec overview

**Site:** https://www.itviec.com

**What:** Vietnamese IT job board with live job postings

**Coverage:** Vietnam-focused, mostly tech roles

**Live data:** Updated daily

## Setup

### 1. Get credentials

ITviec uses Cloudflare protection. To bypass it, you need browser session cookies.

1. **Visit ITviec:**
   - Go to https://www.itviec.com
   - Log in (create account if needed)

2. **Extract credentials:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Refresh page
   - Find any request to `itviec.com`
   - Look at Cookies (in that request or in Application > Cookies)
   - Copy `_ITViec_session` value
   - Also note any `Authorization` header (token)

3. **Add to `.env`:**
   ```bash
   ITVIEC_SESSION=<session_cookie_value>
   ITVIEC_TOKEN=<token_value>
   ```

### 2. Run scraper

```bash
python3 main.py --itviec
```

**What it does:**
1. Reads `ITVIEC_SESSION` and `ITVIEC_TOKEN` from env
2. Uses `curl_cffi` with `impersonate="chrome"` to bypass Cloudflare
3. Scrapes job queries: `backend`, `fullstack-developer`, `java`, `software-engineer`
4. Deduplicates by `data-job-key`
5. Follows each job link to get full description
6. Saves to `data/itviec_jobs.csv`

**Time:** ~1–2 min for ~500 jobs

**Output:** `data/itviec_jobs.csv`

---

## Scraper implementation

**File:** `crawlers/itviec.py`

**Key class:** `ITviecCrawler`

```python
class ITviecCrawler:
    def __init__(self, session_cookie: str, token: str):
        self.session = session_cookie
        self.token = token
        self.cf_session = CloudflareBypassSession()  # curl_cffi
    
    def crawl(self) -> pd.DataFrame:
        jobs = []
        for query in ["backend", "fullstack-developer", "java", "software-engineer"]:
            # Search query
            results = self._search(query)
            for job in results:
                # Fetch full JD
                description = self._get_job_description(job['link'])
                jobs.append({
                    'job_title': job['title'],
                    'company': job['company'],
                    'job_description': description,
                    'link': job['link'],
                    'data-job-key': job['key']  # For deduplication
                })
        return pd.DataFrame(jobs)
```

---

## Data output

**Schema:**
```csv
job_title, company, job_description, link, data-job-key
Backend Engineer, TechCorp, "We're hiring a backend engineer to...", https://itviec.com/job/123, backend-tech-123
```

**Used by:** `IntelligenceEngine.load_all_sources()` merges ITviec jobs with TopCV data.

**Contribution to analysis:**
- Titles are standardized (Backend Engineer → Backend Developer)
- Salary: Not parsed from ITviec (set to null)
- Experience: Hardcoded to 2 years
- Descriptions: Used for skill extraction

**Note:** ITviec rows contribute little to salary analysis (no salary parsed), but provide additional signal for skill keywords and job demand in Vietnam.

---

## Cloudflare bypass

**Why:** ITviec uses Cloudflare TLS fingerprinting to block scrapers.

**Solution:** `curl_cffi` library with `impersonate="chrome"`

**What it does:**
- Makes HTTP requests that appear to come from Chrome browser
- Bypasses Cloudflare's TLS fingerprint check

**Configuration** (in crawler):
```python
from curl_cffi.requests import Session
session = Session(impersonate="chrome")
response = session.get(url, headers={...})
```

**Limitations:**
- ITviec may block the session if it detects scraping (rate limiting)
- Requires valid `ITVIEC_SESSION` cookie

---

## Deduplication

The crawler tracks jobs by `data-job-key` (a unique identifier per job in ITviec's HTML).

**Purpose:** If you run `--itviec` multiple times, new jobs are added, duplicates are skipped.

**Implementation:**
```python
seen_keys = set()
for job in results:
    key = job['data-job-key']
    if key not in seen_keys:
        seen_keys.add(key)
        jobs.append(job)
```

---

## Retry and backoff

The crawler retries failed requests with exponential backoff:

```python
max_retries = 3
backoff_factor = 1.5  # seconds

for attempt in range(max_retries):
    try:
        response = session.get(url)
        if response.status_code == 403:
            # Cloudflare block or IP ban
            raise HTTPError("403 Forbidden")
    except HTTPError:
        wait_time = backoff_factor ** attempt
        time.sleep(wait_time)
        continue
```

**429 (rate limit):** Waits 30s and retries.  
**403 (forbidden):** May indicate IP ban. Check credentials or wait.

---

## Troubleshooting

### Issue: 403 Forbidden when scraping

**Cause:** Session expired, IP blocked, or credentials invalid.

**Fix:**
1. Go to ITviec and log in again
2. Extract fresh cookies
3. Update `.env`
4. Retry: `python3 main.py --itviec`

### Issue: No jobs found (empty CSV)

**Cause:** Credentials invalid or Cloudflare blocking.

**Fix:**
1. Verify `ITVIEC_SESSION` is set: `echo $ITVIEC_SESSION`
2. Try manual scrape: Visit https://itviec.com/jobs?q=backend
3. Check if ITviec has changed its HTML structure (selectors may have changed)

### Issue: Scraper takes >5 min

**Cause:** Network slow, ITviec rate-limiting, or too many jobs.

**Fix:**
1. Run with smaller query scope (edit `QUERIES` in `crawlers/itviec.py`)
2. Increase timeout: See `curl_cffi` docs for session timeout config

### Issue: `ModuleNotFoundError: curl_cffi`

**Fix:**
```bash
pip install curl-cffi
```

---

## Including ITviec in `--flow`

Once you run `--itviec` and generate `data/itviec_jobs.csv`, it's automatically included in `--flow`:

```bash
python3 main.py --itviec
python3 main.py --flow
```

The engine checks for `data/itviec_jobs.csv` and loads it as local job data.

**To exclude ITviec:**
```bash
rm data/itviec_jobs.csv
python3 main.py --flow
```

---

## Rate limiting and ethics

**Best practices:**
- Don't run scraper too frequently (once per day is reasonable)
- Use respectful delays between requests
- Respect robots.txt and site terms of service
- Only scrape public job listings

**Current implementation:** Has 1–2 second delays between requests; should be safe.

---

## See also

- [Workflows: Python Engine](../workflows/python-engine.md) — How ITviec data is loaded
- [Operations: Setup](../operations/setup.md) — Credential setup
- [Integrations: Kaggle](kaggle.md) — Other data sources
