'use client';

import { useState, useEffect } from 'react';

interface KaggleRow {
  std_role: string;
  global_salary_mean: number;
  global_salary_median: number;
  global_salary_min: number;
  global_salary_max: number;
  global_job_count: number;
  local_salary_avg: number;
  local_job_count: number;
}

export default function KaggleDataTable({ initialData }: { initialData?: KaggleRow[] }) {
  const [data, setData] = useState<KaggleRow[]>(initialData || []);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) return;
    
    fetch('/api/kaggle-data')
      .then(res => res.json())
      .then(d => {
        if (Array.isArray(d)) {
          setData(d);
        } else if (d.error) {
          setError(d.error);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [initialData]);

  if (loading) return <div className="p-10 text-center animate-pulse text-zinc-500 font-mono text-xs">LOADING_KAGGLE_INTELLIGENCE...</div>;
  
  if (error) return (
    <div className="p-10 border border-red-900/50 bg-red-900/10 text-red-400 font-mono text-[10px] rounded-sm">
      <p className="font-bold uppercase mb-2">[!] DATA_FETCH_ERROR</p>
      <p>{error}</p>
      <p className="mt-4 text-zinc-500 italic">Hint: Make sure the FastAPI server is running on port 8000.</p>
    </div>
  );

  return (
    <div className="overflow-x-auto border border-zinc-800 bg-black/40 backdrop-blur-md rounded-sm no-scrollbar">
      <table className="w-full text-left font-mono text-[10px] border-collapse">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/50">
            <th className="p-3 text-accent uppercase tracking-widest">Standardized Role</th>
            <th className="p-3 text-zinc-500 uppercase tracking-widest">Global Median ($)</th>
            <th className="p-3 text-zinc-500 uppercase tracking-widest">Global Range ($)</th>
            <th className="p-3 text-zinc-500 uppercase tracking-widest">Kaggle Samples</th>
            <th className="p-3 text-zinc-500 uppercase tracking-widest">Local Avg ($)</th>
            <th className="p-3 text-zinc-500 uppercase tracking-widest">VN Demand</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-b border-zinc-900/50 hover:bg-white/5 transition-colors group">
              <td className="p-3 text-white font-bold group-hover:text-accent">{row.std_role}</td>
              <td className="p-3 text-zinc-400 font-black">${row.global_salary_median.toLocaleString()}</td>
              <td className="p-3 text-zinc-500">
                <span className="text-zinc-600">${row.global_salary_min.toLocaleString()}</span>
                <span className="mx-2 text-zinc-800">—</span>
                <span className="text-zinc-600">${row.global_salary_max.toLocaleString()}</span>
              </td>
              <td className="p-3 text-zinc-500">{row.global_job_count}</td>
              <td className="p-3 text-zinc-400">${row.local_salary_avg.toLocaleString()}</td>
              <td className="p-3 text-accent">{row.local_job_count} jobs</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
