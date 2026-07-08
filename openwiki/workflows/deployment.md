# Deployment Workflows

How the system is deployed to Vercel and how dev/prod differ.

## Vercel deployment architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Your GitHub repo                                            │
│  ├─ Push to main                                             │
│  └─ Trigger Vercel build webhook                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Vercel CI/CD Pipeline              │
        ├────────────────────────────────────┤
        │  1. Install dependencies            │
        │     ├─ pnpm install (Node deps)     │
        │     └─ pip install -r requirements  │
        │  2. Build Next.js                   │
        │     └─ next build                   │
        │  3. Package Python function         │
        │     └─ Prepare api/ for serverless  │
        │  4. Deploy                          │
        │     ├─ Next.js → CDN (static)       │
        │     │           + SSR nodes         │
        │     └─ FastAPI → Serverless fn      │
        └────────────────┬───────────────────┘
                         │
                         ▼ (after ~5 min)
        ┌────────────────────────────────────┐
        │  Production Environment (Vercel)    │
        ├────────────────────────────────────┤
        │                                     │
        │  https://<project>.vercel.app/      │
        │  ├─ Next.js SSR + static assets    │
        │  └─ FastAPI serverless function     │
        │     (responds to /api/*)            │
        │                                     │
        │  Writable paths:                    │
        │  └─ /tmp/ (ephemeral, per-request) │
        │                                     │
        └─────────────────────────────────────┘
```

## Build configuration

### next.config.ts

Controls Next.js build and dev routing.

```typescript
// Production: No rewrites
// Development: Rewrite /api/sync, /api/market-data to localhost:8000

const config: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== 'development') return [];
    return {
      beforeFiles: [
        // Rewrite FastAPI endpoints to local backend
        { source: '/api/sync', destination: 'http://localhost:8000/api/sync' },
        { source: '/api/market-data', destination: 'http://localhost:8000/api/market-data' },
        // ... other /api/sync/* routes
      ],
    };
  },
};
```

**Effect:**
- **Dev mode** (`pnpm dev`): Next.js routes `/api/sync` → `localhost:8000`
- **Prod mode** (Vercel): All `/api/*` handled by `vercel.json` rule

### vercel.json

Controls Vercel routing and function configuration.

```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.11",
      "memory": 3008,
      "maxDuration": 300
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

**Effect:** All requests to `/api/(.*)` → Python FastAPI function.

**Constraints:**
- **maxDuration: 300s** — Sync operations must complete within 5 minutes. Longer jobs are killed.
- **memory: 3008 MB** — Function has 3GB RAM (sufficient for CSV processing, not ML training).
- **runtime: python3.11** — FastAPI runs on Python 3.11.

## Environment variables (Vercel)

Add these in Vercel project settings (Settings > Environment Variables):

| Variable | Purpose | Example |
|----------|---------|---------|
| `KAGGLE_API_TOKEN` | Authenticate Kaggle API | `KGAT_xxx...` |
| `ITVIEC_SESSION` | ITviec crawler cookie | session string |
| `ITVIEC_TOKEN` | ITviec crawler auth token | token string |
| `GROQ_API_KEY` | (Optional) Groq LLM provider | `gsk_xxx...` |
| `OPENROUTER_API_KEY` | (Optional) OpenRouter LLM provider | `sk-xxx...` |
| `GEMINI_API_KEY` | (Optional) Google Gemini LLM provider | `AIzaSyDxxx...` |
| `VERCEL` | Auto-set by Vercel. Triggers `/tmp` path fallbacks. | `1` |

## Build and deployment flow

### 1. Install & build

Vercel runs:
```bash
pnpm install
pip install -r requirements.txt
next build  # Compiles Next.js + SSR
```

**Output:** `.next/` directory (compiled Next.js), ready to serve.

### 2. Package FastAPI function

Vercel detects `api/index.py` and prepares it as a serverless function.

**Constraints:**
- Cold start: 2–10s (Python process initializes)
- Execution timeout: 300s (5 min max)
- Disk: Read-only except `/tmp` (ephemeral)

### 3. Deploy

```bash
vercel deploy  # or: git push main (if auto-deploy enabled)
```

Vercel pushes:
- Next.js build → Edge locations (CDN)
- FastAPI function → Serverless FaaS platform
- Static assets → CDN

**Time:** ~5 min for full deployment.

### 4. Check deployment

```bash
# View logs
vercel logs

# Check function health
curl https://<project>.vercel.app/api/market-data

# Check frontend
https://<project>.vercel.app/
```

## Data persistence on Vercel

**Problem:** Vercel filesystems are ephemeral per-request. You can't persist data between requests.

**Solution:** Use Git commits.

**Workflow:**
1. Run engine locally: `python3 main.py --flow`
2. Commit `data/sync/intelligence.json` and `public/data/intelligence.json` to git
3. `git push`
4. Vercel rebuilds and deploys
5. Dashboard loads the committed JSON

**Alternative (in development):**

Use the `/api/sync` button in the UI. This will:
1. Trigger a FastAPI function
2. Run `python3 main.py --flow`
3. Write to `/tmp/sync/intelligence.json`
4. Return the result to the browser

**Note:** The JSON persists only for the lifetime of that request. To persist across deployments, commit to git.

## Path handling: Vercel vs. local

**Local (dev):**
```
config.settings.DATA_DIR = "data/"
config.settings.SYNC_DIR = "data/sync/"
```

**Vercel (when VERCEL=1):**
```
config.settings.DATA_DIR = "/tmp/data/"
config.settings.SYNC_DIR = "/tmp/sync/"
```

**Why?** Vercel's filesystem is read-only except `/tmp`. The engine needs writable paths for outputs.

**Implementation** (`config/settings.py`):
```python
if os.getenv('VERCEL'):
    SYNC_DIR = '/tmp/sync/'
    RAW_DATA_DIR = '/tmp/data/raw/'
    OUTPUT_DIR = '/tmp/reports/'
else:
    SYNC_DIR = os.path.join(BASE_DIR, 'data/sync/')
    RAW_DATA_DIR = os.path.join(BASE_DIR, 'data/raw/')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'analytics/reports/')
```

**Impact:** If a Python script hardcodes `data/sync/`, it will fail on Vercel. Always import paths from `config/settings`.

## Cold start and performance

**Cold start:** First request to `/api/sync` after deployment takes 2–10s (Python initializes).

**Subsequent requests:** ~1s (warm function).

**Optimization:**
- Pin dependencies in `requirements.txt` to avoid rebuild time.
- Pre-calculate expensive operations (e.g., Kaggle unification) and commit results to git.
- Use `--limit` for testing; avoid full 100k+ row datasets during development.

## Debugging Vercel deployments

### Check build logs

```bash
vercel logs --follow
```

Watch real-time logs as your deployment builds.

### Run locally in Vercel mode

```bash
VERCEL=1 python3 main.py --flow
```

This triggers the same `/tmp` path fallbacks as production. Useful for catching path-related bugs.

### SSH into serverless function

Not available. Instead, add logging to your code and inspect logs via `vercel logs`.

### Test API endpoint

```bash
curl https://<project>.vercel.app/api/market-data | jq .
```

Should return `intelligence.json`.

## Common deployment issues

### Issue: 403 Forbidden when accessing `/api/sync`

**Cause:** FastAPI function not found or misconfigured.

**Fix:** Check `vercel.json` routes; ensure `api/index.py` exists and is named correctly.

### Issue: Module not found (Python import error)

**Cause:** Dependency missing in `requirements.txt`.

**Fix:** Add the module and re-run `pip freeze > requirements.txt`.

### Issue: Data not persisted after sync

**Cause:** Vercel `/tmp` is ephemeral. JSON only lives for that request.

**Fix:** After running `/api/sync`, the JSON is returned to the browser. To persist, commit it to git and redeploy.

### Issue: Build takes >10 min

**Cause:** Installing dependencies is slow; Next.js build is large.

**Fix:** Pre-install in a Docker layer or use Vercel's build caching. Avoid unnecessary dependencies.

---

## See also

- [Operations: Setup](../operations/setup.md) — Local setup
- [Operations: Running Locally](../operations/running-locally.md) — Dev server
- [Workflows: Python Engine](python-engine.md) — What `--flow` does
