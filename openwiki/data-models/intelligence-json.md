# Data Model: intelligence.json

The core data contract. Produced by the Python engine, consumed by the Next.js dashboard.

## Overview

`intelligence.json` is a single JSON file containing 8 vectors (arrays) of analyzed job-market data. It is the **single source of truth** for the dashboard.

**Locations:**
- `data/sync/intelligence.json` — Produced by Python engine
- `public/data/intelligence.json` — Copied to Next.js public folder for serving

**Produced by:** `IntelligenceEngine._export_dashboard_json()` in `analytics/intelligence_engine.py`

**Consumed by:** `src/app/page.tsx` and `RealTimeDashboard.tsx`

## Full schema

```json
{
  "intelligence": [
    {
      "tech": "string",
      "demand": "number (job count)",
      "globalAvgSalary": "number (USD)",
      "localAvgSalary": "number (USD)",
      "resilienceScore": "number (0.0 - 1.0)",
      "riskLevel": "enum: 'LOW' | 'MODERATE' | 'HIGH'"
    }
  ],
  "trends": [
    {
      "year": "number (YYYY)",
      "avgSalary": "number (USD)"
    }
  ],
  "impact": [
    {
      "industry": "string",
      "status": "string (e.g., 'High Demand', 'Emerging')",
      "automationRisk": "number (0.0 - 1.0)"
    }
  ],
  "skills": [
    {
      "skill": "string",
      "relevance": "number (0 - 100)",
      "growth": "number (% change, can be negative)"
    }
  ],
  "correlation": [
    {
      "x": "number (local job demand)",
      "y": "number (local avg salary in USD)",
      "label": "string (role name)",
      "size": "number (global demand, for bubble size)"
    }
  ],
  "marketShare": [
    {
      "name": "string (role name)",
      "value": "number (job count or percentage)"
    }
  ],
  "rawTable": [
    {
      "std_role": "string (standardized role name)",
      "global_salary_mean": "number | null",
      "global_salary_median": "number | null",
      "global_salary_min": "number | null",
      "global_salary_max": "number | null",
      "global_job_count": "number",
      "local_salary_avg": "number | null",
      "local_job_count": "number",
      "opportunity_gap": "number (global_mean - local_avg, USD)"
    }
  ],
  "updated_at": "string (ISO-8601 timestamp)"
}
```

## Vector details

### 1. intelligence (array)

Top roles/technologies with salary and automation risk metrics.

**Purpose:** Main dashboard view showing tech demand, global vs. local salaries, and risk.

**Fields:**
- `tech` — Technology/role name (e.g., "Java", "Backend Developer", "React")
- `demand` — Number of job postings mentioning this tech
- `globalAvgSalary` — Global average salary (USD, from SO survey + Kaggle)
- `localAvgSalary` — Local average salary (USD, converted from VND if necessary)
- `resilienceScore` — Inverse of automation risk (0.0 = high risk, 1.0 = low risk)
- `riskLevel` — Categorical risk: LOW, MODERATE, HIGH

**Example:**
```json
{
  "tech": "Backend Developer",
  "demand": 142,
  "globalAvgSalary": 115000,
  "localAvgSalary": 42000,
  "resilienceScore": 0.72,
  "riskLevel": "MODERATE"
}
```

**Sorted by:** Opportunity gap (highest first).

### 2. trends (array)

Multi-year salary evolution for Software Engineer roles.

**Purpose:** Show career salary progression over time.

**Fields:**
- `year` — YYYY (2020–2035, or as available)
- `avgSalary` — Average SE salary that year (USD)

**Example:**
```json
[
  { "year": 2020, "avgSalary": 85000 },
  { "year": 2021, "avgSalary": 92000 },
  { "year": 2022, "avgSalary": 100000 },
  { "year": 2025, "avgSalary": 120000 }
]
```

**Source:** AI automation-risk dataset (`ai_impact_job_risk.csv`) if available, else SO survey single-year + linear projection.

### 3. impact (array)

Automation risk per industry/role.

**Purpose:** Show which roles are most vulnerable to AI/automation.

**Fields:**
- `industry` — Role/industry name (e.g., "Data Science", "DevOps", "Backend")
- `status` — Categorical status (e.g., "High Risk", "Low Risk", "Stable")
- `automationRisk` — Numerical risk (0.0 = no risk, 1.0 = certain automation)

**Example:**
```json
{
  "industry": "Data Science",
  "status": "High Risk",
  "automationRisk": 0.68
}
```

**Source:** Kaggle AI automation-risk dataset (`ai_impact_job_risk.csv`).

### 4. skills (array)

Top technologies/skills with demand and growth trends.

**Purpose:** Show the most in-demand skills and which are growing/declining.

