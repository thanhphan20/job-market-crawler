# Integrations: LLM Providers

How to validate analysis results with AI using free LLM APIs.

## Overview

`--ai-analyze` is an **optional** post-processing step that validates and analyzes the engine's output using free LLM providers.

**Command:**
```bash
python3 main.py --ai-analyze
```

**What it does:**
1. Reads `data/sync/intelligence.json`
2. Asks LLMs to validate data plausibility
3. Asks LLMs to generate career strategy insights
4. Writes comparison report to `analytics/reports/ai_analysis_*.md`

**Output files:**
- `data/sync/ai_analysis.json` — Raw responses from each provider
- `analytics/reports/ai_analysis_<timestamp>.md` — Formatted comparison

---

## Supported providers

### 1. Groq

**Name:** `groq`  
**Model:** `mixtral-8x7b-32768` (default, can override with `GROQ_MODEL`)  
**Speed:** Very fast (typically <3s per request)  
**Cost:** Free tier (monthly limits)  
**Setup:**

```bash
# 1. Go to https://console.groq.com/keys
# 2. Create API key
# 3. Add to .env:
GROQ_API_KEY=gsk_xxx...

# 4. Run:
python3 main.py --ai-analyze --provider groq
```

### 2. OpenRouter

**Name:** `openrouter`  
**Model:** `meta-llama/llama-2-70b-chat` (default, can override with `OPENROUTER_MODEL`)  
**Speed:** Moderate (2–5s per request)  
**Cost:** Free tier (limited credits/month)  
**Setup:**

```bash
# 1. Go to https://openrouter.ai/keys
# 2. Create API key
# 3. Add to .env:
OPENROUTER_API_KEY=sk-xxx...

# 4. Run:
python3 main.py --ai-analyze --provider openrouter
```

### 3. Gemini

**Name:** `gemini`  
**Model:** `gemini-pro` (default, can override with `GEMINI_MODEL`)  
**Speed:** Moderate (2–5s per request)  
**Cost:** Free tier (60 requests/min, 1500 requests/day)  
**Setup:**

```bash
# 1. Go to https://aistudio.google.com/app/apikey
# 2. Create API key
# 3. Add to .env:
GEMINI_API_KEY=AIzaSyDxxx...

# 4. Run:
python3 main.py --ai-analyze --provider gemini
```

---

## Usage

### Run all providers

```bash
python3 main.py --ai-analyze
```

Runs all providers with keys in `.env`. Skips providers without keys. Writes comparison.

### Run specific provider

```bash
python3 main.py --ai-analyze --provider groq
```

Runs only Groq, ignores other keys.

### Custom profile

Default profile: "Java developer, HCMC, 5 years of experience"

Custom profile:
```bash
python3 main.py --ai-analyze --profile "Frontend dev, remote, 3y, React specialist"
```

---

## Output

### JSON structure (ai_analysis.json)

```json
{
  "digest": { /* compact version of intelligence.json */ },
  "providers": {
    "groq": {
      "model": "mixtral-8x7b-32768",
      "timestamp": "2025-01-15T10:30:00Z",
      "validate": {
        "overall_confidence": 0.87,
        "flags": [
          { "category": "plausibility", "message": "Salary range seems reasonable for SE roles" },
          { "category": "risk_sanity", "message": "Automation risk scores align with industry trends" }
        ]
      },
      "analyze": {
        "market_summary": "Vietnam SE market is growing with strong backend demand...",
        "key_insights": [ "Java ecosystem dominates", "AWS skills premium", ... ],
        "opportunities": [ "DevOps skills have high ROI", ... ],
        "recommendations": [ "Focus on cloud skills", ... ],
        "risks": [ "Data science roles show high automation risk", ... ]
      },
      "metrics": { "latency_ms": 2840, "tokens_used": 450 }
    },
    "openrouter": { /* ... */ },
    "gemini": { /* ... */ }
  },
  "agreement": {
    "common_insights": [ "Backend is high-demand", "AWS is hot", ... ],
    "disagreements": [ "Automation risk: providers split on data-science roles" ]
  }
}
```

### Markdown report (ai_analysis_*.md)

