"""
AI Validation & Analysis Layer

Feeds the engine's computed intelligence.json to free LLM providers
(Groq, OpenRouter, Google Gemini) to:
  1. VALIDATE  - sanity-check the numbers (structured JSON verdict + flags)
  2. ANALYZE   - produce strategic career insight (Vietnam backend dev by default)

Runs every provider that has an API key configured and compares them side by side.
Uses only `requests` (no provider SDKs). Never crashes on a provider failure.

Usage:
    python3 main.py --ai-analyze
    python3 main.py --ai-analyze --provider groq
    python3 main.py --ai-analyze --profile "Senior Java dev, HCMC, 5 yrs"
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

from config.settings import SYNC_DIR, OUTPUT_DIR


# ─────────────────────────────────────────────────────────────
# Provider configuration
# ─────────────────────────────────────────────────────────────
# `kind` selects the HTTP shape:
#   "openai" -> OpenAI-compatible /chat/completions (Groq, OpenRouter)
#   "gemini" -> Google Generative Language REST endpoint
PROVIDERS = {
    "groq": {
        "kind": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
    },
    "openrouter": {
        "kind": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
    },
    "gemini": {
        "kind": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.5-flash",
    },
}

DEFAULT_PROFILE = (
    "A Vietnam-based backend/Java software developer (mid-level, ~3-5 years "
    "experience) weighing which skills to invest in for the best salary ROI "
    "and long-term resilience against AI automation."
)

MAX_RETRIES = 3           # for HTTP 429 (rate limit)
REQUEST_TIMEOUT = 60      # seconds


# ─────────────────────────────────────────────────────────────
# Input: load + digest
# ─────────────────────────────────────────────────────────────
def _load_intelligence():
    """Load the latest intelligence.json (sync dir first, then public)."""
    candidates = [
        SYNC_DIR / "intelligence.json",
        Path("public/data/intelligence.json"),
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r") as f:
                print(f"[AI] Loaded intelligence from {path}")
                return json.load(f)
    return None


def _build_digest(data, top_n=15):
    """Extract a compact, signal-rich digest for the LLM (keeps us in free limits)."""
    intelligence = data.get("intelligence", [])[:top_n]
    roles = [
        {
            "role": r.get("tech"),
            "demand": r.get("demand"),
            "global_salary_usd": round(r.get("globalAvgSalary", 0)),
            "local_salary_usd": round(r.get("localAvgSalary", 0)),
            "resilience_score": r.get("resilienceScore"),
            "risk_level": r.get("riskLevel"),
        }
        for r in intelligence
    ]
    trends = [
        {"year": t.get("year"), "avg_salary_usd": round(t.get("avgSalary", 0))}
        for t in data.get("trends", [])
    ]
    skills = [
        {"skill": s.get("skill"), "relevance": s.get("relevance"), "growth": s.get("growth")}
        for s in data.get("skills", [])[:15]
    ]
    return {
        "roles": roles,
        "salary_trends": trends,
        "top_skills": skills,
        "generated_at": data.get("updated_at"),
    }


# ─────────────────────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────────────────────
def _validate_prompt(digest):
    return (
        "You are a data-quality auditor for a job-market intelligence dataset. "
        "The data below was computed from Kaggle salary datasets and local Vietnamese "
        "job listings, then correlated. Using your own world knowledge, audit it for:\n"
        "  1. plausibility  - are the global salaries realistic for each role?\n"
        "  2. risk_sanity   - do the automation risk_level / resilience_score make sense?\n"
        "  3. standardization - are any role names garbage, duplicated, or too generic?\n"
        "  4. consistency   - e.g. large opportunity but near-zero demand, contradictory fields.\n\n"
        "Respond ONLY with a JSON object of this exact shape:\n"
        "{\n"
        '  "overall_confidence": <float 0-1, how sound the data looks overall>,\n'
        '  "roles_reviewed": <int>,\n'
        '  "flags": [\n'
        '    {"role": "<role name>", "issue": "plausibility|risk_sanity|standardization|consistency",\n'
        '     "severity": "low|medium|high", "note": "<short explanation>"}\n'
        "  ]\n"
        "}\n"
        "If the data looks fine, return an empty flags array.\n\n"
        f"DATA:\n{json.dumps(digest, indent=2)}"
    )


def _analyze_prompt(digest, profile):
    return (
        "You are a career strategy analyst for the tech job market. "
        "Below is a compact digest of correlated global vs. local (Vietnam) job-market data.\n\n"
        f"The analysis is FOR THIS PERSON: {profile}\n\n"
        "Produce an objective market read AND concrete guidance for that person. "
        "Respond ONLY with a JSON object of this exact shape:\n"
        "{\n"
        '  "market_summary": "<2-3 paragraph objective overview of what the data shows>",\n'
        '  "key_insights": ["<takeaway>", "..."],\n'
        '  "opportunities": [{"role": "<role>", "why": "<reason>", "roi": "low|medium|high"}],\n'
        '  "recommendations": ["<actionable step for this person, with the why>", "..."],\n'
        '  "risks": ["<roles/skills most exposed to AI automation and why>", "..."]\n'
        "}\n\n"
        f"DATA:\n{json.dumps(digest, indent=2)}"
    )


# ─────────────────────────────────────────────────────────────
# HTTP callers (requests only)
# ─────────────────────────────────────────────────────────────
def _post_with_retry(url, headers, payload):
    """POST with exponential backoff on HTTP 429. Returns requests.Response."""
    last_resp = None
    for attempt in range(MAX_RETRIES):
        resp = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        last_resp = resp
        if resp.status_code != 429:
            return resp
        wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
        print(f"    [429] rate limited, retrying in {wait}s ({attempt + 1}/{MAX_RETRIES})...")
        time.sleep(wait)
    return last_resp


def _call_openai_compatible(cfg, api_key, model, prompt):
    """Call an OpenAI-compatible /chat/completions endpoint (Groq, OpenRouter)."""
    url = f"{cfg['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise analyst. Always return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    resp = _post_with_retry(url, headers, payload)
    resp.raise_for_status()
    body = resp.json()
    return body["choices"][0]["message"]["content"]


def _call_gemini(cfg, api_key, model, prompt):
    """Call Google Gemini generateContent REST endpoint."""
    url = f"{cfg['base_url']}/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }
    resp = _post_with_retry(url, headers, payload)
    resp.raise_for_status()
    body = resp.json()
    return body["candidates"][0]["content"]["parts"][0]["text"]


def _call_provider(name, cfg, api_key, model, prompt):
    if cfg["kind"] == "gemini":
        return _call_gemini(cfg, api_key, model, prompt)
    return _call_openai_compatible(cfg, api_key, model, prompt)


# ─────────────────────────────────────────────────────────────
# JSON extraction fallback
# ─────────────────────────────────────────────────────────────
def _extract_json(text):
    """Best-effort parse of a JSON object from an LLM response."""
    if not text:
        return None, False
    # 1. direct
    try:
        return json.loads(text), True
    except (json.JSONDecodeError, TypeError):
        pass
    # 2. strip ```json fences
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1)), True
        except json.JSONDecodeError:
            pass
    # 3. first { ... last }
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1]), True
        except json.JSONDecodeError:
            pass
    return None, False


# ─────────────────────────────────────────────────────────────
# Per-provider run
# ─────────────────────────────────────────────────────────────
def _run_step(name, cfg, api_key, model, prompt):
    """Run one call; return (parsed_or_raw_dict, metrics_dict)."""
    t0 = time.time()
    try:
        text = _call_provider(name, cfg, api_key, model, prompt)
        latency_ms = int((time.time() - t0) * 1000)
        parsed, ok = _extract_json(text)
        if ok:
            return {"data": parsed, "parse_failed": False}, {
                "latency_ms": latency_ms, "chars": len(text), "parse_ok": True,
            }
        return {"raw_response": text, "parse_failed": True}, {
            "latency_ms": latency_ms, "chars": len(text or ""), "parse_ok": False,
        }
    except requests.HTTPError as e:
        latency_ms = int((time.time() - t0) * 1000)
        code = e.response.status_code if e.response is not None else "?"
        err = "rate_limited" if code == 429 else f"http_{code}"
        return {"error": err}, {"latency_ms": latency_ms, "parse_ok": False, "error": err}
    except Exception as e:
        latency_ms = int((time.time() - t0) * 1000)
        return {"error": str(e)[:200]}, {"latency_ms": latency_ms, "parse_ok": False, "error": str(e)[:120]}


def _run_provider(name, cfg, digest, profile):
    api_key = os.environ.get(cfg["key_env"])
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    print(f"[AI] Running {name} ({model})...")

    validate_res, v_metrics = _run_step(name, cfg, api_key, model, _validate_prompt(digest))
    analyze_res, a_metrics = _run_step(name, cfg, api_key, model, _analyze_prompt(digest, profile))

    # metrics summary for comparison table
    n_recs = 0
    if not analyze_res.get("error") and not analyze_res.get("parse_failed"):
        n_recs = len(analyze_res.get("data", {}).get("recommendations", []) or [])

    return {
        "provider": name,
        "model": model,
        "validate": validate_res,
        "analyze": analyze_res,
        "metrics": {
            "validate_latency_ms": v_metrics.get("latency_ms"),
            "analyze_latency_ms": a_metrics.get("latency_ms"),
            "validate_parse_ok": v_metrics.get("parse_ok"),
            "analyze_parse_ok": a_metrics.get("parse_ok"),
            "recommendations": n_recs,
            "error": v_metrics.get("error") or a_metrics.get("error"),
        },
    }


# ─────────────────────────────────────────────────────────────
# Cross-provider aggregation
# ─────────────────────────────────────────────────────────────
def _agreement_summary(results):
    """Tally which roles were flagged by >=2 providers in the validate step."""
    role_hits = {}   # role -> set(providers)
    for res in results:
        v = res.get("validate", {})
        if v.get("error") or v.get("parse_failed"):
            continue
        for flag in v.get("data", {}).get("flags", []) or []:
            role = flag.get("role")
            if role:
                role_hits.setdefault(role, set()).add(res["provider"])
    consensus = [
        {"role": role, "flagged_by": sorted(list(provs)), "count": len(provs)}
        for role, provs in role_hits.items() if len(provs) >= 2
    ]
    consensus.sort(key=lambda x: x["count"], reverse=True)
    return consensus


# ─────────────────────────────────────────────────────────────
# Markdown report (A+B: side-by-side + metrics table)
# ─────────────────────────────────────────────────────────────
def _write_markdown(path, results, agreement, profile, ts):
    def _md_escape(s):
        return str(s).replace("|", "\\|").replace("\n", " ")

    with open(path, "w", encoding="utf-8") as f:
        f.write("# 🤖 AI Validation & Analysis Report\n\n")
        f.write(f"*Generated: {ts}*\n\n")
        f.write(f"**Profile for analysis:** {profile}\n\n")

        # Metrics table
        f.write("## Provider Comparison (Metrics)\n\n")
        f.write("| Provider | Model | Validate (ms) | Analyze (ms) | #Recs | Parse OK | Error |\n")
        f.write("| :--- | :--- | ---: | ---: | ---: | :---: | :--- |\n")
        for r in results:
            m = r["metrics"]
            parse_ok = "✅" if (m["validate_parse_ok"] and m["analyze_parse_ok"]) else "⚠️"
            f.write(
                f"| {r['provider']} | `{r['model']}` | {m['validate_latency_ms']} | "
                f"{m['analyze_latency_ms']} | {m['recommendations']} | {parse_ok} | "
                f"{_md_escape(m['error'] or '-')} |\n"
            )
        f.write("\n")

        # Agreement
        f.write("## Cross-Provider Agreement (Validation)\n\n")
        if agreement:
            f.write("Roles flagged by **2+ providers**:\n\n")
            for a in agreement:
                f.write(f"- **{a['role']}** — flagged by {', '.join(a['flagged_by'])}\n")
        else:
            f.write("*No role was independently flagged by 2+ providers.*\n")
        f.write("\n")

        # Per-provider detail
        for r in results:
            f.write(f"---\n\n## {r['provider'].upper()} — `{r['model']}`\n\n")

            # Validation
            f.write("### 🔍 Validation\n\n")
            v = r["validate"]
            if v.get("error"):
                f.write(f"> ⚠️ Error: `{v['error']}`\n\n")
            elif v.get("parse_failed"):
                f.write(f"> ⚠️ Could not parse JSON. Raw:\n\n```\n{(v.get('raw_response') or '')[:1500]}\n```\n\n")
            else:
                d = v["data"]
                f.write(f"- **Confidence:** {d.get('overall_confidence')}\n")
                f.write(f"- **Roles reviewed:** {d.get('roles_reviewed')}\n\n")
                flags = d.get("flags", []) or []
                if flags:
                    f.write("| Role | Issue | Severity | Note |\n| :--- | :--- | :--- | :--- |\n")
                    for fl in flags:
                        f.write(
                            f"| {_md_escape(fl.get('role'))} | {fl.get('issue')} | "
                            f"{fl.get('severity')} | {_md_escape(fl.get('note'))} |\n"
                        )
                    f.write("\n")
                else:
                    f.write("*No issues flagged.*\n\n")

            # Analysis
            f.write("### 📊 Analysis\n\n")
            a = r["analyze"]
            if a.get("error"):
                f.write(f"> ⚠️ Error: `{a['error']}`\n\n")
            elif a.get("parse_failed"):
                f.write(f"> ⚠️ Could not parse JSON. Raw:\n\n```\n{(a.get('raw_response') or '')[:1500]}\n```\n\n")
            else:
                d = a["data"]
                if d.get("market_summary"):
                    f.write(f"**Market Summary**\n\n{d['market_summary']}\n\n")
                if d.get("key_insights"):
                    f.write("**Key Insights**\n\n")
                    for it in d["key_insights"]:
                        f.write(f"- {it}\n")
                    f.write("\n")
                if d.get("opportunities"):
                    f.write("**Opportunities**\n\n")
                    for op in d["opportunities"]:
                        f.write(f"- **{op.get('role')}** ({op.get('roi')} ROI): {op.get('why')}\n")
                    f.write("\n")
                if d.get("recommendations"):
                    f.write("**Recommendations**\n\n")
                    for rec in d["recommendations"]:
                        f.write(f"- {rec}\n")
                    f.write("\n")
                if d.get("risks"):
                    f.write("**Risks**\n\n")
                    for rk in d["risks"]:
                        f.write(f"- {rk}\n")
                    f.write("\n")

        f.write("\n---\n*End of AI Report*\n")


# ─────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────
def run_ai_analysis(provider=None, profile=None):
    profile = profile or DEFAULT_PROFILE

    print("\n" + "=" * 55)
    print(" AI VALIDATION & ANALYSIS LAYER")
    print("=" * 55 + "\n")

    # Which providers to attempt
    if provider:
        if provider not in PROVIDERS:
            print(f"[!] Unknown provider '{provider}'. Options: {', '.join(PROVIDERS)}")
            return None
        selected = {provider: PROVIDERS[provider]}
    else:
        selected = PROVIDERS

    # Filter to those with a key
    active = {}
    for name, cfg in selected.items():
        if os.environ.get(cfg["key_env"]):
            active[name] = cfg
        else:
            print(f"[AI] Skipping {name}: no {cfg['key_env']} set.")

    if not active:
        print("\n[!] No providers configured. Set at least one of: "
              + ", ".join(c["key_env"] for c in PROVIDERS.values()))
        print("    See SETUP.md § AI Analysis for free API keys.")
        return None

    # Load data + digest
    data = _load_intelligence()
    if not data:
        print("[!] No intelligence.json found. Run `python3 main.py --flow` first.")
        return None
    digest = _build_digest(data)
    print(f"[AI] Digest built: {len(digest['roles'])} roles.\n")

    # Run providers
    results = [_run_provider(name, cfg, digest, profile) for name, cfg in active.items()]

    # Aggregate
    agreement = _agreement_summary(results)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "generated_at": datetime.now().isoformat(),
        "profile": profile,
        "source_updated_at": data.get("updated_at"),
        "providers": results,
        "agreement": agreement,
        "metrics_table": [
            {"provider": r["provider"], "model": r["model"], **r["metrics"]} for r in results
        ],
    }

    # Write JSON (A)
    json_path = SYNC_DIR / "ai_analysis.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n[AI] Structured results -> {json_path}")

    # Write Markdown (B)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUTPUT_DIR / f"ai_analysis_{ts}.md"
    _write_markdown(md_path, results, agreement, profile, ts)
    print(f"[AI] Readable report   -> {md_path}")

    # Console summary
    print("\n" + "=" * 55)
    print(" SUMMARY")
    print("=" * 55)
    for r in results:
        m = r["metrics"]
        status = f"ERROR ({m['error']})" if m["error"] else f"{m['recommendations']} recs"
        print(f" > {r['provider']:12s} {r['model']:32s} {status}")
    if agreement:
        print(f"\n Consensus flags (2+ providers): {len(agreement)}")
        for a in agreement[:5]:
            print(f"   - {a['role']} ({', '.join(a['flagged_by'])})")
    print("=" * 55 + "\n")

    return md_path


if __name__ == "__main__":
    run_ai_analysis()