**Fields:**
- `skill` — Technology name (e.g., "Spring Boot", "React", "AWS")
- `relevance` — Demand ranking (0–100, higher = more relevant)
- `growth` — Year-over-year growth (%, can be negative for declining skills)

**Example:**
```json
{
  "skill": "Spring Boot",
  "relevance": 92,
  "growth": 15.3
}
```

**Source:** Job titles + descriptions, regex pattern matching (SKILL_KEYWORDS in `analytics/standardizer.py`), or SO survey `required_skills` if available.

### 5. correlation (array)

Scatter-plot data: local job demand vs. local salary.

**Purpose:** Show relationship between demand and compensation (opportunity gaps).

**Fields:**
- `x` — Local job demand (number of postings)
- `y` — Local average salary (USD)
- `label` — Role name (e.g., "Backend Developer")
- `size` — Global job count (for bubble size, indicates global importance)

**Example:**
```json
{
  "x": 142,
  "y": 42000,
  "label": "Backend Developer",
  "size": 1850
}
```

**Interpretation:** High x + low y = high-demand role with low local pay (high opportunity gap).

### 6. marketShare (array)

Role distribution (pie-chart data).

**Purpose:** Show what % of job market each role represents.

**Fields:**
- `name` — Role name
- `value` — Job count or percentage

**Example:**
```json
[
  { "name": "Backend Developer", "value": 35 },
  { "name": "Frontend Developer", "value": 28 },
  { "name": "Fullstack Developer", "value": 21 },
  { "name": "DevOps", "value": 16 }
]
```

### 7. rawTable (array)

Full standardized data for detailed browsing.

**Purpose:** Show raw statistics for each role. Dashboard renders as sortable/filterable table.

**Fields:**
- `std_role` — Standardized role name
- `global_salary_*` — Global salary statistics (mean, median, min, max, or null if unavailable)
- `global_job_count` — Number of jobs globally
- `local_salary_avg` — Average local salary (or null)
- `local_job_count` — Number of local jobs
- `opportunity_gap` — global_mean - local_avg (USD)

**Example:**
```json
{
  "std_role": "Backend Developer",
  "global_salary_mean": 115000,
  "global_salary_median": 108000,
  "global_salary_min": 70000,
  "global_salary_max": 180000,
  "global_job_count": 1850,
  "local_salary_avg": 42000,
  "local_job_count": 142,
  "opportunity_gap": 73000
}
```

### 8. updated_at

ISO-8601 timestamp indicating when this JSON was generated.

**Example:** `"2025-01-15T10:30:45.123Z"`

**Used by:** Dashboard to show "Last updated" in the UI.

---

## Fallback / default values

If a data source is missing, the exporter writes hardcoded defaults so the frontend never breaks.

**Default intelligence vector:**
```json
{
  "tech": "Backend Developer",
  "demand": 100,
  "globalAvgSalary": 100000,
  "localAvgSalary": 40000,
  "resilienceScore": 0.75,
  "riskLevel": "MODERATE"
}
```

**Default trends:**
```json
[
  { "year": 2020, "avgSalary": 80000 },
  { "year": 2025, "avgSalary": 120000 }
]
```

**Default impact:**
```json
[
  { "industry": "Software Engineering", "status": "Stable", "automationRisk": 0.4 }
]
```

**Default skills:**
```json
[
  { "skill": "Java", "relevance": 85, "growth": 10 },
  { "skill": "React", "relevance": 78, "growth": 5 }
]
```

**These defaults ensure the dashboard always renders**, even if the data source is missing or the engine fails.

---

## How to modify the contract

**If you add a new vector:**

1. Add it to `IntelligenceEngine._export_dashboard_json()` in `analytics/intelligence_engine.py`
2. Add a default value
3. Update `src/app/page.tsx` to pass it to `<RealTimeDashboard>`
4. Add a new tab or chart in `RealTimeDashboard.tsx` to display it
5. Update TS types in `src/components/charts/IntelligenceCharts.tsx`
6. Update this document

**If you change an existing vector:**

1. Update the exporter (`analytics/intelligence_engine.py`)
2. Update all consumers (page.tsx, RealTimeDashboard, chart types)
3. Update this document

**Testing:** Run `python3 main.py --benchmark --flow` to generate test data, then verify the JSON structure with `jq . data/sync/intelligence.json`.

---

## Serialization

**Format:** JSON (UTF-8)

**Size:** Typically 50–200 KB (uncompressed)

**Compression:** Not applied by the engine; let the web server (Vercel, uvicorn) handle gzip.

**Versioning:** No version field in the JSON. If you break the schema, all dashboards must update together.

---

## See also

- [Architecture: System Design](../architecture/system-design.md) — How intelligence.json is created
- [Workflows: Python Engine](../workflows/python-engine.md) — Export step detail
- [Workflows: Dashboard](../workflows/dashboard.md) — How the frontend consumes the JSON
