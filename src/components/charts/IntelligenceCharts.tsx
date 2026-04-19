'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  AreaChart,
  Area,
  TooltipProps
} from 'recharts';

export interface TechStat {
  tech: string;
  demand: number;
  globalAvgSalary: number;
  localAvgSalary: number | null;
  resilienceScore: number;
  riskLevel: string;
}

export interface SalaryTrend {
  year: number;
  avgSalary: number;
}

export interface ImpactData {
  industry: string;
  status: string;
  automationRisk: number;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#0A0A0A] border border-[#262626] p-3 font-mono text-[10px] uppercase tracking-wider shadow-xl">
        <p className="text-foreground font-black mb-1">{label}</p>
        <div className="space-y-1">
          {payload.map((p, index) => (
            <p key={index} style={{ color: p.color }}>
              {p.name}: {typeof p.value === 'number' && p.value > 1000 ? `$${p.value.toLocaleString()}` : `${p.value}%`}
            </p>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

export function OpportunityGapChart({ data }: { data: TechStat[] }) {
  const chartData = data
    .map((d) => ({
      name: d.tech,
      gap: (d.globalAvgSalary / 12) - (d.localAvgSalary || 0),
      demand: d.demand
    }))
    .sort((a, b) => b.gap - a.gap);

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
          <XAxis 
            type="number" 
            stroke="#737373" 
            fontSize={10} 
            tickFormatter={(value) => `$${value}`}
          />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke="#FAFAFA" 
            fontSize={10} 
            width={80}
            tick={{ fontWeight: 700 }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#171717' }} />
          <Bar dataKey="gap" fill="#EAB308" name="Monthly Gap">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fillOpacity={0.3 + (index / chartData.length) * 0.7} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SalaryEvolutionChart({ data }: { data: SalaryTrend[] }) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorSalary" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EAB308" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#EAB308" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="1 4" stroke="#262626" vertical={false} />
          <XAxis dataKey="year" stroke="#737373" fontSize={10} axisLine={false} tickLine={false} />
          <YAxis stroke="#737373" fontSize={10} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v/1000}k`} />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="stepAfter" 
            dataKey="avgSalary" 
            stroke="#EAB308" 
            fillOpacity={1} 
            fill="url(#colorSalary)" 
            strokeWidth={3}
            name="Avg Salary"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ImpactHeatmap({ data }: { data: ImpactData[] }) {
  const sortedData = [...data].sort((a, b) => b.automationRisk - a.automationRisk);
  
  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sortedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
          <XAxis dataKey="industry" stroke="#737373" fontSize={10} tick={{ fontSize: 8 }} interval={0} angle={-45} textAnchor="end" height={80} />
          <YAxis stroke="#737373" fontSize={10} unit="%" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="automationRisk" name="Risk %">
            {sortedData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.automationRisk > 70 ? '#ef4444' : entry.automationRisk > 40 ? '#eab308' : '#22c55e'} 
                fillOpacity={0.8}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AIResilienceRadar({ data }: { data: TechStat[] }) {
  const chartData = data.map(d => ({
    name: d.tech,
    score: d.resilienceScore,
    demand: d.demand
  }));

  return (
    <div className="h-[250px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorRes" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EAB308" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#EAB308" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="name" stroke="#737373" fontSize={10} hide />
          <YAxis hide domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="score" 
            stroke="#EAB308" 
            fillOpacity={1} 
            fill="url(#colorRes)" 
            strokeWidth={2}
            name="Resilience"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
