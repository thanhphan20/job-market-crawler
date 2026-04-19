import pandas as pd
import os
import glob
from config.settings import RAW_DATA_DIR, PATTERNS
from analytics.standardizer import DataStandardizer


class KaggleUnifier:
    """
    Unifies Global datasets with dynamic discovery.
    """

    def __init__(self, raw_dir=RAW_DATA_DIR):
        self.raw_dir = raw_dir

    def _find_file_by_pattern(self, key, required_cols=None):
        pattern = os.path.join(self.raw_dir, "**", f"*{PATTERNS[key]}*.csv")
        files = glob.glob(pattern, recursive=True)

        candidates = []
        for f in files:
            if required_cols:
                try:
                    # Just read the first row to check columns
                    df_check = pd.read_csv(f, nrows=1)
                    if all(col in df_check.columns for col in required_cols):
                        candidates.append(f)
                except:
                    continue
            else:
                candidates.append(f)

        if candidates:
            return max(candidates, key=os.path.getsize)
        return None

    def unify(self):
        print("[*] Unified Intelligence Discovery Process...")

        path_sal = self._find_file_by_pattern(
            "kaggle_salary", required_cols=["job_title", "salary_usd"]
        )
        path_imp = self._find_file_by_pattern(
            "kaggle_impact", required_cols=["Automation Risk (%)"]
        )
        path_ins = self._find_file_by_pattern(
            "kaggle_insights", required_cols=["Job_Growth_Projection"]
        )

        if not path_sal:
            print("[!] Error: Global Salary dataset not found.")
            return None, None

        # 1. Main Salary Data
        df_sal = pd.read_csv(path_sal)
        df_sal["std_role"] = df_sal["job_title"].apply(
            DataStandardizer.standardize_title
        )

        benchmarks = (
            df_sal.groupby("std_role")
            .agg({"salary_usd": ["mean", "median", "min", "max"], "job_id": "count"})
            .reset_index()
        )
        benchmarks.columns = [
            "std_role",
            "global_salary_mean",
            "global_salary_median",
            "global_salary_min",
            "global_salary_max",
            "global_job_count",
        ]

        # Evolution Support (if work_year exists)
        if "work_year" not in df_sal.columns:
            # Fake some distribution if not found for the line chart (or just skip)
            df_sal["work_year"] = 2025  # Fallback

        # 2. Impact Data
        if path_imp:
            df_imp = pd.read_csv(path_imp)
            risk_col = [
                c
                for c in df_imp.columns
                if "risk" in c.lower() or "automation" in c.lower()
            ]
            title_col = [c for c in df_imp.columns if "title" in c.lower()][0]

            if risk_col:
                df_imp["std_role"] = df_imp[title_col].apply(
                    DataStandardizer.standardize_title
                )
                risk_stats = (
                    df_imp.groupby("std_role")[risk_col[0]].mean().reset_index()
                )
                risk_stats.rename(
                    columns={risk_col[0]: "avg_automation_risk_pct"}, inplace=True
                )
                benchmarks = benchmarks.merge(risk_stats, on="std_role", how="left")

        # 3. Insights Data
        if path_ins:
            df_ins = pd.read_csv(path_ins)
            proj_col = [
                c
                for c in df_ins.columns
                if "growth" in c.lower() or "projection" in c.lower()
            ]
            title_col = [c for c in df_ins.columns if "title" in c.lower()][0]

            if proj_col:
                df_ins["std_role"] = df_ins[title_col].apply(
                    DataStandardizer.standardize_title
                )
                growth_stats = (
                    df_ins.groupby("std_role")[proj_col[0]]
                    .agg(lambda x: x.mode()[0] if not x.empty else "Unknown")
                    .reset_index()
                )
                benchmarks = benchmarks.merge(growth_stats, on="std_role", how="left")

        return benchmarks, df_sal