```markdown
# AI Analysis Report — Job Market Intelligence

Generated: 2025-01-15 10:30 UTC  
Profile: Java developer, HCMC, 5y

## Metrics Summary

| Provider | Latency | Confidence | Key Insights | Status |
|----------|---------|-----------|-------------|--------|
| Groq | 2.8s | 87% | 5 | ✓ |
| OpenRouter | 4.2s | 91% | 6 | ✓ |
| Gemini | 3.1s | 84% | 4 | ✓ |

## Provider Comparison

### Groq (mixtral-8x7b-32768)

**Validation:**
- Overall confidence: 87%
- Flags: [plausibility: OK, risk_sanity: OK, ...]

**Analysis:**
Vietnam SE market is growing...
- Key insights: ...
- Opportunities: ...
- Risks: ...

### OpenRouter (llama-2-70b-chat)

...

### Gemini (gemini-pro)

...

## Agreement

Common insights: Backend is hot, AWS demanded, ...
Disagreements: [Risk assessment for data science roles]
```

---

## Implementation details

**File:** `scripts/ai_analyzer.py`

**Two-step LLM interaction:**

1. **Validate step** (structured JSON)
   - Prompt: "Validate this job market data for plausibility"
   - Output: JSON with `overall_confidence`, `flags[]`
   - Used to sanity-check numbers

2. **Analyze step** (structured JSON)
   - Prompt: "Analyze this market for a <profile>"
   - Output: JSON with `market_summary`, `key_insights[]`, `opportunities[]`, `recommendations[]`, `risks[]`
   - Used to generate actionable insights

**Error handling:**
- HTTP 429 (rate limit) → Retry 3× with exponential backoff
- HTTP errors → Log and skip provider
- Malformed JSON → Extract via regex; preserve raw response
- **Run never crashes** on a provider error; all keyed providers are attempted

---

## Robustness

**Retry logic:**
```
Attempt 1: Immediate
Attempt 2: Wait 2s
Attempt 3: Wait 4s
Attempt 4: Wait 8s (if enabled)
```

**JSON extraction:**
1. Try direct parse
2. If fails, strip ``` fences
3. If still fails, extract first `{`…last `}` substring
4. If all fail, preserve `raw_response` for manual inspection

**Provider failures don't block run:** If Groq times out, OpenRouter still runs.

---

## Configuration

Overridable environment variables:

```bash
# Model overrides
GROQ_MODEL=mixtral-8x7b-32768              # default
OPENROUTER_MODEL=meta-llama/llama-2-70b    # default
GEMINI_MODEL=gemini-pro                    # default

# Request config (optional)
LLM_TIMEOUT=30                             # seconds
LLM_MAX_RETRIES=3
LLM_BACKOFF_FACTOR=2
```

---

## Cost and limits

| Provider | Free tier | Limits | Notes |
|----------|-----------|--------|-------|
| Groq | Yes | 1000–2000 req/month | Very fast, reliable |
| OpenRouter | Yes | $5 credit/month | Shared model pool |
| Gemini | Yes | 60 req/min, 1500 req/day | Best for free tier |

**Recommendation for testing:** Use Groq (fastest, most reliable free tier).

---

## Troubleshooting

### Issue: `APIError: Rate limit exceeded`

**Fix:** Wait a few minutes or try a different provider.

### Issue: `KeyError: GROQ_API_KEY not found`

**Cause:** Key not in `.env`.

**Fix:**
```bash
# Check env
echo $GROQ_API_KEY

# Or set directly
GROQ_API_KEY=gsk_xxx python3 main.py --ai-analyze
```

### Issue: `ModuleNotFoundError: requests`

**Fix:**
```bash
pip install requests
```

### Issue: Malformed JSON output

**Fix:** Check `analytics/reports/ai_analysis_*.md`. The raw_response is preserved for inspection. This is a provider or model issue; try a different provider.

---

## When to use

**Good for:**
- Validating surprising findings (high salary gaps, unusual risk scores)
- Generating career strategy narratives
- Sanity-checking data before presentation
- Comparing provider outputs

**Not needed for:**
- Basic analysis (engine output is useful as-is)
- Automated decision-making (LLM responses can hallucinate)
- Production systems (use structured, validated data instead)

---

## See also

- [Workflows: Python Engine](../workflows/python-engine.md) — Engine basics
- [Operations: Setup](../operations/setup.md) — LLM setup
- [Integrations: Index](index.md) — Other data sources
