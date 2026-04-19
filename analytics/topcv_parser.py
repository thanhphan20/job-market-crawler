import pandas as pd
import os
import glob
from config.settings import RAW_DATA_DIR, PATTERNS
from analytics.standardizer import DataStandardizer


class TopCVParser:
    """
    Parses TopCV data using dynamic file discovery.
    """

    def __init__(self, raw_dir=RAW_DATA_DIR):
        self.raw_dir = raw_dir

    def find_file(self):
        """Searches for a TopCV-like CSV file in the raw directory."""
        # Search recursively for any CSV containing 'topcv'
        pattern = os.path.join(self.raw_dir, "**", f"*{PATTERNS['topcv']}*.csv")
        files = glob.glob(pattern, recursive=True)
        return files[0] if files else None

    def parse(self):
        file_path = self.find_file()
        if not file_path:
            print(
                f"[!] Warning: No TopCV dataset found in {self.raw_dir} matching '{PATTERNS['topcv']}'"
            )
            return None

        print(f"[*] Parsing TopCV: {file_path}")
        df = pd.read_csv(file_path, encoding="utf-8-sig")

        # Mapping dict to handle flexible header names
        col_map = {
            "title": "title",
            "Job Title": "title",
            "title_raw": "title",
            "salary": "salary",
            "Salary": "salary",
            "experience": "experience",
            "Experience": "experience",
            "company": "company",
            "Company": "company",
            "location": "location",
            "Location": "location",
        }

        # Rename columns if they exist in the CSV but match our internal logic
        df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})

        df_clean = pd.DataFrame()
        # Required Columns Verification
        required = ["title", "salary", "experience"]
        for col in required:
            if col not in df.columns:
                print(f"[!] Error: TopCV file missing required column '{col}'")
                return None

        df_clean["job_title_raw"] = df["title"]
        df_clean["standardized_title"] = df["title"].apply(
            DataStandardizer.standardize_title
        )
        df_clean["min_years_exp"] = df["experience"].apply(
            DataStandardizer.parse_experience
        )
        df_clean["annual_salary_usd"] = df["salary"].apply(
            DataStandardizer.parse_salary_vnd
        )
        df_clean["location"] = df.get("location", "Vietnam")
        df_clean["company"] = df.get("company", "Unknown")
        df_clean["source"] = "TopCV"

        return df_clean


if __name__ == "__main__":
    parser = TopCVParser()
    res = parser.parse()
    if res is not None:
        print(res.head())
