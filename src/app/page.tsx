import RealTimeDashboard from "@/components/RealTimeDashboard";
import { getCachedIntelligence, getCachedTrends, getCachedImpact } from "@/lib/cache-data";
import { TechStat, SalaryTrend, ImpactData, SkillStat, CorrelationPoint, MarketRegion } from "@/components/charts/IntelligenceCharts";
import { prisma } from "@/lib/db";

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
  let rawTable: any[] = [];
  let lastSync: string | null = null;

  const isDev = process.env.NODE_ENV === "development";

  try {
    // Helper to load from files
    const loadFromFiles = () => {
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
        return true;
      }
      return false;
    };

    // Helper to load from DB
    const loadFromDB = async () => {
      const dbIntelligence = await prisma.globalIntelligence.findMany();
      if (dbIntelligence.length > 0) {
        intelligence = dbIntelligence.map(i => ({
          tech: i.tech,
          demand: i.demand,
          globalAvgSalary: i.globalAvgSalary,
          localAvgSalary: i.localAvgSalary || 0,
          resilienceScore: i.resilienceScore,
          riskLevel: i.riskLevel as any
        }));
        
        const dbTrends = await prisma.salaryTrend.findMany({ where: { source: "Kaggle" }, orderBy: { year: 'asc' } });
        trends = dbTrends.map(t => ({ year: t.year, avgSalary: t.avgSalary }));
        
        const dbImpact = await prisma.aIImpactMatrix.findMany();
        impact = dbImpact.map(im => ({ industry: im.industry, status: im.status, automationRisk: im.automationRisk }));
        
        lastSync = dbIntelligence[0]?.updatedAt.toISOString();
        console.log(`[SSR] Loaded data from CLOUD DB.`);
        return true;
      }
      return false;
    };

    if (isDev) {
      // DEV: Try Files -> then DB
      const fileSuccess = loadFromFiles();
      if (!fileSuccess) await loadFromDB();
    } else {
      // PROD: Try DB -> then Files
      const dbSuccess = await loadFromDB();
      if (!dbSuccess) loadFromFiles();
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
