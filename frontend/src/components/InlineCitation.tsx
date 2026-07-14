import * as React from "react";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "./ui/hover-card";

export interface CitationType {
  citation_number?: number;
  document_id: string;
  uuid?: string;
  drug?: string;
  section?: string;
  source: string;
  snippet: string;
  similarity?: number;
}

interface InlineCitationProps {
  citation: CitationType;
  onClick: (e: React.MouseEvent) => void;
}

export function InlineCitation({ citation, onClick }: InlineCitationProps) {
  const similarityPercent = citation.similarity !== undefined
    ? `${Math.round(citation.similarity * 100)}%`
    : "N/A";

  const num = citation.citation_number ?? parseInt(citation.document_id, 10);

  return (
    <HoverCard openDelay={150}>
      <HoverCardTrigger 
        onClick={onClick}
        className="inline-flex items-center justify-center text-[10px] font-bold text-cyan-400 hover:text-cyan-200 bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyan-800/80 rounded h-4 min-w-[16px] px-1 ml-0.5 cursor-pointer align-baseline relative -top-1 transition-all duration-200"
      >
        [{num}]
      </HoverCardTrigger>
      <HoverCardContent className="w-80 border border-slate-800 shadow-2xl bg-[#0b1320] p-4 rounded-xl z-50 text-left text-slate-200">
        <div className="space-y-3 font-sans">
          <div className="flex items-center justify-between border-b pb-1.5 border-slate-800/60">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
              {citation.source}
            </span>
            {citation.similarity !== undefined && (
              <span className="text-[10px] font-semibold bg-[#121b28] text-slate-400 px-1.5 py-0.5 rounded border border-slate-800">
                Match {similarityPercent}
              </span>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-0.5">Drug</span>
              <span className="font-semibold text-slate-300">{citation.drug || "N/A"}</span>
            </div>
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-0.5">Section</span>
              <span className="font-semibold text-slate-300 line-clamp-1">{citation.section || "N/A"}</span>
            </div>
          </div>
          
          <div className="border-t pt-2 border-slate-800/60">
            <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-1">Snippet</span>
            <p className="text-xs text-slate-400 italic bg-[#060b13] p-2.5 rounded border border-slate-800/80 leading-normal max-h-40 overflow-y-auto shadow-inner">
              "{citation.snippet}"
            </p>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
}
