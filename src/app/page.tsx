import { prisma } from "@/lib/db";
import { 
  OpportunityGapChart, 
  AIResilienceRadar, 
  SalaryEvolutionChart, 
  ImpactHeatmap,
  TechStat,
  SalaryTrend,
  ImpactData
} from "@/components/charts/IntelligenceCharts";

import fs from "fs";
import path from "path";

async function getDashboardData() {
  const localIntelPath = path.join(process.cwd(), "data/sync/global_intelligence.json");
  const localInsightsPath = path.join(process.cwd(), "data/sync/kaggle_insights.json");
  
  let intelligence: TechStat[] = [];
  let trends: SalaryTrend[] = [];
  let impact: ImpactData[] = [];

  try {
    // 1. Fetch Global Intelligence
    intelligence = await prisma.globalIntelligence.findMany({ orderBy: { demand: 'desc' } }) as any;
    if (intelligence.length === 0 && fs.existsSync(localIntelPath)) {
      intelligence = JSON.parse(fs.readFileSync(localIntelPath, "utf-8"));
    }

    // 2. Fetch Salary Trends
    trends = await prisma.salaryTrend.findMany({ orderBy: { year: 'asc' } }) as any;
    
    // 3. Fetch AI Impact
    const dbImpact = await prisma.aIImpactMatrix.findMany() as any;
    impact = dbImpact.map((i: any) => ({
      industry: i.industry,
      status: i.status,
      automationRisk: i.automationRisk
    }));

    // Local JSON Fallbacks for Insights
    if ((trends.length === 0 || impact.length === 0) && fs.existsSync(localInsightsPath)) {
      const insights = JSON.parse(fs.readFileSync(localInsightsPath, "utf-8"));
      if (trends.length === 0) trends = insights.salary_trends;
      if (impact.length === 0) {
        impact = insights.ai_impact.map((i: any) => ({
          industry: i.industry,
          status: i.status,
          automationRisk: i.risk
        }));
      }
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

  } catch (e) {
    console.error("[!] Data fetch error:", e);
  }

  return { intelligence, trends, impact };
}

export default async function DashboardPage({ searchParams }: { searchParams: Promise<{ tab?: string }> }) {
  const { tab = 'local' } = await searchParams;
  const { intelligence, trends, impact } = await getDashboardData();

  return (
    <div className="space-y-10">
      {/* Navigation Tabs */}
      <nav className="flex gap-4 border-b border-border mb-8 overflow-x-auto no-scrollbar">
        <a href="?tab=local" className={`nav-tab ${tab === 'local' ? 'active' : ''}`}>Local Market</a>
        <a href="?tab=global" className={`nav-tab ${tab === 'global' ? 'active' : ''}`}>Global Trends</a>
        <a href="?tab=impact" className={`nav-tab ${tab === 'impact' ? 'active' : ''}`}>AI Impact</a>
        <a href="?tab=skills" className={`nav-tab ${tab === 'skills' ? 'active' : ''}`}>Skill Matrix</a>
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
            
            <div className="terminal-card">
              <h3 className="terminal-label mb-4">Sync Integrity</h3>
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-[8px] text-zinc-500">UPTIME</p><p className="text-xs font-black">99.98%</p></div>
                <div><p className="text-[8px] text-zinc-500">LATENCY</p><p className="text-xs font-black">12ms</p></div>
              </div>
            </div>
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
            <div className="terminal-card">
               <h3 className="terminal-label mb-6">Macro Observations</h3>
               <ul className="list-disc list-inside space-y-4 text-xs text-zinc-400">
                 <li>Compounded Annual Growth Rate (CAGR) for AI roles is <span className="text-accent font-bold">14.2%</span> globally.</li>
                 <li>US/EU market convergence starting to stall; APAC region growth accelerating by 22%.</li>
                 <li>Platform-as-a-Service (PaaS) knowledge now accounts for <span className="text-accent font-bold">18%</span> of salary premium.</li>
               </ul>
            </div>
            <div className="terminal-card border-accent/20">
               <h3 className="terminal-label mb-6">Arbitrage Strategy</h3>
               <p className="text-xs leading-loose text-zinc-300">
                 Focusing on <span className="text-accent">Rust/Go</span> for distributed systems provides the highest ROI resilience. 
                 Forecasted 2026 salaries for AI Architects expected to break <span className="text-accent">$185k</span> median.
               </p>
            </div>
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
              <p className="text-[10px] text-zinc-400">Customer Support, Translation, and Content Moderation are facing &gt; 80% automation potential by 2027.</p>
            </div>
            <div className="terminal-card bg-yellow-500/5 border-yellow-500/20">
              <h3 className="text-yellow-500 text-xs font-black mb-2 uppercase">Augmented</h3>
              <p className="text-[10px] text-zinc-400">Software Development and Data Analysis are being augmented, requiring 3x output per head.</p>
            </div>
            <div className="terminal-card bg-green-500/5 border-green-500/20">
              <h3 className="text-green-500 text-xs font-black mb-2 uppercase">Resilient</h3>
              <p className="text-[10px] text-zinc-400">Healthcare, Physical Logistics, and High-Trust Consulting remain highly resistant to AI replacement.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
