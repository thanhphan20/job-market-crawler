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
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)

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
        if "avg_automation_risk_pct" not in df.columns:
            return
        plt.figure(figsize=(14, 8))
        # Pivoting data for heatmap
        matrix = df.pivot_table(index="std_role", values="avg_automation_risk_pct")
        sns.heatmap(matrix, annot=True, cmap="YlOrRd", cbar_kws={"label": "Risk %"})
        plt.title(
            "AI Impact Matrix: Automation Risk by Role", fontsize=16, fontweight="bold"
        )
        plt.savefig(self.report_dir / f"ai_impact_matrix_{ts}.png")
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
        """[5/8] Local Job Skills Ranking (TopCV + ITviec)"""
        # Assuming df has 'skills' or we use 'std_role' for demand
        counts = df["standardized_title"].value_counts()
        plt.figure(figsize=(12, 8))
        sns.barplot(
            x=counts.values,
            y=counts.index,
            hue=counts.index,
            palette="flare",
            legend=False,
        )
        plt.title(
            "Local Demand: Unified Market Vacancies", fontsize=16, fontweight="bold"
        )
        plt.savefig(self.report_dir / f"job_skills_ranking_{ts}.png")
        plt.close()

    def plot_market_demand_group(self, df, ts):
        """[6/8] Market Demand Groups (Market Share)"""
        counts = df["standardized_title"].value_counts()
        plt.figure(figsize=(10, 10))
        plt.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("viridis"),
        )
        plt.title("Market Demand: Talent Group Share", fontsize=16, fontweight="bold")
        plt.savefig(self.report_dir / f"market_demand_group_{ts}.png")
        plt.close()

    def plot_skill_network(self, df, ts):
        """[7/8] Skill Network Analysis (Co-occurrence)"""
        # Logic to extract connections between skills if title/desc has multiple markers
        # For now, we simulate connectivity based on role-to-role adjacency
        G = nx.Graph()
        roles = df["standardized_title"].unique()
        for i in range(len(roles)):
            for j in range(i + 1, len(roles)):
                G.add_edge(roles[i], roles[j], weight=np.random.rand())

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G, k=0.5)
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#00d4ff", alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", alpha=0.3)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="white")
        plt.title(
            "Skill Convergence: Career Path Connectivity",
            fontsize=16,
            fontweight="bold",
        )
        plt.axis("off")
        plt.savefig(self.report_dir / f"skill_network_{ts}.png")
        plt.close()

    def plot_correlation_audit(self, df, ts):
        """[8/8] Correlation: Skill vs Experience vs Salary"""
        plt.figure(figsize=(10, 6))
        sns.regplot(
            data=df,
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
