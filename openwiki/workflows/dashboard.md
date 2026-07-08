# Dashboard Workflows

How the Next.js frontend loads, displays, and refreshes data.

## Server-side data loading (SSR)

**File:** `src/app/page.tsx`

```typescript
export default async function Home() {
  const data = await getDashboardData();
  return <RealTimeDashboard initialData={data} />;
}

async function getDashboardData() {
  // 1. Try to read intelligence.json
  const dataPath = path.join(process.cwd(), 'public/data/intelligence.json');
  if (fs.existsSync(dataPath)) {
    return JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
  }
  
  // 2. Fallback: Try data/sync/intelligence.json
  const syncPath = path.join(process.cwd(), 'data/sync/intelligence.json');
  if (fs.existsSync(syncPath)) {
    return JSON.parse(fs.readFileSync(syncPath, 'utf-8'));
  }
  
  // 3. Fallback: Try FastAPI /api/market-data
  const response = await fetch('http://localhost:8000/api/market-data');
  if (response.ok) {
    return response.json();
  }
  
  // 4. Final fallback: Return empty structure with hardcoded defaults
  return getDefaultDashboardData();
}
```

**When SSR loads:**
- At build time (if `next build` runs)
- At request time (if dynamic rendering)
- In development (when you visit localhost:3000)

**Result:** The page renders with data in the HTML (good for SEO, fast initial paint).

## Client-side rendering

**Component:** `src/components/RealTimeDashboard.tsx`

```typescript
export const RealTimeDashboard = ({ initialData }) => {
  const [activeTab, setActiveTab] = useState('local');
  const [data, setData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(false);

  // Listen for sync completion
  useEffect(() => {
    window.addEventListener('intel-sync-complete', () => {
      // Refresh data from API
      fetch('/api/market-data').then(r => r.json()).then(setData);
    });
  }, []);

  return (
    <div className="terminal-ui">
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab label="Local Market"    content={<LocalMarketChart data={data.intelligence} />} />
        <Tab label="Global"          content={<GlobalBenchmarkChart data={data.intelligence} />} />
        <Tab label="Impact"          content={<ImpactChart data={data.impact} />} />
        <Tab label="Skills"          content={<SkillsChart data={data.skills} />} />
        <Tab label="Raw Data"        content={<KaggleDataTable data={data.rawTable} />} />
      </Tabs>
      <SyncTerminal />
    </div>
  );
};
```

**Tabs:**
1. **Local Market** — Demand heatmap for Vietnam (TopCV + ITviec jobs)
2. **Global** — Salary ranges and benchmarks (Stack Overflow + Kaggle)
3. **Impact** — Automation risk per industry/role
4. **Skills** — Top technologies + growth trends
5. **Raw Data** — Full standardized table for browsing/exporting

## Chart components

**File:** `src/components/charts/IntelligenceCharts.tsx`

Uses Recharts for all visualizations:

| Component | Chart Type | Data Input | 
|-----------|-----------|-------------|
| `LocalMarketChart` | Bar chart | `intelligence` vector |
| `GlobalBenchmarkChart` | Bar chart (salary ranges) | `intelligence` vector |
| `ImpactChart` | Heatmap | `impact` vector |
| `SkillsChart` | Bar chart | `skills` vector |
| `TrendChart` | Line chart | `trends` vector |
| `CorrelationChart` | Scatter plot | `correlation` vector |
| `MarketShareChart` | Pie chart | `marketShare` vector |
| `RawDataTable` | HTML table | `rawTable` vector |

**Data types:**
```typescript
interface TechStat {
  tech: string;
  demand: number;
  globalAvgSalary: number;
  localAvgSalary: number;
  resilienceScore: number;
  riskLevel: 'LOW' | 'MODERATE' | 'HIGH';
}

interface SalaryTrend {
  year: number;
  avgSalary: number;
}

interface ImpactData {
  industry: string;
  status: string;
  automationRisk: number;
}

interface SkillStat {
  skill: string;
  relevance: number;
  growth: number;
}

interface CorrelationPoint {
  x: number;
  y: number;
  label: string;
  size: number;
}

interface MarketRegion {
  name: string;
  value: number;
}
```

## Sync terminal

**File:** `src/components/SyncTerminal.tsx`

**Purpose:** Control panel to trigger engine actions and view live reports.

**UI:**
```
┌──────────────────────────────────────┐
│  🔄 Full Sync (--flow)               │  [button] Run
│  🕷️  ITviec Crawler                  │  [button] Run
│  📦 Extract Datasets                 │  [button] Run
├──────────────────────────────────────┤
│  📄 Latest Report                     │
│                                      │
│  Market Intelligence Report          │
│  Updated: 2025-01-15 10:30 UTC       │
│                                      │
│  [displays markdown content]          │
│  [images rewritten to /api/report/...│
└──────────────────────────────────────┘
```

