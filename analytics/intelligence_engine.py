import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class MarketContext:
    def __init__(self):
        self.knowledge_base = {
            "local_itviec": None,
            "kaggle_regional": None,
            "so_global": None
        }

    def add_data(self, source, df):
        self.knowledge_base[source] = df

class AIImpactAgent:
    def __init__(self):
        self.impact_map = {
            "Frontend": {"resilience": 0.6, "risk": "High (AI UI Generation)"},
            "Backend": {"resilience": 0.85, "risk": "Moderate (Complex Logic)"},
            "Mobile": {"resilience": 0.75, "risk": "Moderate (OS Specifics)"},
            "Data/AI": {"resilience": 0.98, "risk": "Low (AI Builders)"},
            "DevOps": {"resilience": 0.92, "risk": "Low (Infra/Security)"},
            "Java": {"resilience": 0.90, "risk": "Low (Legacy/Enterprise)"},
            "Python": {"resilience": 0.95, "risk": "Low (AI Engine)"},
            "Go": {"resilience": 0.93, "risk": "Low (Performance)"},
            "Rust": {"resilience": 0.94, "risk": "Low (Safety)"},
            "PHP": {"resilience": 0.55, "risk": "High (Basic Web)"}
        }

    def get_score(self, tech):
        data = self.impact_map.get(tech, {"resilience": 0.75, "risk": "Unknown"})
        if data['resilience'] > 0.9: return "🟢 High Resilience", data['risk']
        if data['resilience'] > 0.7: return "🟡 Moderate Resilience", data['risk']
        return "🔴 Low Resilience", data['risk']

class IntelligenceEngine:
    def __init__(self):
        self.context = MarketContext()
        self.ai_agent = AIImpactAgent()
        self.global_benchmarks = {
            "Go": 85000, "Rust": 88000, "TypeScript": 77000, "Python": 75000, 
            "Java": 72000, "JavaScript": 70000, "DevOps": 85000, "AI/ML": 95000
        }

    def _parse_salary(self, salary_str):
        if not salary_str or pd.isna(salary_str) or 'sign in' in str(salary_str).lower(): return None
        nums = re.findall(r'(\d+[\.,]?\d*)', str(salary_str).replace(',', ''))
        if not nums: return None
        vals = [float(n.replace(',', '')) for n in nums]
        is_vnd = 'tr' in str(salary_str).lower() or 'vnd' in str(salary_str).lower()
        mult = (1000000 / 25400) if is_vnd else 1.0
        return max(vals) * mult

    def _parse_exp(self, text):
        if not text or pd.isna(text): return None
        matches = re.findall(r'(\d+)\s*(?:-|to)?\s*\d*\s*year', str(text).lower())
        return int(matches[0]) if matches else None

    def load_all_sources(self, data_dir="data"):
        if not os.path.exists(data_dir): return
        it_files = [f for f in os.listdir(data_dir) if "itviec" in f and f.endswith(".csv")]
        if it_files:
            df = pd.read_csv(os.path.join(data_dir, sorted(it_files)[-1]))
            # Robust normalization
            df.columns = [c.lower() for c in df.columns]
            
            # Use columns safely
            if 'salary' in df.columns: df['salary_max_usd'] = df['salary'].apply(self._parse_salary)
            if 'skills_and_experience' in df.columns: df['exp_years'] = df['skills_and_experience'].apply(self._parse_exp)
            elif 'skills' in df.columns: df['exp_years'] = df['skills'].apply(self._parse_exp)
            
            self.context.add_data("local_itviec", df)
        
        so_path = os.path.join(data_dir, "so_survey_2025_lite.csv")
        if os.path.exists(so_path):
            self.context.add_data("so_global", pd.read_csv(so_path))

    def _calculate_tech_stats(self):
        stats = {}
        target_df = self.context.knowledge_base.get("local_itviec")
        for tech, benchmark in self.global_benchmarks.items():
            count = 0
            avg_salary, avg_exp = 0, 0
            if target_df is not None and 'title' in target_df.columns:
                mask = target_df['title'].str.contains(tech, case=False, na=False)
                count = mask.sum()
                if count > 0:
                    if 'salary_max_usd' in target_df.columns: avg_salary = target_df[mask]['salary_max_usd'].mean()
                    if 'exp_years' in target_df.columns: avg_exp = target_df[mask]['exp_years'].mean()
            
            stats[tech] = {
                "demand": count, "global": benchmark, 
                "local_avg": avg_salary if not pd.isna(avg_salary) else 0,
                "local_exp": avg_exp if not pd.isna(avg_exp) else 0
            }
        return stats

    def run_agentic_analysis(self, output_dir="analytics/reports"):
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"market_intelligence_{timestamp}.md")
        
        stats = self._calculate_tech_stats()
        self._generate_visuals(output_dir, timestamp, stats)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🤖 AI-Driven Market Intelligence Report (v4.5)\n\n")
            f.write(f"![Salary Boost](salary_boost_{timestamp}.png)\n\n")
            f.write("## 🏗️ AI Impact & Resilience Matrix\n")
            f.write("| Technology | Local Demand | Avg Exp (Local) | AI Resilience | Future Risk |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            for tech, data in stats.items():
                score, risk = self.ai_agent.get_score(tech)
                f.write(f"| {tech} | {data['demand']} | {data['local_exp']:.1f}y | {score} | {risk} |\n")
            f.write("\n## 🧠 Insights: Salary & Experience Correlation\n")
            f.write(f"![Correlation Plot](correlation_{timestamp}.png)\n\n")
        return report_path

    def _generate_visuals(self, output_dir, timestamp, stats):
        try:
            plt.style.use('dark_background')
            data_list = []
            for tech, d in stats.items():
                local_monthly = d['local_avg'] if d['local_avg'] > 0 else 2500
                gap_monthly = (d['global'] / 12) - local_monthly
                data_list.append({"Tech": tech, "Demand": d['demand'], "Gap": gap_monthly, "Exp": d['local_exp']})
            df = pd.DataFrame(data_list)
            plt.figure(figsize=(12, 6))
            sns.barplot(data=df.sort_values("Gap", ascending=False), x="Gap", y="Tech", palette="magma", hue="Tech", legend=False)
            plt.title("Opportunity Gap ($/mo Potential Increase)")
            plt.tight_layout(); plt.savefig(f"{output_dir}/salary_boost_{timestamp}.png")
            plt.figure(figsize=(10, 6))
            sns.regplot(data=df, x="Exp", y="Gap", scatter_kws={'s':200}, line_kws={"color":"#00ff00"})
            plt.title("Correlation: Job Seniority vs. Earning Potential")
            plt.tight_layout(); plt.savefig(f"{output_dir}/correlation_{timestamp}.png")
            plt.close('all')
        except Exception as e:
            print(f"[!] Plotting error: {e}")

    def get_processed_data(self):
        """Returns a list of dictionaries suitable for Supabase insertion."""
        stats = self._calculate_tech_stats()
        processed = []
        for tech, data in stats.items():
            score, risk = self.ai_agent.get_score(tech)
            processed.append({
                "tech": tech,
                "demand": data['demand'],
                "globalAvgSalary": data['global'],
                "localAvgSalary": data['local_avg'],
                "resilienceScore": score,
                "riskLevel": risk
            })
        return processed

if __name__ == "__main__":
    engine = IntelligenceEngine()
    engine.load_all_sources()
    engine.run_agentic_analysis()
