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
        className="inline-flex items-center justify-center text-[10px] font-bold text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded h-4 min-w-[16px] px-1 ml-0.5 cursor-pointer align-baseline relative -top-1 transition-all duration-200"
      >
        [{num}]
      </HoverCardTrigger>
      <HoverCardContent className="w-80 border border-slate-200 shadow-xl bg-white p-4 rounded-xl z-50 text-left">
        <div className="space-y-3 font-sans">
          <div className="flex items-center justify-between border-b pb-1.5 border-slate-100">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
              {citation.source}
            </span>
            {citation.similarity !== undefined && (
              <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                Similarity {similarityPercent}
              </span>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Drug</span>
              <span className="font-semibold text-slate-800">{citation.drug || "N/A"}</span>
            </div>
            <div>
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Section</span>
              <span className="font-semibold text-slate-800 line-clamp-1">{citation.section || "N/A"}</span>
            </div>
          </div>
          
          <div className="border-t pt-2 border-slate-100">
            <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 block mb-1">Snippet</span>
            <p className="text-xs text-slate-600 italic bg-slate-50 p-2.5 rounded border border-slate-100 leading-normal max-h-40 overflow-y-auto shadow-inner">
              "{citation.snippet}"
            </p>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
}
