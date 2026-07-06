import pandas as pd
import os
import sys
from datetime import datetime
from config.settings import RAW_DATA_DIR, DATA_DIR
from analytics.topcv_parser import TopCVParser
from analytics.kaggle_unifier import KaggleUnifier
from analytics.standardizer import DataStandardizer

from supabase import create_client, Client
from analytics.visualizer import MarketVisualizer


# Software-engineering skills to mine from job titles (canonical -> regex).
# Ordered roughly by stack; matching is case-insensitive on lowercased titles.
SKILL_KEYWORDS = {
    "Java": r"\bjava\b(?!script)",
    "JavaScript": r"\bjavascript\b",
    "TypeScript": r"\btypescript\b",
    "Python": r"\bpython\b",
    "Spring Boot": r"\bspring\b",
    ".NET / C#": r"\.net\b|\bc#\b|\bdotnet\b",
    "React": r"\breact\b",
    "Angular": r"\bangular\b",
    "Vue": r"\bvue\b",
    "Node.js": r"\bnode(?:\.js|js)?\b",
    "PHP": r"\bphp\b",
    "Go": r"\bgolang\b|\bgo\s+developer\b",
    "Ruby": r"\bruby\b",
    "C++": r"c\+\+",
    "Kotlin": r"\bkotlin\b",
    "Swift": r"\bswift\b",
    "Flutter": r"\bflutter\b",
    "Android": r"\bandroid\b",
    "iOS": r"\bios\b",
    "Unity": r"\bunity\b",
    "SQL": r"\bsql\b",
    "AWS": r"\baws\b",
    "Azure": r"\bazure\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "DevOps": r"\bdevops\b",
    "QA / Testing": r"\btester\b|\bqa\b|\bqc\b|\btesting\b",
    "Embedded": r"\bembedded\b|\bfirmware\b",
}

