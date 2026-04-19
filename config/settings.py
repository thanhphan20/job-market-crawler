from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "analytics" / "reports"

# Ensure directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Dataset Specific Patterns (to avoid hardcoding exact names)
PATTERNS = {
    "topcv": "topcv",
    "kaggle_salary": "ai_job",
    "kaggle_impact": "impact",
    "kaggle_insights": "powered",
}

# Currency / Logic Settings
VND_USD_RATE = 25000
