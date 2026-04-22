'use client';

import { useState, useEffect } from 'react';
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ScatterChart,
  Scatter,
  ZAxis,
  Treemap
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

export interface SkillStat {
  skill: string;
  relevance: number;
  growth: number;
}

export interface CorrelationPoint {
  x: number;
  y: number;
  label: string;
  size: number;
}

export interface MarketRegion {
  name: string;
  value: number;
  [key: string]: string | number | undefined;
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) => {
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
  const [mounted, setMounted] = useState(false);
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return <div className="h-[400px] w-full bg-border/10 animate-pulse" />;

  const chartData = data
    .map((d) => ({
      name: d.tech,
      gap: (d.globalAvgSalary / 12) - (d.localAvgSalary || 0),
      demand: d.demand
    }))
    .sort((a, b) => b.gap - a.gap);

  return (
    <div className="h-auto w-full min-h-[400px]">
      <ResponsiveContainer width="99%" aspect={1.5}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
          <XAxis 
            type="number" 
            stroke="#737373" 
            fontSize={10} 
            tickFormatter={(_value) => `$${_value}`}
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
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  if (!mounted) return <div className="h-[250px] w-full bg-border/10 animate-pulse" />;

  return (
    <div className="h-auto w-full min-h-[250px]">
      <ResponsiveContainer width="99%" aspect={2}>
        <AreaChart data={data.length === 1 ? [...data, { ...data[0], year: data[0].year + 1 }] : data}>
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
    <div className=" w-full min-h-[400px]">
      <ResponsiveContainer width="99%" aspect={1.5}>
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
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
  }, []);

  if (!mounted) return <div className="h-[250px] w-full bg-border/10 animate-pulse" />;
  
  const chartData = data.map(d => ({
    subject: d.tech,
    A: d.resilienceScore,
    fullMark: 100,
  })).slice(0, 6);

  return (
    <div className="h-auto w-full min-h-[250px] flex items-center justify-center">
      <ResponsiveContainer width="99%" aspect={1.5}>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#262626" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#737373', fontSize: 8 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Resilience"
            dataKey="A"
            stroke="#EAB308"
            fill="#EAB308"
            fillOpacity={0.4}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SkillMatrixChart({ data }: { data: SkillStat[] }) {
  const [mounted, setMounted] = useState(false);
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return <div className="h-[400px] w-full bg-border/10 animate-pulse" />;

  return (
    <div className=" w-full min-h-[400px]">
      <ResponsiveContainer width="99%" aspect={1.5}>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#262626" />
          <PolarAngleAxis dataKey="skill" tick={{ fill: '#737373', fontSize: 10 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Skill Relevance"
            dataKey="relevance"
            stroke="#EAB308"
            fill="#EAB308"
            fillOpacity={0.2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CorrelationChart({ data }: { data: CorrelationPoint[] }) {
  const [mounted, setMounted] = useState(false);
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return <div className="h-[400px] w-full bg-border/10 animate-pulse" />;

  return (
    <div className=" w-full min-h-[400px]">
      <ResponsiveContainer width="99%" aspect={1.5}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Experience" 
            unit="yrs" 
            stroke="#737373" 
            fontSize={10}
            domain={['auto', 'auto']}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Salary" 
            unit="$" 
            stroke="#737373" 
            fontSize={10} 
            domain={['auto', 'auto']}
            tickFormatter={(v) => `$${v/1000}k`}
          />
          <ZAxis type="number" dataKey="size" range={[60, 400]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
          <Scatter 
            name="Market Correlation" 
            data={data} 
            fill="#EAB308" 
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function GlobalMarketShareChart({ data }: { data: MarketRegion[] }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  if (!mounted) return <div className="h-[400px] w-full bg-border/10 animate-pulse" />;

  return (
    <div className="h-auto w-full min-h-[400px]">
      <ResponsiveContainer width="99%" aspect={2} minWidth={0} minHeight={0}>
        <Treemap
          data={data}
          dataKey="value"
          stroke="#060606"
          fill="#EAB308"
          content={<CustomTreemapContent />}
        >
          <Tooltip content={<CustomTooltip />} />
        </Treemap>
      </ResponsiveContainer>
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTreemapContent = (props: any) => {
  const { x, y, width, height, index, name } = props;
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: '#EAB308',
          fillOpacity: 0.3 + (index / 6) * 0.6,
          stroke: 'none',
        }}
      />
      {width > 50 && height > 30 && (
        <text
          x={x + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#FFFFFF"
          fontSize={14}
          fontWeight={900}
          className="uppercase tracking-tighter drop-shadow-md"
        >
          {name}
        </text>
      )}
    </g>
  );
};
