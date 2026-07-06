"""
Stack Overflow Developer Survey fetch + normalize.

Downloads the (real, ~49k respondent) SO Developer Survey and reshapes it into
the schema the Intelligence Engine expects for its GLOBAL software-engineer
benchmark: job_title + salary_usd + required_skills.

Output: data/raw/ai_job_so_survey_2025.csv  (matches the engine's "ai_job" pattern)

The survey is genuinely software-engineering focused (full-stack, back-end,
front-end, mobile, embedded, DevOps dominate), which is why it's a far more
reliable SE source than generic scraped job dumps.
"""

import os
from pathlib import Path

import requests
import pandas as pd


# Public mirror of the SO Developer Survey results (2025).
SO_SURVEY_URL = (
    "https://github.com/StackExchange/Survey/raw/refs/heads/main/"
    "packages/archive/2025/results.csv"
)
SO_YEAR = 2025

# Allowlist: SO `DevType` -> clean role name. Only these (software-engineering)
# roles are kept, so the benchmark isn't diluted by data-science / non-tech /
# student / retired respondents.
DEVTYPE_MAP = {
    "Developer, full-stack": "Fullstack Developer",
    "Developer, back-end": "Backend Developer",
    "Developer, front-end": "Frontend Developer",
    "Developer, desktop or enterprise applications": "Desktop Developer",
    "Developer, mobile": "Mobile Developer",
    "Developer, embedded applications or devices": "Embedded Developer",
    "Developer, game or graphics": "Game Developer",
    "Developer, QA or test": "QA Engineer",
    "Architect, software or solutions": "Solution Architect",
    "DevOps engineer or professional": "DevOps Engineer",
    "Cloud infrastructure engineer": "Cloud Engineer",
    "Engineering manager": "Engineering Manager",
    "AI/ML engineer": "AI Engineer",
    "Security professional": "Security Engineer",
    "Blockchain": "Blockchain Developer",
}

SALARY_MIN = 1000
SALARY_MAX = 500000


def _repo_data_dir():
    return Path(__file__).resolve().parent.parent / "data"


def fetch_so_survey(url=SO_SURVEY_URL, target_dir=None):
    """Download the raw SO survey results.csv."""
    target_dir = Path(target_dir) if target_dir else _repo_data_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / "so_survey_2025.csv"

    print(f"[*] Downloading Stack Overflow Developer Survey {SO_YEAR}...")
    try:
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"[+] Downloaded {len(r.content) // 1024 // 1024} MB -> {dest}")
        return dest
    except Exception as e:
        print(f"[!] Failed to fetch SO survey: {e}")
        return None


def normalize_so_survey(src=None, raw_dir=None):
    """Reshape the SO survey into the engine's global-benchmark schema."""
    data_dir = _repo_data_dir()
    src = Path(src) if src else data_dir / "so_survey_2025.csv"
    raw_dir = Path(raw_dir) if raw_dir else data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print(f"[!] Survey file not found: {src}")
        return None

    print("[*] Normalizing SO survey into SE benchmark...")
    want = ["DevType", "ConvertedCompYearly", "LanguageHaveWorkedWith", "Country"]
    available = pd.read_csv(src, nrows=0).columns.tolist()
    use = [c for c in want if c in available]
    df = pd.read_csv(src, usecols=use)

    # Keep only allowlisted software-engineering roles with a usable salary.
    df = df[df["DevType"].isin(DEVTYPE_MAP)]
    df = df.dropna(subset=["ConvertedCompYearly"])
    df = df[
        (df["ConvertedCompYearly"] >= SALARY_MIN)
        & (df["ConvertedCompYearly"] <= SALARY_MAX)
    ]

    out = pd.DataFrame()
    out["job_id"] = range(len(df))
    out["job_title"] = df["DevType"].map(DEVTYPE_MAP).values
    out["salary_usd"] = df["ConvertedCompYearly"].values
    out["work_year"] = SO_YEAR
    out["required_skills"] = (
        df["LanguageHaveWorkedWith"].fillna("").values
        if "LanguageHaveWorkedWith" in df.columns else ""
    )
    if "Country" in df.columns:
        out["country"] = df["Country"].values

    dest = raw_dir / "ai_job_so_survey_2025.csv"
    out.to_csv(dest, index=False)
    print(f"[+] Wrote {len(out)} SE rows across {out['job_title'].nunique()} roles -> {dest}")
    return dest


def fetch_and_prepare():
    """Download + normalize in one step (used by `main.py --download-datasets`)."""
    src = fetch_so_survey()
    if not src:
        return None
    return normalize_so_survey(src)


if __name__ == "__main__":
    fetch_and_prepare()
