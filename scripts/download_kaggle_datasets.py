"""
Automated Kaggle Dataset Downloader

Downloads and prepares datasets for the Intelligence Engine.
Requires: pip install kaggle
Setup: https://www.kaggle.com/settings/account (create API token)
"""

import os
import subprocess
import shutil
from pathlib import Path
import zipfile


# Curated Kaggle datasets for this project
DATASETS = {
    "salary": {
        "id": "ruchi798/data-science-job-salaries",
        "files": ["ds_salaries.csv"],
        "rename_to": "ai_job_market_2025.csv",
        "description": "Data Science Job Salaries (607 records with global salary data)",
    },
    "impact": {
        "id": "bimarsalim/ai-powered-job-market-insights",
        "files": ["*impact*.csv", "*automation*.csv"],
        "rename_to": "ai_impact_2024_2030.csv",
        "description": "AI Impact & Automation Risk by Job/Industry",
    },
    "insights": {
        "id": "cedricaubin/data-science-salary-2020-2026",
        "files": ["*salary*.csv", "*2020*.csv"],
        "rename_to": "ai_data_science_2020_2026.csv",
        "description": "Data Science Salary Evolution (2020-2026 trends)",
    },
}


def check_kaggle_installed():
    """Check if kaggle CLI is installed."""
    try:
        subprocess.run(["kaggle", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_kaggle_credentials():
    """Check if Kaggle credentials are configured."""
    cred_path = Path.home() / ".kaggle" / "kaggle.json"
    return cred_path.exists()


def download_dataset(dataset_id, target_dir):
    """Download a single dataset from Kaggle."""
    try:
        cmd = ["kaggle", "datasets", "download", "-d", dataset_id, "-p", str(target_dir)]
        print(f"  Downloading {dataset_id}...")
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Download failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def extract_and_rename(target_dir, original_files, rename_to):
    """Extract ZIP and rename matching CSV files."""
    try:
        # Find and extract ZIP files
        for zip_file in Path(target_dir).glob("*.zip"):
            print(f"  Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(target_dir)
            zip_file.unlink()  # Remove ZIP after extraction

        # Find matching CSV files
        found_files = []
        for pattern in original_files if isinstance(original_files, list) else [original_files]:
            found_files.extend(Path(target_dir).glob(pattern))

        if found_files:
            # Rename the first matching file
            src = found_files[0]
            dst = Path(target_dir).parent / rename_to
            shutil.move(str(src), str(dst))
            print(f"  ✓ Extracted and renamed to {rename_to}")

            # Clean up any other extracted files
            for extra_file in Path(target_dir).glob("*.csv"):
                if extra_file != dst:
                    extra_file.unlink()

            return True
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")

    return False


def download_all_datasets(data_dir=None):
    """Download and prepare all required Kaggle datasets."""
    if data_dir is None:
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent
        data_dir = repo_root / "data"
    else:
        data_dir = Path(data_dir)

    data_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print(" KAGGLE DATASET DOWNLOADER")
    print("=" * 60 + "\n")

    # Check prerequisites
    if not check_kaggle_installed():
        print("[!] Kaggle CLI not installed.")
        print("    Install with: pip install kaggle")
        return False

    if not check_kaggle_credentials():
        print("[!] Kaggle credentials not configured.")
        print("    1. Go to: https://www.kaggle.com/settings/account")
        print("    2. Click 'Create New API Token' (downloads kaggle.json)")
        print("    3. Move kaggle.json to ~/.kaggle/")
        print("    4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False

    print("[✓] Kaggle CLI configured\n")

    # Download each dataset
    all_success = True
    for dataset_key, dataset_info in DATASETS.items():
        print(f"[*] {dataset_key.upper()}: {dataset_info['description']}")

        # Create temp directory for download
        temp_dir = data_dir / f"_download_{dataset_key}"
        temp_dir.mkdir(exist_ok=True)

        # Download
        if download_dataset(dataset_info["id"], temp_dir):
            # Extract and rename
            if extract_and_rename(
                temp_dir,
                dataset_info["files"],
                dataset_info["rename_to"]
            ):
                print()
            else:
                print(f"  ✗ Failed to process {dataset_key}\n")
                all_success = False
                # Clean up temp dir
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print(f"  ✗ Failed to download {dataset_key}\n")
            all_success = False
            # Clean up temp dir
            shutil.rmtree(temp_dir, ignore_errors=True)

    # Final summary
    print("=" * 60)
    if all_success:
        print("[SUCCESS] All datasets downloaded and ready!")
        print(f"Location: {data_dir}")
        print("\nNext: python3 main.py --flow")
    else:
        print("[!] Some datasets failed. Check errors above.")
        print("    Tip: Ensure datasets still exist on Kaggle")
    print("=" * 60 + "\n")

    return all_success


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else None
    download_all_datasets(data_dir)
