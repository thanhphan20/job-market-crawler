import RealTimeDashboard from "@/components/RealTimeDashboard";
import { TechStat, SalaryTrend, ImpactData, SkillStat, CorrelationPoint, MarketRegion } from "@/components/charts/IntelligenceCharts";
import type { KaggleRow } from "@/components/KaggleDataTable";

import fs from "fs";
import path from "path";

async function getDashboardData() {
  const localInsightsPath = path.join(process.cwd(), "data/sync/kaggle_insights.json");
  const realIntelligencePath = path.join(process.cwd(), "public/data/intelligence.json");
  
  let intelligence: TechStat[] = [];
  let trends: SalaryTrend[] = [];
  let impact: ImpactData[] = [];
  let skills: SkillStat[] = [];
  let correlation: CorrelationPoint[] = [];
  let marketShare: MarketRegion[] = [];
  let rawTable: KaggleRow[] = [];
  let lastSync: string | null = null;

  try {
    if (fs.existsSync(realIntelligencePath)) {
      const realData = JSON.parse(fs.readFileSync(realIntelligencePath, "utf-8"));
      intelligence = realData.intelligence || [];
      trends = realData.trends || [];
      impact = realData.impact || [];
      skills = realData.skills || [];
      correlation = realData.correlation || [];
      marketShare = realData.marketShare || [];
      rawTable = realData.rawTable || [];
      lastSync = realData.updated_at || null;
      console.log(`[SSR] Loaded data from LOCAL FILES.`);
    }

    if (skills.length === 0 && fs.existsSync(localInsightsPath)) {
      const insights = JSON.parse(fs.readFileSync(localInsightsPath, "utf-8"));
      skills = insights.skill_matrix || [];
      correlation = insights.correlation_data || [];
      marketShare = insights.market_share || [];
    }

    // Default Fallbacks for all vectors if missing
    if (intelligence.length === 0) {
      intelligence = [
        { tech: "Python/AI", demand: 120, globalAvgSalary: 110000, localAvgSalary: 2500, resilienceScore: 95, riskLevel: "LOW" },
        { tech: "Cloud/DevOps", demand: 85, globalAvgSalary: 125000, localAvgSalary: 3000, resilienceScore: 92, riskLevel: "LOW" },
      ];
    }
    if (trends.length === 0) {
      trends = [{ year: 2024, avgSalary: 105000 }, { year: 2025, avgSalary: 110000 }];
    }
    if (skills.length === 0) {
      skills = [{ skill: "System Design", relevance: 90, growth: 20 }, { skill: "Generative AI", relevance: 98, growth: 50 }];
    }
    if (marketShare.length === 0) {
      marketShare = [{ name: "IT", value: 60 }, { name: "Finance", value: 40 }];
    }
  } catch (e) {
    console.error("[!] Data fetch error:", e);
  }

  return { intelligence, trends, impact, skills, correlation, marketShare, rawTable, lastSync };
}

export default async function Page() {
  const initialData = await getDashboardData();
  return <RealTimeDashboard initialData={initialData} />;
}
