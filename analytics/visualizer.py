import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import networkx as nx
from config.settings import OUTPUT_DIR


class MarketVisualizer:
    """
    Premium Visualization Engine for Market Intelligence.
    Generates 8+ distinct chart types for the full-flow report.
    """

    def __init__(self, report_dir=OUTPUT_DIR):
        # On Vercel, use /tmp for output
        if os.environ.get("VERCEL") == "1":
            from pathlib import Path
            self.report_dir = Path("/tmp/reports")
        else:
            self.report_dir = report_dir
            
        try:
            self.report_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[WARN] Could not create report directory {self.report_dir}: {e}")

        # High-end design tokens
        self.palette = "viridis"
        self.dark_mode = True
        self._apply_style()

    def _apply_style(self):
        plt.style.use("dark_background" if self.dark_mode else "seaborn-v0_8-whitegrid")
        plt.rcParams.update(
            {
                "figure.facecolor": "#121212",
                "axes.facecolor": "#121212",
                "font.family": "sans-serif",
                "grid.alpha": 0.1,
            }
        )

    def plot_salary_distribution(self, df, ts):
        """[1/8] Salary Distribution Insights (Global)"""
        if "salary_usd" not in df.columns:
            return
        plt.figure(figsize=(12, 6))
        sns.histplot(df["salary_usd"], kde=True, color="#00d4ff", alpha=0.6)
        plt.title(
            "Salary Distribution: Global AI Talent (2025)",
            fontsize=16,
            fontweight="bold",
        )
        plt.savefig(self.report_dir / f"salary_distribution_insight_{ts}.png")
        plt.close()

    def plot_ai_impact_matrix(self, df, ts):
        """[2/8] AI Impact Matrix (Risk vs Trend)"""
        # Expecting standardized correlation df
        if "avg_automation_risk_pct" not in df.columns or df.empty:
            return
        try:
            plt.figure(figsize=(14, 8))
            # Pivoting data for heatmap
            matrix = df.pivot_table(index="std_role", values="avg_automation_risk_pct")
            if matrix.empty or matrix.size == 0:
                plt.close()
                return
            sns.heatmap(matrix, annot=True, cmap="YlOrRd", cbar_kws={"label": "Risk %"})
            plt.title(
                "AI Impact Matrix: Automation Risk by Role", fontsize=16, fontweight="bold"
            )
            plt.savefig(self.report_dir / f"ai_impact_matrix_{ts}.png")
            plt.close()
        except (ValueError, Exception) as e:
            print(f"[WARN] Could not generate AI Impact Matrix: {e}")
            plt.close()

    def plot_global_skills_ranking(self, skills_series, ts):
        """[3/8] Global Skills Demand (Kaggle)"""
        plt.figure(figsize=(12, 8))
        sns.barplot(
            x=skills_series.values,
            y=skills_series.index,
            hue=skills_series.index,
            palette="mako",
            legend=False,
        )
        plt.title(
            "Global Tech Demand: Most Required Skills", fontsize=16, fontweight="bold"
        )
        plt.savefig(self.report_dir / f"global_skills_ranking_{ts}.png")
        plt.close()

    def plot_salary_evolution(self, df, ts):
        """[4/8] Salary Evolution (2020-2026/2030)"""
        if "work_year" not in df.columns:
            return
        sal_col = "salary_usd" if "salary_usd" in df.columns else "salary"
        plt.figure(figsize=(10, 6))
        sns.lineplot(
            data=df,
            x="work_year",
            y=sal_col,
            estimator="median",
            marker="o",
            color="#ff007f",
        )
        plt.title(
            "Market Evolution: Global Salary Projection", fontsize=16, fontweight="bold"
        )
        plt.savefig(self.report_dir / f"salary_evolution_{ts}.png")
        plt.close()

    def plot_job_skills_ranking(self, df, ts):
        """[5/8] Local Job Skills Ranking (TopCV + ITviec) — top 15 roles."""
        if df.empty or "standardized_title" not in df.columns:
            return
        counts = df["standardized_title"].value_counts().head(20)
        if len(counts) == 0:
            return
        plt.figure(figsize=(12, max(6, 0.5 * len(counts))))
        sns.barplot(
            x=counts.values,
            y=counts.index,
            hue=counts.index,
            palette="flare",
            legend=False,
        )
        plt.title("Local Demand: Top 20 Roles", fontsize=16, fontweight="bold")
        plt.xlabel("Job Postings")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(self.report_dir / f"job_skills_ranking_{ts}.png",
                    bbox_inches="tight", dpi=120)
        plt.close()

    def plot_market_demand_group(self, df, ts):
        """[6/8] Market Demand Groups — top 8 roles + Others, donut w/ legend."""
        if df.empty or "standardized_title" not in df.columns:
            return
        counts = df["standardized_title"].value_counts()
        if len(counts) == 0:
            return
        top = counts.head(12)
        labels = list(top.index)
        values = list(top.values)
        others = int(counts[12:].sum())
        if others > 0:
            labels.append("Others")
            values.append(others)

        plt.figure(figsize=(11, 8))
        colors = sns.color_palette("viridis", len(values))
        wedges, _texts, autotexts = plt.pie(
            values,
            autopct=lambda p: f"{p:.0f}%" if p >= 4 else "",
            startangle=140,
            colors=colors,
            pctdistance=0.8,
            wedgeprops=dict(width=0.42, edgecolor="#121212"),
        )
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(9)
        plt.legend(wedges, labels, title="Roles", loc="center left",
                   bbox_to_anchor=(1.0, 0.5), fontsize=9, frameon=False)
        plt.title("Market Demand: Talent Group Share (Top 12)",
                  fontsize=16, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.report_dir / f"market_demand_group_{ts}.png",
                    bbox_inches="tight", dpi=120)
        plt.close()

    def plot_skill_network(self, df, ts):
        """[7/8] Role convergence — top 15 roles around the dominant hub."""
        if df.empty or "standardized_title" not in df.columns:
            return
        counts = df["standardized_title"].value_counts().head(15)
        if len(counts) < 2:
            return
        roles = list(counts.index)
        hub = roles[0]

        G = nx.Graph()
        for r in roles:
            G.add_node(r)
        for r in roles[1:]:
            G.add_edge(hub, r)  # star from the dominant role — no hairball

        plt.figure(figsize=(13, 10))
        pos = nx.spring_layout(G, k=2.4, seed=42)
        sizes = [400 + (counts[n] ** 0.5) * 90 for n in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color="#EAB308", alpha=0.85)
        nx.draw_networkx_edges(G, pos, width=1.2, edge_color="gray", alpha=0.35)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="white",
                                bbox=dict(facecolor="#121212", edgecolor="none", alpha=0.6, pad=1))
        plt.title("Role Convergence: Top Local Roles", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(self.report_dir / f"skill_network_{ts}.png",
                    bbox_inches="tight", dpi=120)
        plt.close()

    def plot_correlation_audit(self, df, ts):
        """[8/8] Correlation: Skill vs Experience vs Salary"""
        if df.empty or "local_avg_exp" not in df.columns or "local_salary_avg" not in df.columns:
            return
        # Filter to rows with valid data
        df_valid = df[(df["local_avg_exp"].notna()) & (df["local_salary_avg"].notna()) & (df["local_salary_avg"] > 0)]
        if df_valid.empty:
            return
        plt.figure(figsize=(10, 6))
        sns.regplot(
            data=df_valid,
            x="local_avg_exp",
            y="local_salary_avg",
            scatter_kws={"s": 100, "alpha": 0.5},
            color="#00ff00",
        )
        plt.title(
            "Correlation Audit: Seniority vs. Earning Power",
            fontsize=16,
            fontweight="bold",
        )
        plt.xlabel("Avg Experience (Years)")
        plt.ylabel("Avg Salary (USD)")
        plt.savefig(
            self.report_dir / f"correlation_between_skill_experien_salary_{ts}.png"
        )
        plt.close()
