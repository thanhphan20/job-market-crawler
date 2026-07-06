import zipfile
import os
from pathlib import Path


def extract_all(data_dir=None):
    """Extract all ZIP files in data/ to data/raw/"""
    if data_dir is None:
        # Dynamically determine repo root (parent of scripts/)
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent
        data_dir = repo_root / "data"
    else:
        data_dir = Path(data_dir)

    raw_dir = data_dir / "raw"

    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Extracting ZIPs from {data_dir} to {raw_dir}...")

    if not data_dir.exists():
        print(f"[!] Data directory not found: {data_dir}")
        return

    for item in data_dir.iterdir():
        if item.suffix.lower() == ".zip":
            target_dir = raw_dir / item.stem
            print(f"[*] Extracting {item.name}...")
            try:
                with zipfile.ZipFile(item, "r") as zip_ref:
                    zip_ref.extractall(target_dir)
                print(f"[+] Done: {target_dir}")
            except Exception as e:
                print(f"[!] Failed {item.name}: {e}")

    print("\n--- Extracted CSV Files ---")
    for csv_file in raw_dir.rglob("*.csv"):
        print(csv_file.relative_to(raw_dir.parent))


if __name__ == "__main__":
    extract_all()
