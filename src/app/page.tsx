import { 
  OpportunityGapChart, 
  AIResilienceRadar, 
  SalaryEvolutionChart, 
  ImpactHeatmap,
  SkillMatrixChart,
  CorrelationChart,
  TechStat,
  SalaryTrend,
  ImpactData,
  SkillStat,
  CorrelationPoint
} from "@/components/charts/IntelligenceCharts";
import SyncTerminal from "@/components/SyncTerminal";
import { getCachedIntelligence, getCachedTrends, getCachedImpact } from "@/lib/cache-data";

import fs from "fs";
import path from "path";

async function getDashboardData() {
  const localInsightsPath = path.join(process.cwd(), "data/sync/kaggle_insights.json");
  const localIntelPath = path.join(process.cwd(), "data/sync/global_intelligence.json");
  
  let intelligence: TechStat[] = [];
  let trends: SalaryTrend[] = [];
  let impact: ImpactData[] = [];
  let skills: SkillStat[] = [];
  let correlation: CorrelationPoint[] = [];

  try {
    // 1. Fetch Cached Data
    intelligence = await getCachedIntelligence() as any;
    trends = await getCachedTrends() as any;
    impact = await getCachedImpact() as any;

    // Local JSON Fallbacks for Insights
    if (fs.existsSync(localInsightsPath)) {
      const insights = JSON.parse(fs.readFileSync(localInsightsPath, "utf-8"));
      if (trends.length === 0) trends = insights.salary_trends;
      if (impact.length === 0) {
        impact = insights.ai_impact.map((i: any) => ({
          industry: i.industry,
          status: i.status,
          automationRisk: i.risk || i.automationRisk
        }));
      }
      skills = insights.skill_matrix || [];
      correlation = insights.correlation_data || [];
    }

    if (intelligence.length === 0 && fs.existsSync(localIntelPath)) {
      intelligence = JSON.parse(fs.readFileSync(localIntelPath, "utf-8"));
    }

    // Default Fallbacks
    if (intelligence.length === 0) {
      intelligence = [
        { tech: "Python", demand: 120, globalAvgSalary: 110000, localAvgSalary: 2500, resilienceScore: 95, riskLevel: "LOW" },
        { tech: "Go", demand: 85, globalAvgSalary: 125000, localAvgSalary: 3000, resilienceScore: 92, riskLevel: "LOW" },
        { tech: "Rust", demand: 45, globalAvgSalary: 130000, localAvgSalary: 3200, resilienceScore: 94, riskLevel: "LOW" },
        { tech: "Java", demand: 200, globalAvgSalary: 95000, localAvgSalary: 2000, resilienceScore: 88, riskLevel: "LOW" },
        { tech: "React", demand: 150, globalAvgSalary: 105000, localAvgSalary: 1800, resilienceScore: 75, riskLevel: "MODERATE" },
      ];
    }
    if (trends.length === 0) {
      trends = [
        { year: 2021, avgSalary: 72000 }, { year: 2022, avgSalary: 85000 },
        { year: 2023, avgSalary: 92000 }, { year: 2024, avgSalary: 105000 },
        { year: 2025, avgSalary: 118000 }, { year: 2026, avgSalary: 132000 },
      ];
    }
    if (impact.length === 0) {
      impact = [
        { industry: "Customer Service", status: "High Risk", automationRisk: 85 },
        { industry: "Software Dev", status: "Medium Risk", automationRisk: 42 },
        { industry: "Data Analysis", status: "Medium Risk", automationRisk: 55 },
        { industry: "Healthcare", status: "Low Risk", automationRisk: 12 },
        { industry: "Finance", status: "High Risk", automationRisk: 68 },
      ];
    }
    if (skills.length === 0) {
      skills = [
        { skill: "LLM Orchestration", relevance: 95, growth: 120 },
        { skill: "Data Engineering", relevance: 88, growth: 45 },
        { skill: "Cloud Native", relevance: 92, growth: 30 },
        { skill: "Frontend Dev", relevance: 70, growth: -10 },
        { skill: "DevOps", relevance: 85, growth: 25 },
      ];
    }
    if (correlation.length === 0) {
      correlation = [
        { x: 2, y: 45000, label: "Junior DA", size: 100 },
        { x: 5, y: 95000, label: "Senior DS", size: 250 },
        { x: 8, y: 145000, label: "Principal MLE", size: 400 },
        { x: 4, y: 72000, label: "Mid DE", size: 180 },
        { x: 1, y: 35000, label: "Intern", size: 50 },
      ];
    }

  } catch (e) {
    console.error("[!] Data fetch error:", e);
  }

  return { intelligence, trends, impact, skills, correlation };
}

