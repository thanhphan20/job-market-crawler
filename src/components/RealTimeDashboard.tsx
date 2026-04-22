'use client';

import { useState, useEffect } from 'react';
import { 
  OpportunityGapChart, 
  AIResilienceRadar, 
  SalaryEvolutionChart, 
  ImpactHeatmap,
  SkillMatrixChart,
  CorrelationChart,
  GlobalMarketShareChart
} from "@/components/charts/IntelligenceCharts";
import { TechStat, SalaryTrend, ImpactData, SkillStat, CorrelationPoint, MarketRegion } from "./charts/IntelligenceCharts";
import SyncTerminal from "./SyncTerminal";
import KaggleDataTable from "./KaggleDataTable";

interface Props {
  initialData: {
    intelligence: TechStat[];
    trends: SalaryTrend[];
    impact: ImpactData[];
    skills: SkillStat[];
    correlation: CorrelationPoint[];
    marketShare: MarketRegion[];
    rawTable: any[];
    lastSync: string | null;
  };
}

export default function RealTimeDashboard({ initialData }: Props) {
  const [data, setData] = useState(initialData);
  const [tab, setTab] = useState('local');

  const refreshData = async () => {
    try {
      const res = await fetch('/api/market-data');
      if (res.ok) {
        const json = await res.json();
        setData({
          intelligence: json.intelligence || initialData.intelligence,
          trends: json.trends || initialData.trends,
          impact: json.impact || initialData.impact,
          skills: json.skills || initialData.skills,
          correlation: json.correlation || initialData.correlation,
          marketShare: json.marketShare || initialData.marketShare,
          rawTable: json.rawTable || initialData.rawTable,
          lastSync: json.updated_at || initialData.lastSync
        });
        console.log("[DASHBOARD] Cloud data hot-refreshed.");
      }
    } catch (e) {
      console.error("Failed to refresh chart data:", e);
    }
  };

  useEffect(() => {
    window.addEventListener('intel-sync-complete', refreshData);
    return () => window.removeEventListener('intel-sync-complete', refreshData);
  }, []);

  return (
    <div className="space-y-10">
      {/* Header with Last Sync */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-border pb-6 gap-4">
        <div>
          <h1 className="text-4xl font-black glow-text">Job Market Intelligence</h1>
          <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] mt-1">
            Global AI Impact & Local Arbitrage Monitoring v6.1
          </p>
        </div>
        <div className="terminal-card py-2 px-4 border-accent/30 bg-accent/5">
          <p className="terminal-label text-accent">Status: ONLINE</p>
          <p className="font-mono text-[10px] text-zinc-400">
            LAST_SYNC: {data.lastSync ? new Date(data.lastSync).toLocaleString() : 'NEVER_SYNCED'}
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex gap-4 border-b border-border mb-8 overflow-x-auto no-scrollbar">
        {['local', 'global', 'impact', 'skills', 'raw'].map((t) => (
          <button 
            key={t}
            onClick={() => setTab(t)} 
            className={`nav-tab capitalize ${tab === t ? 'active' : ''}`}
          >
            {t === 'local' ? 'Local Market' : 
             t === 'global' ? 'Global Trends' : 
             t === 'impact' ? 'AI Impact' : 
             t === 'skills' ? 'Skill Matrix' : 'Raw Data'}
          </button>
        ))}
      </nav>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3 items-start">
        {/* Main Content Area (Tabs) */}
        <div className="lg:col-span-2 space-y-12 min-w-0">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            {tab === 'local' && (
              <div className="space-y-12">
                <section className="terminal-card">
                  <h2 className="mb-6 flex items-center gap-2">
                    <span className="h-2 w-2 bg-accent animate-pulse" />
                    VN Market: Opportunity Gap ($/mo Potential)
                  </h2>
                  <div className="w-full">
                    <OpportunityGapChart data={data.intelligence} />
                  </div>
                </section>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <section className="terminal-card min-h-[400px]">
                    <h2 className="mb-6 text-xs font-bold text-accent uppercase tracking-[0.3em]">AI Resilience Profile</h2>
                    <AIResilienceRadar data={data.intelligence} />
                  </section>
                  <section className="terminal-card min-h-[400px]">
                    <h2 className="mb-6 text-xs font-bold text-accent uppercase tracking-[0.3em]">Market Velocity</h2>
                    <div className="space-y-6">
                      {(data.intelligence || []).slice(0, 6).map(t => (
                        <div key={t.tech} className="flex justify-between items-center border-b border-border/50 pb-3 group hover:border-accent/30 transition-colors">
                          <span className="text-xs font-bold text-zinc-300">{t.tech}</span>
                          <div className="text-right">
                            <span className="text-accent font-black block leading-none">{t.demand}</span>
                            <span className="text-[8px] text-zinc-500 uppercase tracking-tighter">Jobs Indexed</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              </div>
            )}

            {tab === 'global' && (
              <div className="space-y-12">
                <section className="terminal-card">
                  <h2 className="mb-10 text-lg font-black uppercase italic tracking-tighter">Global Market Share & Volume</h2>
                  <div className="">
                    <GlobalMarketShareChart data={data.marketShare} />
                  </div>
                </section>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <section className="terminal-card min-h-[400px]">
                    <h2 className="mb-10 text-xs font-bold text-accent uppercase tracking-widest">Global Salary Evolution</h2>
                    <SalaryEvolutionChart data={data.trends} />
                  </section>
                  <section className="terminal-card min-h-[400px]">
                    <h2 className="mb-10 text-xs font-bold text-accent uppercase tracking-widest">Experience ROI Heatmap</h2>
                    <CorrelationChart data={data.correlation} />
                  </section>
                </div>
              </div>
            )}

            {tab === 'impact' && (
              <section className="terminal-card">
                <h2 className="mb-8">AI Automation Risk Matrix</h2>
                <ImpactHeatmap data={data.impact} />
              </section>
            )}

            {tab === 'skills' && (
              <section className="terminal-card">
                <h2 className="mb-8">Skill Relevance Matrix</h2>
                <SkillMatrixChart data={data.skills} />
              </section>
            )}

            {tab === 'raw' && (
              <section className="terminal-card">
                <h2 className="mb-8 flex items-center gap-2">
                  <span className="h-2 w-2 bg-accent animate-pulse" />
                  Kaggle Unified Intelligence Dataset ({data.rawTable?.length || 0} Roles)
                </h2>
                <KaggleDataTable initialData={data.rawTable} />
              </section>
            )}
          </div>
        </div>

        {/* Persistent Aside (Terminal & Intel) */}
        <aside className="space-y-6 sticky top-24">
          <section className="terminal-card bg-black/50">
            <SyncTerminal />
          </section>
        </aside>
      </div>
    </div>
  );
}