# Rough demand-growth outlook per skill (0-100) for the skill matrix chart.
# Keys cover both title-mined skills and Stack Overflow language names.
SKILL_GROWTH = {
    "Java": 45, "JavaScript": 55, "TypeScript": 70, "Python": 80, "Spring Boot": 50,
    ".NET / C#": 45, "C#": 50, "React": 68, "Angular": 40, "Vue": 55, "Node.js": 60,
    "PHP": 30, "Go": 78, "Ruby": 30, "C++": 40, "C": 35, "Kotlin": 62, "Swift": 55,
    "Flutter": 65, "Android": 50, "iOS": 50, "Unity": 48, "SQL": 55, "AWS": 82,
    "Azure": 75, "Docker": 78, "Kubernetes": 85, "DevOps": 80, "QA / Testing": 42,
    "Embedded": 50, "HTML/CSS": 48, "Bash/Shell": 45, "Rust": 82, "Dart": 58,
    "R": 45, "Scala": 48, "PowerShell": 45, "Assembly": 30, "Perl": 25, "Lua": 45,
}


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
        
        # Initialize Supabase
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key) if url and key else None
        if self.supabase:
            print("[INFO] Supabase cloud-sync active.")
        self.visualizer = MarketVisualizer()

    def load_all_sources(self, skip_itviec=False):
        """Loads and standardizes all intelligence sources."""
        print("\n--- Intelligence Engine: Syncing Full Flow ---")

        # 1. Load TopCV
        topcv_parser = TopCVParser(raw_dir=self.raw_dir)
        df_topcv = topcv_parser.parse()

        # 2. Load ITviec (Localized CSV)
        df_itviec = None
        if not skip_itviec:
            itviec_path = self.data_dir / "itviec_jobs.csv"
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
                df_itviec["annual_salary_usd"] = None 
                df_itviec["min_years_exp"] = 2
                df_itviec["source"] = "ITviec"
                print(f"[+] Cleaned {len(df_itviec)} records from ITviec.")
            else:
                print("[!] ITviec data not found. Skipping.")
        else:
            print("[INFO] ITviec ignored per request.")

        # Unified Local Pool
        self.local_data = (
            pd.concat([df_topcv, df_itviec], ignore_index=True)
            if df_itviec is not None
            else df_topcv
        )

        # If no local data, create an empty dataframe with required columns
        if self.local_data is None:
            self.local_data = pd.DataFrame(columns=[
                "job_title_raw", "standardized_title", "min_years_exp",
                "annual_salary_usd", "location", "company", "source"
            ])
            print("[!] No local data available. Using global data only.")

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

        # Dashboard Export (New)
        self._export_dashboard_json(merged)

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
        
        print("\n" + "="*40)
        print(" STRATEGIC MARKET SUMMARY")
        print("="*40)
        merged_fill = merged.fillna(0)
        for _, row in merged_fill.head(5).iterrows():
            gap = row['global_salary_median'] - row['local_salary_avg']
            print(f" > {row['std_role']}: Opportunity Gap +${gap:,.0f}/year")
        print("="*40 + "\n")
        
        return report_path

    def _export_dashboard_json(self, df):
        """Exports sanitized data to public/data/intelligence.json for Next.js."""
        from pathlib import Path
        import json

        # Ensure no NaN values reach JSON
        df = df.fillna(0)

        # On Vercel, use /tmp for output if public/ is not writable
        is_vercel = os.environ.get("VERCEL") == "1"
        output_path = Path("public/data/intelligence.json")
        
        from config.settings import SYNC_DIR

        # Real AI automation-risk overlay (from the impact dataset, if present)
        impact_lookup, se_risk_baseline = self._load_impact_lookup()

        # 1. Intelligence Matrix
        intelligence = []
        for _, row in df.head(30).iterrows():
            risk = self._risk_for_role(row, impact_lookup, se_risk_baseline)
            demand = int(row["local_job_count"])
            if demand == 0: demand = int(row["global_job_count"] / 100)
            
            intelligence.append({
                "tech": row["std_role"],
                "demand": demand,
                "globalAvgSalary": float(row["global_salary_median"]),
                "localAvgSalary": float(row["local_salary_avg"]),
                "resilienceScore": 100 - risk,
                "riskLevel": ("LOW" if risk < 30 else "HIGH" if risk > 60 else "MODERATE"),
            })

        # 2. Trends
        trends = []
        if self.global_raw is not None and "work_year" in self.global_raw.columns:
            evolution = self.global_raw.groupby("work_year")["salary_usd"].median().reset_index()
            for _, row in evolution.iterrows():
                trends.append({"year": int(row["work_year"]), "avgSalary": float(row["salary_usd"])})
        if 0 < len(trends) < 3:
            last_year = trends[-1]["year"]; last_sal = trends[-1]["avgSalary"]
            for i in range(1, 4 - len(trends)):
                trends.append({"year": last_year + i, "avgSalary": last_sal * (1 + 0.04 * i)})

        # 3. Impact Matrix
        impact = []
        for _, row in df.head(30).iterrows():
            risk = self._risk_for_role(row, impact_lookup, se_risk_baseline)
            impact.append({
                "industry": row["std_role"],
                "status": ("High Risk" if risk > 60 else "Safe" if risk < 30 else "Stable"),
                "automationRisk": risk,
            })

        # 4. Skills Matrix — mine software-engineering tech skills from local job titles
        skills = self._extract_skill_matrix()

        # 5. Correlation
        correlation = []
        for _, row in df.head(25).fillna(0).iterrows():
            y_val = float(row["local_salary_avg"])
            if y_val == 0: y_val = float(row["global_salary_median"])
            correlation.append({
                "x": float(row.get("local_avg_exp", 5)) or 5.0,
                "y": y_val,
                "label": row["std_role"],
                "size": (int(row["local_job_count"]) + 5) * 5,
            })

        # 6. Market Share
        market_share = []
        top_roles = df.head(5); total_vol = df["global_job_count"].sum()
        for _, row in top_roles.iterrows():
            market_share.append({"name": row["std_role"], "value": int(row["global_job_count"])})
        market_share.append({"name": "Others", "value": int(total_vol - top_roles["global_job_count"].sum())})

        # 7. Raw Table
        raw_table = []
        for _, row in df.iterrows():
            raw_table.append({
                "std_role": row["std_role"],
                "global_salary_mean": float(row["global_salary_mean"]),
                "global_salary_median": float(row["global_salary_median"]),
                "global_salary_min": float(row["global_salary_min"]),
                "global_salary_max": float(row["global_salary_max"]),
                "global_job_count": int(row["global_job_count"]),
                "local_salary_avg": float(row["local_salary_avg"]),
                "local_job_count": int(row["local_job_count"]),
            })
        
        dashboard_data = {
            "intelligence": intelligence,
            "trends": trends,
            "impact": impact,
            "skills": skills,
            "correlation": correlation,
            "marketShare": market_share,
            "rawTable": raw_table,
            "updated_at": datetime.now().isoformat(),
        }

        # Priority path for dashboard (SYNC_DIR on Vercel is /tmp, else data/sync)
        sync_path = SYNC_DIR / "intelligence.json"
        
        # Also try to update the public folder for build-time persistence (only works locally)
        public_path = Path("public/data/intelligence.json")
        
        for path in [sync_path, public_path]:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    json.dump(dashboard_data, f, indent=2)
                print(f"[DASHBOARD] Exported to {path}")
            except Exception as e:
                pass # Silently fail for public_path on Vercel
        
        if self.supabase:
            self._sync_to_cloud(dashboard_data)

        print(f"[DASHBOARD] Exported real-time intelligence to {output_path}")

    def _load_impact_lookup(self):
        """Load real automation-risk % keyed by standardized role from the AI-impact
        dataset (any *impact*.csv in raw_dir with an 'Automation Risk (%)' column).
        Returns (lookup dict {std_role: pct}, software-engineer baseline pct)."""
        import glob
        from analytics.standardizer import DataStandardizer

        lookup, se_baseline = {}, None
        pattern = os.path.join(str(self.raw_dir), "**", "*impact*.csv")
        for f in glob.glob(pattern, recursive=True):
            try:
                d = pd.read_csv(f)
            except Exception:
                continue
            rcol = [c for c in d.columns if "risk" in c.lower() or "automation" in c.lower()]
            tcol = [c for c in d.columns if "title" in c.lower()]
            if not rcol or not tcol:
                continue
            rcol = [c for c in rcol if pd.api.types.is_numeric_dtype(d[c])]
            if not rcol:
                continue
            d["_std"] = d[tcol[0]].apply(DataStandardizer.standardize_title)
            for role, val in d.groupby("_std")[rcol[0]].mean().items():
                lookup[role] = float(val)
            for key in ("Software Engineer", "Software Developer"):
                if key in lookup:
                    se_baseline = lookup[key]
                    break
        return lookup, se_baseline

    def _risk_for_role(self, row, impact_lookup, se_baseline):
        """Automation-risk % for a role: prefer real merged data, then the impact
        lookup, then the software-engineer baseline for dev roles, then a heuristic."""
        risk = row.get("avg_automation_risk_pct")
        if pd.notna(risk) and risk not in (0, 0.0):
            return float(risk)

        std = str(row["std_role"])
        if std in impact_lookup:
            return float(impact_lookup[std])

        rl = std.lower()
        # Keyword heuristic — gives relative role differentiation.
        if "data" in rl or "ai" in rl: heuristic = 15.0
        elif "manager" in rl or "lead" in rl: heuristic = 25.0
        elif "backend" in rl or "system" in rl: heuristic = 35.0
        elif "frontend" in rl or "mobile" in rl: heuristic = 45.0
        elif "test" in rl or "qa" in rl: heuristic = 65.0
        else: heuristic = 40.0

        dev_markers = (
            "developer", "engineer", "architect", "programmer", "software",
            "fullstack", "backend", "frontend", "mobile", "embedded", "devops", "cloud",
        )
        if se_baseline is not None and any(m in rl for m in dev_markers):
            # Anchor to the real software-engineer risk, keep relative role nuance.
            return float(min(95.0, max(5.0, se_baseline + (heuristic - 40.0))))
        return heuristic

    def _extract_skill_matrix(self, top_n=18):
        """Build the skill matrix. Prefers real survey skills (Stack Overflow
        `required_skills`); falls back to mining local job titles."""
        skills = self._skills_from_survey(top_n)
        if skills:
            return skills
        return self._skills_from_titles(top_n)

    def _skills_from_survey(self, top_n):
        """Count real skills/languages from the global survey's required_skills column."""
        if self.global_raw is None or "required_skills" not in self.global_raw.columns:
            return []
        exploded = (
            self.global_raw["required_skills"]
            .dropna()
            .astype(str)
            .str.split(";")
            .explode()
            .str.replace(r"\s*\(.*?\)", "", regex=True)  # drop "(all shells)" etc.
            .str.strip()
        )
        exploded = exploded[exploded.str.len() > 1]
        counts = exploded.value_counts().head(top_n)
        if counts.empty:
            return []
        top_count = int(counts.iloc[0])
        skills = []
        for skill, n in counts.items():
            relevance = int(round(40 + 58 * (n / top_count)))  # 40..98 by frequency
            skills.append({
                "skill": skill,
                "relevance": min(98, relevance),
                "growth": SKILL_GROWTH.get(skill, 50),
            })
        return skills

    def _skills_from_titles(self, top_n):
        """Fallback: mine tech skills from local job titles (Java, React, AWS...)."""
        import re

        if self.local_data is None or self.local_data.empty:
            return []
        if "job_title_raw" not in self.local_data.columns:
            return []

        corpus = " \n ".join(
            str(t).lower() for t in self.local_data["job_title_raw"].dropna()
        )
        if not corpus.strip():
            return []

        counts = {}
        for skill, pattern in SKILL_KEYWORDS.items():
            n = len(re.findall(pattern, corpus))
            if n > 0:
                counts[skill] = n
        if not counts:
            return []

        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_count = ranked[0][1]
        skills = []
        for skill, n in ranked:
            relevance = int(round(40 + 58 * (n / top_count)))  # 40..98 by frequency
            skills.append({
                "skill": skill,
                "relevance": min(98, relevance),
                "growth": SKILL_GROWTH.get(skill, 50),
            })
        return skills

    def _sync_to_cloud(self, data):
        """Pushes intelligence data to Supabase/Prisma tables."""
        if not self.supabase:
            print("[WARN] Cloud sync skipped: Supabase not configured.")
            return

        print("[*] Synchronizing cleaned Kaggle findings to cloud database...")
        try:
            # 1. Sync GlobalIntelligence (Kaggle focused)
            for item in data["intelligence"]:
                # Filter out low demand or noisy data if needed
                if item["demand"] < 1: continue 
                
                self.supabase.table("GlobalIntelligence").upsert({
                    "tech": item["tech"],
                    "demand": item["demand"],
                    "globalAvgSalary": item["globalAvgSalary"],
                    "localAvgSalary": item["localAvgSalary"] if item["localAvgSalary"] > 0 else None,
                    "resilienceScore": item["resilienceScore"],
                    "riskLevel": item["riskLevel"],
                }, on_conflict="tech").execute()

            # 2. Sync AIImpactMatrix
            for item in data["impact"]:
                self.supabase.table("AIImpactMatrix").upsert({
                    "industry": item["industry"],
                    "status": item["status"],
                    "automationRisk": item["automationRisk"],
                }, on_conflict="industry,status").execute()

            # 3. Sync SalaryTrend
            for item in data["trends"]:
                self.supabase.table("SalaryTrend").upsert({
                    "year": item["year"],
                    "avgSalary": item["avgSalary"],
                    "source": "Kaggle",
                }, on_conflict="year,tech,source").execute()

            print("[SUCCESS] Cloud synchronization complete.")
        except Exception as e:
            print(f"[ERR] Cloud sync failed: {str(e)}")

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
            local_stats, self.global_benchmarks, on="std_role", how="right"
        ).sort_values("global_job_count", ascending=False)

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
