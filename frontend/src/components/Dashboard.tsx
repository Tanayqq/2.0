import React, { useEffect, useState } from 'react';
import { Activity, Database, CheckCircle, AlertCircle, Server, Info } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

interface DashboardMetrics {
  total_drugs: number;
  total_chunks: number;
  complete: number;
  incomplete: number;
  avg_sections: number;
  avg_chunks: number;
  corpus_version: string;
  authorities: {
    DailyMed: number;
    openFDA: number;
  };
}

export function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/dashboard`)
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load dashboard metrics", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-slate-400">
        <Activity className="h-6 w-6 animate-spin" />
        <span className="ml-3 font-mono-dash text-sm">LOADING METRICS...</span>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex h-full items-center justify-center text-rose-400">
        <AlertCircle className="h-6 w-6" />
        <span className="ml-3 font-mono-dash text-sm">FAILED TO LOAD METRICS</span>
      </div>
    );
  }

  const completenessRatio = metrics.total_drugs > 0 
    ? (metrics.complete / metrics.total_drugs) * 100 
    : 0;

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <Database className="h-6 w-6 text-cyan-500" />
            Corpus Health Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">Admin Panel for Pipeline Ingestion & Retrieval Metrics</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-mono-dash text-slate-500 uppercase tracking-widest">Corpus Version</span>
            <span className="text-sm font-bold text-emerald-400 font-mono-dash bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-900/50 mt-1">
              {metrics.corpus_version}
            </span>
          </div>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard 
          title="Drugs Indexed" 
          value={metrics.total_drugs} 
          icon={<Database className="h-4 w-4 text-cyan-500" />} 
          borderClass="border-cyan-900/50"
          bgClass="bg-cyan-950/10"
        />
        <MetricCard 
          title="Complete Profiles" 
          value={metrics.complete} 
          icon={<CheckCircle className="h-4 w-4 text-emerald-500" />} 
          borderClass="border-emerald-900/50"
          bgClass="bg-emerald-950/10"
        />
        <MetricCard 
          title="Incomplete Profiles" 
          value={metrics.incomplete} 
          icon={<AlertCircle className="h-4 w-4 text-yellow-500" />} 
          borderClass="border-yellow-900/50"
          bgClass="bg-yellow-950/10"
        />
        <MetricCard 
          title="Total Chunks" 
          value={metrics.total_chunks.toLocaleString()} 
          icon={<Server className="h-4 w-4 text-indigo-500" />} 
          borderClass="border-indigo-900/50"
          bgClass="bg-indigo-950/10"
        />
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Completeness Progress */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#090e17] flex flex-col gap-5">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-300 uppercase tracking-wider font-mono-dash">
            <Activity className="h-4 w-4 text-slate-500" /> Average Completeness
          </div>
          
          <div className="flex flex-col gap-2 mt-2">
            <div className="flex justify-between items-end">
              <span className="text-4xl font-bold text-white tracking-tighter">
                {completenessRatio.toFixed(1)}%
              </span>
              <span className="text-xs text-slate-500 font-mono-dash mb-1">
                {metrics.complete} / {metrics.total_drugs} DRUGS
              </span>
            </div>
            
            <div className="h-3 w-full bg-slate-900 rounded-full overflow-hidden flex border border-slate-800">
              <div 
                className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400" 
                style={{ width: `${completenessRatio}%` }}
              />
            </div>
          </div>
        </div>

        {/* Authorities Breakdown */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#090e17] flex flex-col gap-5">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-300 uppercase tracking-wider font-mono-dash">
            <Database className="h-4 w-4 text-slate-500" /> Authorities
          </div>
          
          <div className="flex flex-col gap-4 mt-2">
            <AuthorityBar 
              label="DailyMed" 
              count={metrics.authorities.DailyMed} 
              total={metrics.total_drugs} 
              color="bg-emerald-500" 
            />
            <AuthorityBar 
              label="openFDA" 
              count={metrics.authorities.openFDA} 
              total={metrics.total_drugs} 
              color="bg-blue-500" 
            />
          </div>
        </div>
      </div>

      {/* Averages Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              <Info className="h-4 w-4 text-slate-400" />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash">Avg Sections / Drug</span>
              <span className="text-lg font-bold text-slate-200">{metrics.avg_sections.toFixed(1)}</span>
            </div>
          </div>
        </div>
        
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              <Database className="h-4 w-4 text-slate-400" />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash">Avg Chunks / Drug</span>
              <span className="text-lg font-bold text-slate-200">{metrics.avg_chunks.toFixed(1)}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

function MetricCard({ title, value, icon, borderClass, bgClass }: { title: string, value: string | number, icon: React.ReactNode, borderClass: string, bgClass: string }) {
  return (
    <div className={`p-5 rounded-xl border ${borderClass} ${bgClass} flex flex-col gap-3 relative overflow-hidden`}>
      <div className="flex items-center gap-2 z-10">
        {icon}
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono-dash">{title}</span>
      </div>
      <div className="text-3xl font-bold text-white tracking-tight z-10">{value}</div>
      
      {/* Decorative background icon */}
      <div className="absolute -right-4 -bottom-4 opacity-10 transform scale-150 grayscale">
        {icon}
      </div>
    </div>
  );
}

function AuthorityBar({ label, count, total, color }: { label: string, count: number, total: number, color: string }) {
  const percent = total > 0 ? (count / total) * 100 : 0;
  
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center text-xs font-bold text-slate-400">
        <span>{label}</span>
        <span className="font-mono-dash text-[10px]">{count} DRUGS</span>
      </div>
      <div className="h-2 w-full bg-slate-800 rounded overflow-hidden flex">
        <div 
          className={`h-full ${color}`} 
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
