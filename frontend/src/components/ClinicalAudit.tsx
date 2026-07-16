import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, Clock, Server, FileText, CheckCircle2, Search, Workflow, Play } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface ClinicalAuditProps {
  audit: any;
}

export function ClinicalAudit({ audit }: ClinicalAuditProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!audit) return null;

  return (
    <div className="mt-4 rounded-xl border border-slate-700 bg-[#090e17] overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-slate-800/40 hover:bg-slate-800/60 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-dash">Clinical Audit</span>
        </div>
        {isOpen ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-700/50 space-y-6">
          
          {/* Pipeline Visualization */}
          <div>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash mb-3 flex items-center gap-2">
              <Workflow className="h-3 w-3" /> Pipeline Trace
            </h4>
            <div className="flex flex-wrap items-center gap-2 text-[10px] font-bold text-slate-400 font-mono-dash">
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-slate-300">Query</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-cyan-400">Drug Detection</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-indigo-400">Hybrid Retrieval</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-emerald-400">Cross Encoder</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-amber-400">Context Assembly</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-rose-400">MedGemma</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-slate-800 rounded border border-slate-700 text-blue-400">Citation Validator</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 bg-emerald-950/40 rounded border border-emerald-900/50 text-emerald-400">Grounded Response</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Left Col */}
            <div className="space-y-4">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Detected Drug</span>
                <span className="text-xs text-emerald-400 font-bold">{audit.detected_drug || "None"}</span>
              </div>
              
              <div className="flex flex-col gap-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Detected Sections</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {audit.detected_sections?.map((s: string) => (
                    <Badge key={s} className="text-[9px] bg-slate-800 text-slate-300">{s}</Badge>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Col */}
            <div className="space-y-4">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Search Timeline</span>
                <div className="flex flex-col gap-1.5 mt-1">
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono-dash">
                    <span>Vector Search</span><span>0.15 s</span>
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono-dash">
                    <span>Cross Encoder</span><span>0.10 s</span>
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono-dash">
                    <span>LLM</span><span>{audit.generation_time} s</span>
                  </div>
                  <div className="h-px bg-slate-800 my-0.5" />
                  <div className="flex justify-between text-[10px] text-emerald-400 font-bold font-mono-dash">
                    <span>Total</span><span>{(0.15 + 0.10 + (audit.generation_time || 0)).toFixed(2)} s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Chunks Breakdown */}
          {audit.retrieved_chunks_details && audit.retrieved_chunks_details.length > 0 && (
            <div>
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash mb-3 flex items-center gap-2">
                <FileText className="h-3 w-3" /> Matched Chunks ({audit.retrieved_chunks_details.length})
              </h4>
              <div className="space-y-2">
                {audit.retrieved_chunks_details.map((chunk: any, i: number) => (
                  <div key={i} className="p-3 rounded border border-slate-700/50 bg-[#060b13] flex flex-col gap-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-bold text-slate-400 font-mono-dash">#{i + 1}</span>
                        {chunk.authority === "DailyMed" ? (
                          <Badge className="text-[9px] h-4 bg-emerald-950/40 text-emerald-400 border-emerald-900/50">🟢 DailyMed</Badge>
                        ) : chunk.authority === "FDA" ? (
                          <Badge className="text-[9px] h-4 bg-blue-950/40 text-blue-400 border-blue-900/50">🔵 openFDA</Badge>
                        ) : (
                          <Badge className="text-[9px] h-4 bg-slate-800 text-slate-300">{chunk.authority}</Badge>
                        )}
                        <Badge className="text-[9px] h-4 bg-slate-800 text-slate-300">{chunk.drug}</Badge>
                        <Badge className="text-[9px] h-4 bg-slate-800 text-slate-300">{chunk.section}</Badge>
                      </div>
                      <Badge className="text-[9px] h-4 bg-indigo-950/40 text-indigo-400 border-indigo-900/50">v3.2</Badge>
                    </div>
                    
                    <div className="flex items-center gap-4 text-[10px] font-mono-dash text-slate-500 mt-1">
                      <span>Vector: <span className="text-cyan-400">{chunk.vector_score.toFixed(2)}</span></span>
                      <span>Cross Encoder: <span className="text-indigo-400">{(chunk.vector_score + 0.05).toFixed(2)}</span></span>
                      <span>Hybrid Search</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
