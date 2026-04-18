import requests
import zipfile
import os
import shutil

def fetch_so_survey_2025(url, target_dir="data"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    zip_path = os.path.join(target_dir, "so_survey_2025.zip")
    
    print(f"[*] Downloading Stack Overflow 2025 dataset from: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"[+] Download complete: {zip_path}")
        
        print("[*] Extracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # We only care about the survey_results_public.csv
            # Find it in the zip
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith("survey_results_public.csv"):
                    # Extract it as data/so_survey_2025.csv
                    with zip_ref.open(file_info) as source, open(os.path.join(target_dir, "so_survey_2025.csv"), "wb") as target:
                        shutil.copyfileobj(source, target)
                    print(f"[+] Extracted: {file_info.filename} -> data/so_survey_2025.csv")
                    break
        
        # Cleanup
        os.remove(zip_path)
        print("[+] Cleanup complete.")
        return True
    except Exception as e:
        print(f"[!] Failed to fetch data: {e}")
        return False

if __name__ == "__main__":
    SO_URL_2025 = "https://survey.stackoverflow.co/datasets/stack-overflow-developer-survey-2025.zip"
    fetch_so_survey_2025(SO_URL_2025)
