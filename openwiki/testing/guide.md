# Testing Guide

How to test the system, validate changes, and catch common issues.

## Testing strategies

### 1. Unit testing (Python engine)

Test individual components in isolation.

**Current state:** Limited unit tests exist. See `analytics/` for test placeholders.

**To add tests:**

```python
# tests/test_standardizer.py
import unittest
from analytics.standardizer import DataStandardizer

class TestStandardizer(unittest.TestCase):
    def test_standardize_title_backend(self):
        std = DataStandardizer()
        result = std.standardize_title("Sr. Backend Engineer")
        self.assertEqual(result, "Backend Developer")
    
    def test_parse_salary_vnd(self):
        result = DataStandardizer.parse_salary_vnd("30-50 triệu VND")
        self.assertGreater(result, 1000000)  # > $40k
        self.assertLess(result, 3000000)     # < $120k
```

**Run:**
```bash
python -m pytest tests/test_standardizer.py
```

### 2. Integration testing (end-to-end flow)

Test the full pipeline with real or synthetic data.

**Quick test:**
```bash
# Synthetic data (no Kaggle)
python3 main.py --benchmark

# Full flow
python3 main.py --flow

# Verify output
jq '.intelligence | length' data/sync/intelligence.json
jq '.skills | map(.relevance) | sort | reverse | .[0:3]' data/sync/intelligence.json
```

**With limit (fast):**
```bash
python3 main.py --flow --limit 10
```

### 3. Data validation

Check that `intelligence.json` has the right structure.

```bash
# Schema validation
python3 << 'EOF'
import json

with open('data/sync/intelligence.json') as f:
    data = json.load(f)

assert 'intelligence' in data, "Missing intelligence vector"
assert 'skills' in data, "Missing skills vector"
assert 'trends' in data, "Missing trends vector"
assert data['updated_at'] is not None, "Missing timestamp"

assert len(data['intelligence']) > 0, "Empty intelligence vector"
for row in data['intelligence']:
    assert 'tech' in row, "Missing tech field"
    assert 'demand' in row, "Missing demand field"
    assert 'globalAvgSalary' in row, "Missing salary field"
    assert row['riskLevel'] in ['LOW', 'MODERATE', 'HIGH'], f"Invalid risk: {row['riskLevel']}"

print("✓ Schema valid")
EOF
```

### 4. Regression testing (check for breakage)

After code changes, verify critical workflows still work.

**Checklist:**
- [ ] `python3 main.py --benchmark` completes without errors
- [ ] `python3 main.py --flow --limit 5` completes in <30s
- [ ] `data/sync/intelligence.json` exists and is valid JSON
- [ ] `analytics/reports/*.png` files generated
- [ ] `pnpm dev` starts without TypeScript errors
- [ ] Dashboard loads at http://localhost:3000
- [ ] `/api/market-data` returns valid JSON

---

## Testing specific components

### Testing the engine (Python)

**File:** `analytics/intelligence_engine.py`

**Test data:**
```bash
# Generate synthetic data
python3 main.py --benchmark
ls -lh data/raw/

# Run engine
python3 << 'EOF'
from analytics.intelligence_engine import IntelligenceEngine
engine = IntelligenceEngine()
engine.run_agentic_analysis()

# Check outputs
import json
with open('data/sync/intelligence.json') as f:
    data = json.load(f)
print(f"Roles: {len(data['intelligence'])}")
print(f"Skills: {len(data['skills'])}")
print(f"Updated: {data['updated_at']}")
EOF
```

### Testing standardization

```bash
python3 << 'EOF'
from analytics.standardizer import DataStandardizer

std = DataStandardizer()

# Test title mapping
titles = [
    "Backend Engineer",
    "Sr. Frontend Developer",
    "Java Developer",
    "DevOps Engineer",
    "Full Stack Developer",
]

for title in titles:
    standardized = std.standardize_title(title)
    print(f"{title:30} → {standardized}")

# Test salary parsing
salaries = [
    "30-50 triệu VND",
    "$80,000",
    "1500-2000 triệu VND",
]

for salary_str in salaries:
    try:
        usd = std.parse_salary_vnd(salary_str)
        print(f"{salary_str:30} → ${usd:,.0f}")
    except:
        print(f"{salary_str:30} → FAILED")
EOF
```

### Testing Kaggle downloads

