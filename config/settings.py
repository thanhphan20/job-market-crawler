from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import os
# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    DATA_DIR = Path("/tmp/data")
    RAW_DATA_DIR = BASE_DIR / "data" / "raw" # Read from repo
    OUTPUT_DIR = Path("/tmp/reports")
    SYNC_DIR = Path("/tmp/data/sync")
else:
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    OUTPUT_DIR = BASE_DIR / "analytics" / "reports"
    SYNC_DIR = DATA_DIR / "sync"

# Ensure directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR]:
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[WARN] Could not create {folder}: {e}")

# Dataset Specific Patterns (to avoid hardcoding exact names)
PATTERNS = {
    "topcv": "topcv",
    "kaggle_salary": "ai_job",
    "kaggle_impact": "impact",
    "kaggle_insights": "powered",
}

# Currency / Logic Settings
VND_USD_RATE = 25000
