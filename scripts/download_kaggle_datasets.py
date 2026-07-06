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
import re
import io
import zipfile
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

KAGGLE_API = "https://www.kaggle.com/api/v1"


# ─────────────────────────────────────────────────────────────
# SE salary normalization
# ─────────────────────────────────────────────────────────────
def _parse_se_salary(s):
    """'$68K - $94K (Glassdoor est.)' -> 81000.0 (annual USD midpoint)."""
    if not isinstance(s, str):
        return None
    text = s.replace("\xa0", " ")
    # $NNK ranges/singles (the dominant format)
    ks = re.findall(r"\$\s*([\d.]+)\s*[Kk]", text)
    if ks:
        vals = [float(n) * 1000 for n in ks]
        return sum(vals) / len(vals)
    # $NN/hr -> annualize (2080 work hours/yr)
    hourly = re.findall(r"\$\s*([\d.]+)\s*/?\s*(?:hr|hour)", text, re.I)
    if hourly:
        vals = [float(n) * 2080 for n in hourly]
        return sum(vals) / len(vals)
    # plain $NN,NNN
    plain = re.findall(r"\$\s*([\d,]+)", text)
    if plain:
        vals = [float(n.replace(",", "")) for n in plain if n.replace(",", "").isdigit()]
        if vals:
            avg = sum(vals) / len(vals)
            return avg if avg > 1000 else None
    return None


def _normalize_se_salaries(csv_path):
    """Reshape the Glassdoor SE dataset into the engine's expected schema
    (job_title + salary_usd + job_id) so KaggleUnifier can consume it."""
    df = pd.read_csv(csv_path)
    rename = {"Job Title": "job_title", "Location": "location", "Company": "company"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "Salary" not in df.columns or "job_title" not in df.columns:
        print("  [!] SE dataset missing expected columns; leaving as-is.")
        return
    df["salary_usd"] = df["Salary"].apply(_parse_se_salary)
    df = df.dropna(subset=["salary_usd", "job_title"])
    df["job_id"] = range(len(df))
    df.to_csv(csv_path, index=False)
    print(f"  ✓ Normalized SE salaries: {len(df)} rows with numeric salary_usd")


# ─────────────────────────────────────────────────────────────
# Dataset registry
# ─────────────────────────────────────────────────────────────
DATASETS = {
    # Global software-engineer salary benchmark (engine's "kaggle_salary" source).
    "salary": {
        "id": "emreksz/software-engineer-jobs-and-salaries-2024",
        "rename_to": "ai_job_software_engineer_2024.csv",  # matches "ai_job" pattern
        "description": "Software Engineer Jobs & Salaries 2024 (global SE roles)",
        "post_process": _normalize_se_salaries,
    },
    # Local Vietnam jobs (engine's "topcv" source) — already matches TopCVParser.
    "topcv": {
        "id": "baocgb/vietnam-it-jobs-raw-data-from-topcv-2026",
        "rename_to": "topcv_vietnam_it_jobs_2026.csv",  # matches "topcv" pattern
        "description": "Vietnam IT Jobs raw data from TopCV 2026 (local market)",
        "post_process": None,
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
