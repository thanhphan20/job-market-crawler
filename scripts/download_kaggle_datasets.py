"""
Automated Kaggle Dataset Downloader

Downloads and prepares the datasets the Intelligence Engine needs, using a
Kaggle API token (the newer KGAT_... token) as a Bearer credential — no
`kaggle` CLI or username/key `kaggle.json` required.

Setup:
    1. https://www.kaggle.com/settings/account -> "Create New API Token"
    2. Put the token in .env as:  KAGGLE_API_TOKEN=KGAT_xxx
    3. python3 main.py --download-datasets

Focus: software-engineer roles (e.g. Java) and their skills — a local Vietnam
market (TopCV) correlated against a global software-engineer salary benchmark.
"""

import os
import io
import zipfile
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

KAGGLE_API = "https://www.kaggle.com/api/v1"


def _normalize_ai_impact(csv_path):
    """Reshape the AI job-risk dataset into the engine's impact schema
    ('Job Title' + 'Automation Risk (%)') so KaggleUnifier can consume it."""
    df = pd.read_csv(csv_path)
    if "job_title" not in df.columns or "ai_risk_score" not in df.columns:
        print("  [!] AI-impact dataset missing expected columns; leaving as-is.")
        return
    # Focus on the near-term horizon so risk reflects "current" AI impact.
    if "year" in df.columns:
        recent = df[(df["year"] >= 2024) & (df["year"] <= 2030)]
        if not recent.empty:
            df = recent
    out = pd.DataFrame()
    out["Job Title"] = df["job_title"]
    out["Automation Risk (%)"] = (df["ai_risk_score"] * 100).round(2)  # 0-1 -> %
    out = out.dropna(subset=["Job Title", "Automation Risk (%)"])
    out.to_csv(csv_path, index=False)
    print(f"  ✓ Normalized AI impact: {len(out)} rows with Automation Risk (%)")


# ─────────────────────────────────────────────────────────────
# Dataset registry (Kaggle sources)
# ─────────────────────────────────────────────────────────────
# The GLOBAL software-engineer salary + skills benchmark comes from the Stack
# Overflow Developer Survey (see scripts/fetch_data.py). Kaggle supplies the
# local Vietnam market and the AI automation-risk overlay.
DATASETS = {
    # Local Vietnam jobs (engine's "topcv" source) — already matches TopCVParser.
    "topcv": {
        "id": "baocgb/vietnam-it-jobs-raw-data-from-topcv-2026",
        "rename_to": "topcv_vietnam_it_jobs_2026.csv",  # matches "topcv" pattern
        "description": "Vietnam IT Jobs raw data from TopCV 2026 (local market)",
        "post_process": None,
    },
    # AI automation-risk overlay for tech roles (engine's "kaggle_impact" source).
    "impact": {
        "id": "shree0910/ai-job-risk-and-salary-dataset-20152035",
        "rename_to": "ai_impact_job_risk.csv",  # matches "impact" pattern
        "description": "AI Job Impact & Risk 2015-2035 (automation risk by tech role)",
        "post_process": _normalize_ai_impact,
    },
}


# ─────────────────────────────────────────────────────────────
# Download via Bearer token
# ─────────────────────────────────────────────────────────────
def _get_token():
    return os.environ.get("KAGGLE_API_TOKEN")


def download_and_extract(dataset_id, token, raw_dir, rename_to):
    """Download a dataset zip via the Kaggle API and extract its main CSV."""
    url = f"{KAGGLE_API}/datasets/download/{dataset_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=180)
        resp.raise_for_status()
    except requests.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        print(f"  ✗ Download failed (HTTP {code}). Dataset private/renamed or bad token.")
        return False
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return False

    try:
        z = zipfile.ZipFile(io.BytesIO(resp.content))
    except zipfile.BadZipFile:
        print("  ✗ Response was not a valid zip (auth or dataset issue).")
        return False

    csvs = [f for f in z.namelist() if f.lower().endswith(".csv")]
    if not csvs:
        print("  ✗ No CSV found in dataset zip.")
        return False

    # Extract the largest CSV (the main data file) to the rename target.
    main = max(csvs, key=lambda f: z.getinfo(f).file_size)
    dst = raw_dir / rename_to
    with z.open(main) as src, open(dst, "wb") as out:
        out.write(src.read())
    print(f"  ✓ {main} -> {dst.name}")
    return True


def download_all_datasets(data_dir=None):
    """Download and prepare all required datasets. Returns True if all succeeded."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data"
    else:
        data_dir = Path(data_dir)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print(" KAGGLE DATASET DOWNLOADER")
    print("=" * 60 + "\n")

    token = _get_token()
    if not token:
        print("[!] No KAGGLE_API_TOKEN set.")
        print("    1. https://www.kaggle.com/settings/account -> Create New API Token")
        print("    2. Add to .env:  KAGGLE_API_TOKEN=KGAT_xxx")
        return False

    all_success = True
    for key, info in DATASETS.items():
        print(f"[*] {key.upper()}: {info['description']}")
        ok = download_and_extract(info["id"], token, raw_dir, info["rename_to"])
        if ok and info.get("post_process"):
            try:
                info["post_process"](raw_dir / info["rename_to"])
            except Exception as e:
                print(f"  [!] post-process failed: {e}")
        if not ok:
            all_success = False
        print()

    # Global SE salary + skills benchmark: Stack Overflow Developer Survey.
    print("[*] GLOBAL: Stack Overflow Developer Survey (SE salaries + skills)")
    try:
        from scripts.fetch_data import fetch_and_prepare
        if not fetch_and_prepare():
            all_success = False
    except Exception as e:
        print(f"  [!] SO survey fetch failed: {e}")
        all_success = False
    print()

    # Remove any stale global benchmark from earlier dataset choices.
    for stale in raw_dir.glob("ai_job_software_engineer_*.csv"):
        stale.unlink()

    print("=" * 60)
    if all_success:
        print("[SUCCESS] Datasets downloaded and ready!")
        print(f"Location: {raw_dir}")
        print("\nNext: python3 main.py --flow")
    else:
        print("[!] Some datasets failed. Check errors above.")
    print("=" * 60 + "\n")
    return all_success


if __name__ == "__main__":
    import sys
    download_all_datasets(sys.argv[1] if len(sys.argv) > 1 else None)
