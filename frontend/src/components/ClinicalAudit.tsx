import { useState } from 'react';
import { ChevronDown, ChevronUp, Database, FileText, Workflow, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface ClinicalAuditProps {
  metadata: any;
}

export function ClinicalAudit({ metadata }: ClinicalAuditProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!metadata) return null;
  const coverage = metadata.clinical_coverage || { sections: {}, overall_percentage: 0 };
  const trace = metadata.retrieval_trace || [];
  const latency = metadata.latency_breakdown || {};
  const provenance = metadata.provenance_block || [];

  return (
    <div className="mt-4 rounded-xl border border-slate-700 bg-[#090e17] overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-slate-800/40 hover:bg-slate-800/60 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-cyan-400" />
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono-dash">Clinical Audit</span>
          </div>
          {metadata.groundedness && (
            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-900/50 px-2 py-0.5 rounded font-mono-dash">
              Groundedness: {metadata.groundedness}
            </span>
          )}
        </div>
        {isOpen ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-slate-700/50 space-y-6">
          
          {/* Groundedness & Coverage Header */}
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1 space-y-3">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-emerald-500" /> Clinical Coverage
              </h4>
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono-dash">
                {Object.entries(coverage.sections).map(([sec, hasData]: any) => (
                  <div key={sec} className="flex items-center gap-2">
                    {hasData ? <span className="text-emerald-400">✔</span> : <span className="text-rose-500">✘</span>}
                    <span className={hasData ? "text-slate-300" : "text-slate-600"}>{sec}</span>
                  </div>
                ))}
              </div>
              <div className="mt-2 text-[10px] font-bold text-slate-400 font-mono-dash border-t border-slate-800 pt-2">
                Completeness: <span className="text-emerald-400">{coverage.overall_percentage}%</span>
              </div>
            </div>

            <div className="flex-1 space-y-3">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash flex items-center gap-2">
                <Workflow className="h-3 w-3 text-indigo-400" /> Latency Breakdown
              </h4>
              <div className="flex flex-col gap-1.5 text-[10px] font-mono-dash">
                <div className="flex justify-between text-slate-400">
                  <span>Alias Resolution</span><span>{latency.alias_resolution_ms || 0} ms</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Qdrant Search</span><span>{latency.vector_search_ms || 0} ms</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Cross Encoder</span><span>{latency.rerank_ms || 0} ms</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>LLM Generation</span><span>{latency.generation_ms || 0} ms</span>
                </div>
                <div className="h-px bg-slate-800 my-0.5" />
                <div className="flex justify-between text-emerald-400 font-bold">
                  <span>Total Response Time</span><span>{metadata.total_latency_sec ? (metadata.total_latency_sec * 1000).toFixed(2) : 0} ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* Retrieval Trace */}
          {trace.length > 0 && (
            <div className="border-t border-slate-800 pt-6">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash mb-3 flex items-center gap-2">
                <Workflow className="h-3 w-3 text-cyan-400" /> Step-by-Step Retrieval Trace
              </h4>
              <div className="space-y-4">
                {trace.map((step: any, idx: number) => (
                  <div key={idx} className="p-3 bg-[#060b13] border border-slate-800 rounded flex flex-col gap-2">
                    <span className="text-[10px] font-bold text-slate-300 capitalize font-mono-dash">{step.drug} - {step.section}</span>
                    <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono-dash">
                      {step.attempts.map((att: any, aIdx: number) => (
                        <div key={aIdx} className="flex items-center gap-2">
                          {aIdx > 0 && <span className="text-slate-600">→</span>}
                          <span className={`px-2 py-1 rounded border ${att.chunks > 0 || att.top_k > 0 ? "bg-slate-800 border-slate-700 text-cyan-400" : "bg-red-950/20 border-red-900/50 text-red-400"}`}>
                            {att.type} ({att.chunks !== undefined ? att.chunks + " chunks" : "Top " + att.top_k})
                          </span>
                        </div>
                      ))}
                      <span className="text-slate-600">→</span>
                      <span className="px-2 py-1 rounded border bg-emerald-950/20 border-emerald-900/50 text-emerald-400">LLM Generation</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Provenance Block */}
          {provenance.length > 0 && (
            <div className="border-t border-slate-800 pt-6">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono-dash mb-3 flex items-center gap-2">
                <FileText className="h-3 w-3 text-amber-400" /> Provenance Evidence ({provenance.length} chunks)
              </h4>
              <div className="grid grid-cols-1 gap-2">
                {provenance.map((prov: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-slate-900/50 border border-slate-800/80 text-[10px] font-mono-dash">
                    <div className="flex items-center gap-3">
                      <Badge className="bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-800">{prov.authority}</Badge>
                      <span className="text-slate-300 font-bold truncate max-w-[150px]">{prov.document}</span>
                    </div>
                    <div className="flex items-center gap-4 text-slate-500">
                      <span>Chunk ID: <span className="text-cyan-500">{prov.chunk_id}</span></span>
                      <span>Doc v{prov.version}</span>
                      <span>Corpus: {prov.corpus}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-2 text-[10px] font-mono-dash text-slate-500">
                {metadata.groundedness_details}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