```bash
# Verify datasets exist
ls -lh data/raw/*topcv*.csv data/raw/*ai_job*.csv data/raw/*impact*.csv

# Check CSV structure
head -1 data/raw/topcv_vietnam_it_jobs_2026.csv
wc -l data/raw/topcv_vietnam_it_jobs_2026.csv

# Validate columns
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('data/raw/topcv_vietnam_it_jobs_2026.csv')
print(f"Columns: {df.columns.tolist()}")
print(f"Rows: {len(df)}")
print(f"Dtypes: {df.dtypes}")
print(df.head())
EOF
```

### Testing the dashboard (Next.js)

**Build check:**
```bash
pnpm build
pnpm lint
pnpm type-check
```

**Runtime check:**
```bash
pnpm dev
# Open http://localhost:3000
# Check browser console for errors
# Try each tab: Local, Global, Impact, Skills, Raw
```

**API check:**
```bash
# With backend running
curl http://localhost:8000/api/market-data | jq '.intelligence[0]'
curl http://localhost:3000/api/report | jq '.content' | head -20
```

---

## Common issues and fixes

### Issue: `intelligence.json` is empty or missing vectors

**Cause:** Engine failed or data sources missing.

**Debug:**
```bash
# Check for errors in engine logs
python3 main.py --flow 2>&1 | grep -i error

# Check if data files exist
ls -la data/raw/

# Try with synthetic data
python3 main.py --benchmark
python3 main.py --flow
```

**Fix:** Run `python3 main.py --download-datasets` or `--benchmark`.

### Issue: Dashboard doesn't load

**Cause:** Next.js build error or missing intelligence.json.

**Debug:**
```bash
# Check build output
pnpm build

# Check for TypeScript errors
pnpm type-check

# Verify JSON exists
ls -la public/data/intelligence.json data/sync/intelligence.json
```

**Fix:** Run `python3 main.py --flow` to generate JSON, then `pnpm dev`.

### Issue: Charts show no data

**Cause:** intelligence.json vectors are empty.

**Debug:**
```bash
jq '.skills | length' data/sync/intelligence.json
jq '.intelligence | length' data/sync/intelligence.json
```

**Fix:** Check if engine ran successfully; if not, run with `--benchmark` first.

### Issue: Sync button fails (API 500)

**Cause:** FastAPI backend error.

**Debug:**
```bash
# Check backend logs
uvicorn api.index:app --reload --port 8000

# Test endpoint directly
curl -X POST http://localhost:8000/api/sync

# Check if Python is installed
python3 --version
pip show pandas
```

**Fix:** Ensure all Python dependencies are installed: `pip install -r requirements.txt`.

### Issue: ITviec scraper returns 403

**Cause:** Session expired or IP blocked.

**Debug:**
```bash
# Verify credentials
echo $ITVIEC_SESSION
echo $ITVIEC_TOKEN

# Check if cookies are valid
curl -I https://itviec.com
```

**Fix:** Get fresh cookies from https://itviec.com after logging in.

---

## Performance testing

### Engine speed

```bash
time python3 main.py --flow --limit 100
# Should complete in <10s for 100 rows
```

**Typical performance:**
- Synthetic data (--benchmark): <5s
- Real data, 100 rows: ~10s
- Real data, full (1000s rows): 1–2 min

### Dashboard load time

```bash
# Cold load (after pnpm build)
time curl http://localhost:3000 > /dev/null

# Should be <1s

# Check with browser DevTools Network tab
# Measure DOMContentLoaded and Load times
```

### API response time

```bash
# Time an API call
time curl http://localhost:8000/api/market-data > /dev/null

# Should be <1s
```

---

## Testing before deployment

**Checklist:**

- [ ] Code builds without errors: `pnpm build`
- [ ] No TypeScript errors: `pnpm type-check`
- [ ] Linting passes: `pnpm lint`
- [ ] Engine runs: `python3 main.py --flow --limit 10`
- [ ] JSON is valid: `jq . data/sync/intelligence.json > /dev/null`
- [ ] Dashboard loads: `pnpm dev` → http://localhost:3000
- [ ] Sync button works: Click in UI, check logs
- [ ] Reports generate: `ls analytics/reports/`

---

## CI/CD (optional)

To automate testing, add a `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - run: pip install -r requirements.txt
      - run: pnpm install
      
      - run: pnpm build
      - run: pnpm type-check
      - run: pnpm lint
      
      - run: python3 main.py --benchmark
      - run: python3 main.py --flow --limit 10
      
      - run: jq . data/sync/intelligence.json > /dev/null
```

---

## See also

- [Workflows: Python Engine](../workflows/python-engine.md) — Engine internals
- [Workflows: Dashboard](../workflows/dashboard.md) — Frontend internals
- [Architecture: System Design](../architecture/system-design.md) — Data flow
