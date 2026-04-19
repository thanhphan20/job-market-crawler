import zipfile
import os


def extract_all():
    data_dir = r"e:\Repository\job-market-crawler\data"
    raw_dir = os.path.join(data_dir, "raw")

    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    for item in os.listdir(data_dir):
        if item.endswith(".zip"):
            zip_path = os.path.join(data_dir, item)
            target_dir = os.path.join(raw_dir, item.replace(".zip", ""))

            print(f"[*] Extracting {item}...")
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(target_dir)
                print(f"[+] Done: {target_dir}")
            except Exception as e:
                print(f"[!] Failed {item}: {e}")

    print("\n--- Listing Files ---")
    for root, dirs, files in os.walk(raw_dir):
        for f in files:
            if f.endswith(".csv"):
                print(os.path.join(root, f))


if __name__ == "__main__":
    extract_all()