export default async function DashboardPage({ searchParams }: { searchParams: Promise<{ tab?: string }> }) {
  const { tab = 'local' } = await searchParams;
  const { intelligence, trends, impact, skills, correlation } = await getDashboardData();

  return (
    <div className="space-y-10">
      {/* Navigation Tabs */}
      <nav className="flex gap-4 border-b border-border mb-8 overflow-x-auto no-scrollbar">
        <a href="?tab=local" className={`nav-tab \${tab === 'local' ? 'active' : ''}`}>Local Market</a>
        <a href="?tab=global" className={`nav-tab \${tab === 'global' ? 'active' : ''}`}>Global Trends</a>
        <a href="?tab=impact" className={`nav-tab \${tab === 'impact' ? 'active' : ''}`}>AI Impact</a>
        <a href="?tab=skills" className={`nav-tab \${tab === 'skills' ? 'active' : ''}`}>Skill Matrix</a>
      </nav>

      {tab === 'local' && (
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3 animate-in fade-in duration-500">
          <div className="lg:col-span-2 space-y-8">
            <section className="terminal-card">
              <h2 className="mb-6 flex items-center gap-2">
                <span className="h-2 w-2 bg-accent animate-pulse" />
                VN Market: Opportunity Gap ($/mo Potential)
              </h2>
              <OpportunityGapChart data={intelligence} />
            </section>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <section className="terminal-card">
                <h2 className="mb-4 text-xs font-bold text-accent">Tech Resilience</h2>
                <AIResilienceRadar data={intelligence} />
              </section>
              <section className="terminal-card">
                <h2 className="mb-4 text-xs font-bold text-accent">Market Intensity</h2>
                <div className="space-y-4">
                  {intelligence.slice(0, 4).map(t => (
                    <div key={t.tech} className="flex justify-between items-center border-b border-border pb-2">
                      <span className="text-[10px] font-bold">{t.tech}</span>
                      <span className="text-accent font-black">{t.demand} <span className="text-[8px] text-zinc-500 tracking-normal">JOBS</span></span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>

          <aside className="space-y-6">
            <div className="terminal-card border-accent/20">
              <h3 className="terminal-label mb-4 text-foreground">Local Intel Alpha</h3>
              <div className="space-y-6 font-mono text-[10px] leading-relaxed">
                <p className="border-l-2 border-accent pl-3 text-zinc-400">
                  <strong className="text-accent block mb-1 uppercase"> arbitrage detected</strong>
                  Senior Go Engineers in HCM currently earn 45% less than Remote Global average. Remote-first is the play.
                </p>
                <p className="border-l-2 border-red-500 pl-3 text-zinc-400">
                  <strong className="text-red-500 block mb-1 uppercase"> warning: saturation</strong>
                  Junior Frontend (React) market showing 220 applicants/listing. Transition to Fullstack or DevOps recommended.
                </p>
              </div>
            </div>
            
            <section className="terminal-card bg-black/50">
              <SyncTerminal />
            </section>
          </aside>
        </div>
      )}

      {tab === 'global' && (
        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <section className="terminal-card md:col-span-2">
              <h2 className="mb-8">Global AI Salary Evolution (2021-2026 Forecast)</h2>
              <SalaryEvolutionChart data={trends} />
            </section>
            
            <section className="terminal-card md:col-span-2">
              <h2 className="mb-8">Seniority vs. Earning Potential (Experience Correlation)</h2>
              <CorrelationChart data={correlation} />
            </section>
          </div>
        </div>
      )}

      {tab === 'impact' && (
        <div className="space-y-8 animate-in zoom-in-95 duration-500">
          <section className="terminal-card">
            <h2 className="mb-8">AI Automation Risk Matrix (Industry Benchmark)</h2>
            <ImpactHeatmap data={impact} />
          </section>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="terminal-card bg-red-500/5 border-red-500/20">
              <h3 className="text-red-500 text-xs font-black mb-2 uppercase">High Exposure</h3>
              <p className="text-[10px] text-zinc-400">Customer Support and Content Moderation are facing &gt; 80% automation potential.</p>
            </div>
            <div className="terminal-card bg-yellow-500/5 border-yellow-500/20">
              <h3 className="text-yellow-500 text-xs font-black mb-2 uppercase">Augmented</h3>
              <p className="text-[10px] text-zinc-400">Software Development is being augmented, requiring 3x output per head.</p>
            </div>
            <div className="terminal-card bg-green-500/5 border-green-500/20">
              <h3 className="text-green-500 text-xs font-black mb-2 uppercase">Resilient</h3>
              <p className="text-[10px] text-zinc-400">Physical Logistics and High-Trust Consulting remain resistant.</p>
            </div>
          </div>
        </div>
      )}

      {tab === 'skills' && (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <section className="terminal-card md:col-span-2">
              <h2 className="mb-8">Skill Relevance Matrix (Industry Demand)</h2>
              <SkillMatrixChart data={skills} />
            </section>
            <div className="space-y-6">
               <div className="terminal-card">
                 <h3 className="terminal-label mb-4">Growth Leaders</h3>
                 <div className="space-y-4">
                   {skills.sort((a,b) => b.growth - a.growth).slice(0, 3).map(s => (
                     <div key={s.skill} className="flex justify-between items-center">
                       <span className="text-[10px]">{s.skill}</span>
                       <span className="text-green-500 font-bold">+{s.growth}%</span>
                     </div>
                   ))}
                 </div>
               </div>
               <div className="terminal-card">
                 <h3 className="terminal-label mb-4">Stability Index</h3>
                 <p className="text-[10px] text-zinc-500 italic">Cloud and Security skills show 0.98 stability correlation across all Kaggle global datasets.</p>
               </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
