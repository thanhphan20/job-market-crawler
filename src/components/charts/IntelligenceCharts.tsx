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
  Area
} from 'recharts';

export interface TechStat {
  tech: string;
  demand: number;
  globalAvgSalary: number;
  localAvgSalary: number | null;
  resilienceScore: number;
  riskLevel: string;
}

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
        <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
          <XAxis 
            type="number" 
            stroke="#737373" 
            fontSize={12} 
            tickFormatter={(value) => `$${value}`}
          />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke="#FAFAFA" 
            fontSize={12} 
            width={100}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0A0A0A', border: '1px solid #262626' }}
            itemStyle={{ color: '#EAB308' }}
            formatter={(value: any) => [`$${(value || 0).toLocaleString()}/mo`, 'Monthly Gap']}
          />
          <Bar dataKey="gap" fill="#EAB308">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fillOpacity={0.4 + (index / chartData.length) * 0.6} />
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
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorRes" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EAB308" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#EAB308" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="name" stroke="#737373" fontSize={10} />
          <YAxis hide domain={[0, 100]} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0A0A0A', border: '1px solid #262626' }}
          />
          <Area 
            type="monotone" 
            dataKey="score" 
            stroke="#EAB308" 
            fillOpacity={1} 
            fill="url(#colorRes)" 
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