**Actions:**
1. **Full Sync** — POST to `/api/sync`. Triggers `python3 main.py --flow`.
2. **ITviec Crawler** — POST to `/api/sync/itviec`. Triggers `python3 main.py --itviec` + `--flow`.
3. **Extract Datasets** — POST to `/api/sync/extract`. Triggers `python3 main.py --extract`.

**Report display:**
- Fetches `/api/report` to get latest markdown
- Rewrites image paths: `![](chart_demand.png)` → `![](/api/report/image/chart_demand.png)`
- Renders markdown as HTML

**Event flow:**
```
User clicks "Full Sync" button
             │
             ▼
POST /api/sync (or localhost:8000/api/sync)
             │
             ▼ (subprocess)
python3 main.py --flow
             │ (writes intelligence.json + PNGs)
             ▼
window.postMessage('intel-sync-complete')
             │
             ▼ (browser receives)
RealTimeDashboard.useEffect()
             │
             ▼
fetch('/api/market-data')
             │
             ▼
Update charts + refresh report display
```

## API endpoints (Next.js)

### GET /api/report

Returns latest `analytics/reports/market_intelligence_*.md` content.

**Usage:** Called by `<SyncTerminal>` to display markdown report.

**Response:**
```json
{
  "content": "# Market Intelligence Report\n\n...",
  "timestamp": "2025-01-15T10:30:00Z",
  "charts": ["chart_demand.png", "chart_salary_trends.png", ...]
}
```

### GET /api/report/image/[filename]

Serves PNG from `analytics/reports/[filename]`.

**Usage:** Called by `<img src="/api/report/image/chart_demand.png" />`.

**Response:** Binary PNG.

### POST /api/run-script

Spawns `python3 main.py <command>` and streams stdout.

**Allowed commands:** `--flow`, `--itviec`, `--extract`

**Body:** `{ "command": "--flow" }`

**Response (streaming):** Newline-delimited stdout.

**Availability:** Local dev only (no Vercel support — Vercel functions can't exec long-lived subprocesses).

---

## API endpoints (FastAPI)

### GET /api/market-data

Returns the latest `intelligence.json` with fallback discovery.

**Usage:** Called by RealTimeDashboard to refresh charts after sync.

**Response:** Full `intelligence.json` (schema in [Data Models](../data-models/intelligence-json.md)).

**Fallback order:**
1. `data/sync/intelligence.json`
2. `public/data/intelligence.json`
3. Hardcoded default (if both missing)

### POST /api/sync

Triggers `python3 main.py --flow`.

**Body:** (empty or metadata)

**Returns:** `{ "status": "started" | "completed" | "failed", "message": "..." }`

**Side effects:**
- Runs `--flow` subprocess
- Writes `intelligence.json` + PNGs
- Fires `window.postMessage('intel-sync-complete')` on completion

### POST /api/sync/itviec

Triggers `python3 main.py --itviec` + `--flow`.

**Body:** (empty)

**Returns:** Same as `/api/sync`.

### POST /api/sync/extract

Triggers `python3 main.py --extract`.

**Body:** (empty)

**Returns:** Same as `/api/sync`.

---

## Development vs. production routing

### Development (pnpm dev:all)

```
Browser request to /api/sync
             │
             ▼ (next.config.ts rewrites)
             ├─ /api/sync → localhost:8000/api/sync
             ├─ /api/market-data → localhost:8000/api/market-data
             └─ /api/report → handled by Next.js (local file read)
             
             ▼
uvicorn running on localhost:8000 (FastAPI)
```

### Production (Vercel)

```
Browser request to /api/sync
             │
             ▼ (vercel.json rewrites ALL /api/*)
             ├─ /api/sync → /api/index.py (FastAPI function)
             ├─ /api/market-data → /api/index.py
             └─ /api/report → /api/index.py
             
             ▼
Python function (FastAPI)
```

**Consequence:** The effective API implementation differs between dev and prod. When debugging an endpoint, confirm which handler is live.

---

## Chart styling

**Framework:** Recharts + Tailwind CSS v4

**Colors:**
- Primary: `#3b82f6` (blue)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (amber)
- Danger: `#ef4444` (red)
- Background: `#1f2937` (dark gray)
- Text: `#f3f4f6` (light gray)

**Animations:** Framer Motion for enter/exit transitions.

**Responsive:** Mobile-first. Charts stack vertically on small screens.

## Error handling

- **Missing intelligence.json:** Falls back to hardcoded default data. Page still renders.
- **API timeout:** Charts show cached data. Sync button remains functional.
- **Malformed JSON:** Frontend catches and logs. Uses fallback schema.
- **Image 404:** Chart markdown references broken images. Frontend gracefully skips.

---

## See also

- [Architecture: System Design](../architecture/system-design.md) — API routes and routing logic
- [Data Models: intelligence.json](../data-models/intelligence-json.md) — Chart data schema
- [Operations: Running Locally](../operations/running-locally.md) — How to start the servers
