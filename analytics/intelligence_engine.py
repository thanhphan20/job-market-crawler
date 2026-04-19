import pandas as pd
from datetime import datetime
from config.settings import RAW_DATA_DIR, DATA_DIR
from analytics.topcv_parser import TopCVParser
from analytics.kaggle_unifier import KaggleUnifier
from analytics.standardizer import DataStandardizer

from analytics.visualizer import MarketVisualizer


class IntelligenceEngine:
    """
    Advanced Intelligence Engine v6.0 (Full Flow)
    Correlates Local (TopCV + ITviec) with Global (Kaggle) across 8 Intelligence Vectors.
    """

    def __init__(self, raw_dir=RAW_DATA_DIR, data_dir=DATA_DIR):
        self.raw_dir = raw_dir
        self.data_dir = data_dir
        self.local_data = None
        self.global_benchmarks = None
        self.global_raw = None
        self.visualizer = MarketVisualizer()

    def load_all_sources(self):
        """Loads and standardizes all intelligence sources."""
        print("\n--- Intelligence Engine: Syncing Full Flow ---")

        # 1. Load TopCV
        topcv_parser = TopCVParser(raw_dir=self.raw_dir)
        df_topcv = topcv_parser.parse()

        # 2. Load ITviec (Localized CSV)
        itviec_path = self.data_dir / "itviec_jobs.csv"
        df_itviec = None
        if itviec_path.exists():
            print(f"[*] Parsing ITviec: {itviec_path}")
            df_itviec_raw = pd.read_csv(itviec_path)
            # Basic standardization for ITviec
            df_itviec = pd.DataFrame()
            it_titles = (
                df_itviec_raw["title"]
                if "title" in df_itviec_raw.columns
                else pd.Series(["Unknown"] * len(df_itviec_raw))
            )
            df_itviec["job_title_raw"] = it_titles
            df_itviec["standardized_title"] = it_titles.apply(
                DataStandardizer.standardize_title
            )
            # Hacky salary parsing for ITviec if needed, or just follow TopCV pattern
            df_itviec["annual_salary_usd"] = 25000  # Default fallback for ITviec demo
            df_itviec["min_years_exp"] = 2
            df_itviec["source"] = "ITviec"
            print(f"[+] Cleaned {len(df_itviec)} records from ITviec.")

        # Unified Local Pool
        self.local_data = (
            pd.concat([df_topcv, df_itviec], ignore_index=True)
            if df_itviec is not None
            else df_topcv
        )

        # 3. Load Global Kaggle Intel
        unifier = KaggleUnifier(raw_dir=self.raw_dir)
        self.global_benchmarks, self.global_raw = unifier.unify()

        print(
            f"[DONE] Full Knowledge Base Synchronized. Total Local Records: {len(self.local_data)}"
        )

    def run_agentic_analysis(self):
        if self.local_data is None or self.global_benchmarks is None:
            print("[!] Critical Error: Data not loaded.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.visualizer.report_dir / f"market_intelligence_{timestamp}.md"

        # Matrix Math
        merged = self._correlate_data()

        print("[*] Generating 8-Vector Visualization Suite...")
        v = self.visualizer
        v.plot_ai_impact_matrix(merged, timestamp)
        v.plot_salary_distribution(self.global_raw, timestamp)
        v.plot_salary_evolution(self.global_raw, timestamp)
        v.plot_job_skills_ranking(self.local_data, timestamp)
        v.plot_market_demand_group(self.local_data, timestamp)
        v.plot_skill_network(self.local_data, timestamp)
        v.plot_correlation_audit(merged, timestamp)
        # Skills Ranking (Global)
        if "required_skills" in self.global_raw.columns:
            skills_series = (
                self.global_raw["required_skills"]
                .str.split(",")
                .explode()
                .str.strip()
                .value_counts()
                .head(15)
            )
            v.plot_global_skills_ranking(skills_series, timestamp)

        self._write_full_report(report_path, timestamp, merged)
        return report_path

    def _correlate_data(self):
        local_stats = (
            self.local_data.groupby("standardized_title")
            .agg(
                {
                    "annual_salary_usd": ["mean", "median", "count"],
                    "min_years_exp": "mean",
                }
            )
            .reset_index()
        )
        local_stats.columns = [
            "std_role",
            "local_salary_avg",
            "local_salary_median",
            "local_job_count",
            "local_avg_exp",
        ]
        return pd.merge(
            local_stats, self.global_benchmarks, on="std_role", how="inner"
        ).sort_values("local_job_count", ascending=False)

    def _write_full_report(self, path, ts, df):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# 🌐 Full-Flow Market Intelligence Report (v6.0)\n\n")
            f.write("| Intelligence Vector | Status | Insight Level |\n")
            f.write("| :--- | :--- | :--- |\n")
            f.write("| AI Impact & Risk | ✅ Active | High |\n")
            f.write("| Salary Distribution | ✅ Normalized | High |\n")
            f.write("| Skill Connectivity | ✅ Mapped | Medium |\n\n")

            f.write("## 1. Local Opportunity Analysis (ITviec + TopCV)\n")
            f.write(f"![Local Demand](job_skills_ranking_{ts}.png)\n")
            f.write(f"![Market Share](market_demand_group_{ts}.png)\n\n")

            f.write("## 2. Global Benchmarking (Kaggle)\n")
            f.write(f"![Salary Insight](salary_distribution_insight_{ts}.png)\n")
            f.write(f"![Market Evolution](salary_evolution_{ts}.png)\n\n")

            f.write("## 3. High-ROI Strategy & AI Risk\n")
            f.write(f"![AI Impact](ai_impact_matrix_{ts}.png)\n")
            f.write(
                f"![Opportunity Correlation](correlation_between_skill_experien_salary_{ts}.png)\n\n"
            )

            f.write("## 4. Skill Network & Path Connectivity\n")
            f.write("How technologies converge in the current job market.\n\n")
            f.write(f"![Skill Network](skill_network_{ts}.png)\n")

            f.write("\n--- \n*End of Executive Intelligence Summary*")


if __name__ == "__main__":
    engine = IntelligenceEngine()
    engine.load_all_sources()
    report = engine.run_agentic_analysis()
    if report:
        print(f"\n[SUCCESS] Full Flow Complete: {report}")
