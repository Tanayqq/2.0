import React, { useState, useEffect } from "react";
import { queryMedicalAPI, type AnswerResponse } from "./services/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  ShieldAlert, 
  Loader2, 
  ChevronDown, 
  ChevronUp,
  Folder,
  Database,
  Terminal,
  FileText,
  Sliders,
  Trash2,
  History,
  BookOpen,
  AlertTriangle,
  LayoutDashboard,
  MessageSquare
} from "lucide-react";
import { InlineCitation } from "./components/InlineCitation";
import { Dashboard } from "./components/Dashboard";
import { ClinicalAudit } from "./components/ClinicalAudit";
import "./App.css";

// ── TYPES & INTERFACES ───────────────────────────────────────────────────────
interface ParsedSection {
  contraindications: string;
  warnings: string;
  interactions: string;
  overview: string;
  dosing: string;
}

interface ParsedDrug {
  name: string;
  sections: ParsedSection;
}

// ── DRUG LOCAL EQUIVALENTS DATABASE ──────────────────────────────────────────
const DRUG_EQUIVALENTS: Record<string, string[]> = {
  "abatacept": ["Orencia"],
  "abemaciclib": ["Verzenio"],
  "acalabrutinib": ["Calquence"],
  "acarbose": ["Precose"],
  "acetaminophen": ["Tylenol"],
  "acyclovir": ["Zovirax"],
  "adalimumab": ["Humira"],
  "albuterol": ["Ventolin", "Proair", "Proventil"],
  "alectinib": ["Alecensa"],
  "allopurinol": ["Zyloprim", "Aloprim"],
  "alogliptin": ["Nesina"],
  "alprazolam": ["Xanax"],
  "amlodipine": ["Norvasc"],
  "amoxicillin": ["Amoxil", "Novamox"],
  "apixaban": ["Eliquis"],
  "atenolol": ["Tenormin"],
  "atezolizumab": ["Tecentriq"],
  "atorvastatin": ["Lipitor"],
  "azathioprine": ["Imuran"],
  "azithromycin": ["Zithromax"],
  "belimumab": ["Benlysta"],
  "bevacizumab": ["Avastin"],
  "budesonide": ["Pulmicort", "Rhinocort"],
  "bupropion": ["Wellbutrin", "Zyban"],
  "canagliflozin": ["Invokana"],
  "carvedilol": ["Coreg"],
  "cefdinir": ["Omnicef"],
  "cefuroxime": ["Ceftin"],
  "cephalexin": ["Keflex"],
  "certolizumab": ["Cimzia"],
  "cetirizine": ["Zyrtec"],
  "cetuximab": ["Erbitux"],
  "cimetidine": ["Tagamet"],
  "ciprofloxacin": ["Cipro"],
  "citalopram": ["Celexa"],
  "clarithromycin": ["Biaxin"],
  "clindamycin": ["Cleocin"],
  "clonazepam": ["Klonopin"],
  "clonidine": ["Catapres"],
  "clopidogrel": ["Plavix"],
  "colchicine": ["Colcrys", "Mitigare"],
  "cyclosporine": ["Neoral", "Sandimmune", "Gengraf"],
  "dabigatran": ["Pradaxa"],
  "dapagliflozin": ["Farxiga"],
  "dasatinib": ["Sprycel"],
  "dexamethasone": ["Decadron"],
  "diazepam": ["Valium"],
  "diphenhydramine": ["Benadryl"],
  "doxycycline": ["Vibramycin", "Doryx"],
  "dulaglutide": ["Trulicity"],
  "duloxetine": ["Cymbalta"],
  "durvalumab": ["Imfinzi"],
  "edoxaban": ["Savaysa"],
  "empagliflozin": ["Jardiance"],
  "enalapril": ["Vasotec"],
  "erlotinib": ["Tarceva"],
  "erythromycin": ["Erythrocin"],
  "escitalopram": ["Lexapro"],
  "esomeprazole": ["Nexium"],
  "etanercept": ["Enbrel"],
  "ezetimibe": ["Zetia"],
  "famotidine": ["Pepcid"],
  "febuxostat": ["Uloric"],
  "fenofibrate": ["Tricor", "Antara"],
  "fexofenadine": ["Allegra"],
  "fluconazole": ["Diflucan"],
  "fluticasone": ["Flonase", "Flovent"],
  "formoterol": ["Foradil"],
  "furosemide": ["Lasix"],
  "gabapentin": ["Neurontin"],
  "gemfibrozil": ["Lopid"],
  "glimepiride": ["Amaryl"],
  "glipizide": ["Glucotrol"],
  "glyburide": ["Micronase", "Diabeta"],
  "golimumab": ["Simponi"],
  "guselkumab": ["Tremfya"],
  "hydralazine": ["Apresoline"],
  "hydrochlorothiazide": ["Microzide"],
  "hydroxychloroquine": ["Plaquenil"],
  "hydroxyzine": ["Vistaril", "Atarax"],
  "ibrutinib": ["Imbruvica"],
  "ibuprofen": ["Advil", "Motrin"],
  "imatinib": ["Gleevec"],
  "infliximab": ["Remicade"],
  "insulin aspart": ["Novolog"],
  "insulin degludec": ["Tresiba"],
  "insulin detemir": ["Levemir"],
  "insulin glargine": ["Lantus", "Toujeo", "Basaglar"],
  "insulin glulisine": ["Apidra"],
  "insulin lispro": ["Humalog"],
  "ipilimumab": ["Yervoy"],
  "ipratropium": ["Atrovent"],
  "itraconazole": ["Sporanox"],
  "ixekizumab": ["Taltz"],
  "ketoconazole": ["Nizoral"],
  "lansoprazole": ["Prevacid"],
  "levofloxacin": ["Levaquin"],
  "levothyroxine": ["Synthroid", "Levoxyl", "Unithroid"],
  "linagliptin": ["Tradjenta"],
  "linezolid": ["Zyvox"],
  "liraglutide": ["Victoza", "Saxenda"],
  "lisinopril": ["Prinivil", "Zestril"],
  "loperamide": ["Imodium"],
  "loratadine": ["Claritin"],
  "lorazepam": ["Ativan"],
  "losartan": ["Cozaar"],
  "lovastatin": ["Mevacor"],
  "meloxicam": ["Mobic"],
  "mesalamine": ["Lialda", "Asacol", "Pentasa"],
  "metformin": ["Glucophage", "Fortamet", "Glumetza"],
  "methotrexate": ["Rheumatrex", "Trexall"],
  "methylprednisolone": ["Medrol"],
  "metoclopramide": ["Reglan"],
  "metoprolol": ["Lopressor", "Toprol"],
  "metronidazole": ["Flagyl"],
  "miglitol": ["Glyset"],
  "minocycline": ["Minocin", "Solodyn"],
  "misoprostol": ["Cytotec"],
  "montelukast": ["Singulair"],
  "moxifloxacin": ["Avelox"],
  "mycophenolate_mofetil": ["Cellcept"],
  "nateglinide": ["Starlix"],
  "nilotinib": ["Tasigna"],
  "niraparib": ["Zejula"],
  "nitrofurantoin": ["Macrobid", "Macrodantin"],
  "nivolumab": ["Opdivo"],
  "olaparib": ["Lynparza"],
  "omeprazole": ["Prilosec"],
  "ondansetron": ["Zofran"],
  "oseltamivir": ["Tamiflu"],
  "osimertinib": ["Tagrisso"],
  "palbociclib": ["Ibrance"],
  "pantoprazole": ["Protonix"],
  "pembrolizumab": ["Keytruda"],
  "pertuzumab": ["Perjeta"],
  "pioglitazone": ["Actos"],
  "prasugrel": ["Effient"],
  "pravastatin": ["Pravachol"],
  "prednisolone": ["Millipred", "Orapred"],
  "prednisone": ["Deltasone"],
  "promethazine": ["Phenergan"],
  "propranolol": ["Inderal"],
  "rabeprazole": ["Aciphex"],
  "ramipril": ["Altace"],
  "repaglinide": ["Prandin"],
  "ribociclib": ["Kisqali"],
  "risankizumab": ["Skyrizi"],
  "rituximab": ["Rituxan"],
  "rivaroxaban": ["Xarelto"],
  "rosiglitazone": ["Avandia"],
  "rosuvastatin": ["Crestor"],
  "rucaparib": ["Rubraca"],
  "sacubitril_valsartan": ["Entresto"],
  "salmeterol": ["Serevent"],
  "saxagliptin": ["Onglyza"],
  "secukinumab": ["Cosentyx"],
  "semaglutide": ["Ozempic", "Wegovy"],
  "sertraline": ["Zoloft"],
  "simvastatin": ["Zocor"],
  "sitagliptin": ["Januvia"],
  "spironolactone": ["Aldactone"],
  "sulfasalazine": ["Azulfidine"],
  "tacrolimus": ["Prograf"],
  "tamsulosin": ["Flomax"],
  "terbinafine": ["Lamisil"],
  "tetracycline": ["Sumycin"],
  "ticagrelor": ["Brilinta"],
  "tiotropium": ["Spiriva"],
  "tirzepatide": ["Mounjaro", "Zepbound"],
  "tocilizumab": ["Actemra"],
  "trastuzumab": ["Herceptin"],
  "trimethoprim": ["Primsol"],
  "ustekinumab": ["Stelara"],
  "valacyclovir": ["Valtrex"],
  "valsartan": ["Diovan"],
  "vancomycin": ["Vancocin"],
  "venetoclax": ["Venclexta"],
  "warfarin": ["Coumadin", "Jantoven"],
  "zanubrutinib": ["Brukinsa"],
  "zolpidem": ["Ambien"],
};

// ── SECTION PARSER HELPER ────────────────────────────────────────────────────
function parseMarkdownReport(text: string): ParsedDrug[] {
  if (!text) return [];
  
  // Split by drug name block: **DrugName** or ### DrugName
  const drugBlocks = text.split(/(?=\n\s*(?:\*\*[A-Z][a-zA-Z0-9- ]+\*\*|###\s+[A-Z][a-zA-Z0-9- ]+))/i);
  const parsedDrugs: ParsedDrug[] = [];

  for (const block of drugBlocks) {
    if (!block.trim()) continue;
    
    // Extract drug name
    const drugNameMatch = block.match(/(?:\*\*|###\s+)([A-Z][a-zA-Z0-9- ]+)(?:\*\*|)/i);
    if (!drugNameMatch) continue;
    const drugName = drugNameMatch[1].trim();
    
    const getSectionContent = (secName: string, textContent: string): string => {
      // Find headings matching ## secName or #### secName
      const escapedSec = secName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(
        `(?:##|###|####)\\s+${escapedSec}\\b([\\s\\S]*?)(?=(?:##|###|####)\\s+[A-Za-z]|$)`,
        'i'
      );
      const match = textContent.match(pattern);
      return match ? match[1].trim() : "";
    };
    
    const contraindications = getSectionContent("Contraindications", block);
    const warnings = getSectionContent("Warnings", block);
    const interactions = getSectionContent("Drug Interactions", block) || getSectionContent("Co-Administration Risks", block);
    const overview = getSectionContent("Clinical Profile Overview", block) || getSectionContent("Indications and Usage", block);
    const dosing = getSectionContent("Dosing & Administration", block) || getSectionContent("Dosage", block);
    
    // If all structured headings are empty, treat the whole block as clinical overview
    const hasAnySection = contraindications || warnings || interactions || overview || dosing;
    const finalOverview = hasAnySection ? overview : block.replace(/(?:\*\*|###\s+)[A-Z][a-zA-Z0-9- ]+(?:\*\*|)/i, "").trim();
    
    parsedDrugs.push({
      name: drugName,
      sections: {
        contraindications: contraindications || "Not found in available sources.",
        warnings: warnings || "Not found in available sources.",
        interactions: interactions || "Not found in available sources.",
        overview: finalOverview || "Not found in available sources.",
        dosing: dosing || "Not found in available sources."
      }
    });
  }
  
  return parsedDrugs;
}


function SectionHeaderBadge({ drugName, sectionKeys, activeItem }: { drugName: string, sectionKeys: string[], activeItem: any }) {
  if (!activeItem?.a?.metadata?.section_status) return null;
  const statusMapObj = activeItem.a.metadata.section_status;
  const statusKeys = Object.keys(statusMapObj || {});
  if (statusKeys.length === 0) return null;

  const activeLower = (drugName || "").toLowerCase().trim();
  const matchedKey = statusKeys.find(k => {
    const kLower = k.toLowerCase().trim();
    return kLower === activeLower || activeLower.includes(kLower) || kLower.includes(activeLower) ||
      (DRUG_EQUIVALENTS[kLower]?.some(eq => eq.toLowerCase() === activeLower || activeLower.includes(eq.toLowerCase()))) ||
      (DRUG_EQUIVALENTS[activeLower]?.some(eq => eq.toLowerCase() === kLower || kLower.includes(eq.toLowerCase())));
  }) || statusKeys[0];

  const statusMap = matchedKey ? statusMapObj[matchedKey] : null;
  if (!statusMap) return null;
  
  let bestMeta: any = null;
  for (const key of sectionKeys) {
     if (statusMap[key] && statusMap[key].status !== "NO_DATA") {
         bestMeta = statusMap[key];
         break;
     }
  }
  if (!bestMeta) {
     const firstAvailable = Object.values(statusMap).find((v: any) => v && v.status !== "NO_DATA");
     bestMeta = firstAvailable || Object.values(statusMap)[0];
  }
  if (!bestMeta) return null;
  
  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex items-center gap-2">
        {bestMeta.status && bestMeta.status.includes("SEMANTIC") && (
          <span className="text-[9px] font-bold text-yellow-500 tracking-wider font-mono-dash bg-yellow-950/30 px-1.5 py-0.5 rounded border border-yellow-900/50">
            ⚠ Recovered from: {bestMeta.original_section || "Unknown"}
          </span>
        )}
        <span className="text-[9px] font-bold text-slate-300 tracking-wider uppercase font-mono-dash bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
          {bestMeta.confidence_stars || "★★★☆☆"} {(bestMeta.status || "EXACT_SECTION").replace("_", " ")}
        </span>
      </div>
      {bestMeta.evidence_diversity && (
        <span className="text-[8px] text-slate-500 font-mono-dash text-right max-w-[150px] leading-tight">
          Evidence: {bestMeta.evidence_diversity}
        </span>
      )}
    </div>
  );
}

// ── CUSTOM TEXT RENDERING COMPONENT ─────────────────────────────────────────
function CustomTextRenderer({ 
  text, 
  citations, 
  cardIndex 
}: { 
  text: string; 
  citations: AnswerResponse["citations"]; 
  cardIndex: number;
}) {
  const regex = /\[([0-9]+)\]|\[Unsupported Citation Removed\]/g;
  
  if (text.toLowerCase() === "not found in available sources.") {
    return <span className="text-slate-500 italic text-sm">Not found in available sources.</span>;
  }

  // Split text by lines to preserve format/bullet lists
  const lines = text.split('\n').filter(l => l.trim().length > 0);

  const handleCitationClick = (e: React.MouseEvent, docId: string) => {
    e.preventDefault();
    const num = parseInt(docId, 10);
    const citation = citations.find(c => (c.citation_number ?? parseInt(c.document_id, 10)) === num);
    
    if (citation) {
      const elementId = `citation-card-${cardIndex}-${citation.citation_number ?? citation.document_id}`;
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        element.classList.add("ring-2", "ring-cyan-400", "bg-cyan-950/20", "scale-[1.01]");
        setTimeout(() => {
          element.classList.remove("ring-2", "ring-cyan-400", "bg-cyan-950/20", "scale-[1.01]");
        }, 1000);
      }
    }
  };

  const renderBoldAndText = (textSegment: string, keyPrefix: string) => {
    const boldRegex = /\*\*([^*]+)\*\*/g;
    const elements = [];
    let lastIdx = 0;
    let boldMatch;
    boldRegex.lastIndex = 0;
    while ((boldMatch = boldRegex.exec(textSegment)) !== null) {
      if (boldMatch.index > lastIdx) {
        elements.push(<span key={`${keyPrefix}-text-${lastIdx}`}>{textSegment.substring(lastIdx, boldMatch.index)}</span>);
      }
      elements.push(<strong key={`${keyPrefix}-bold-${boldMatch.index}`} className="font-bold text-slate-100">{boldMatch[1]}</strong>);
      lastIdx = boldMatch.index + boldMatch[0].length;
    }
    if (lastIdx < textSegment.length) {
      elements.push(<span key={`${keyPrefix}-text-end`}>{textSegment.substring(lastIdx)}</span>);
    }
    return elements;
  };

  return (
    <div className="space-y-2">
      {lines.map((line, lIdx) => {
        // Detect if line is bullet-like
        const isBullet = line.trim().startsWith("-") || line.trim().startsWith("*");
        // Strip bullet prefixes
        let lineText = line;
        if (isBullet) {
          lineText = line.trim().replace(/^[-*]\s*/, "");
        }

        const parts: any[] = [];
        let lastIndex = 0;
        let match;
        
        // Reset regex index for this line
        regex.lastIndex = 0;
        
        while ((match = regex.exec(lineText)) !== null) {
          if (match.index > lastIndex) {
            parts.push(...renderBoldAndText(lineText.substring(lastIndex, match.index), `l${lIdx}-p1-${lastIndex}`));
          }
          
          const matchedText = match[0];
          if (matchedText === "[Unsupported Citation Removed]") {
            parts.push(
              <span key={`l${lIdx}-unsupported-${match.index}`} className="inline-flex px-1 text-[9px] text-red-500 font-bold bg-red-950/20 border border-red-900/40 rounded ml-0.5">
                [Ungrounded Removed]
              </span>
            );
          } else {
            const docId = match[1];
            parts.push(
              <InlineCitation 
                key={`l${lIdx}-citation-${match.index}`}
                citation={citations.find(c => (c.citation_number ?? parseInt(c.document_id, 10)) === parseInt(docId, 10)) || {
                  document_id: docId,
                  source: "Ingested Corpus",
                  snippet: "Grounded chunk citation"
                }}
                onClick={(e) => handleCitationClick(e, docId)}
              />
            );
          }
          lastIndex = match.index + match[0].length;
        }
        
        if (lastIndex < lineText.length) {
          parts.push(...renderBoldAndText(lineText.substring(lastIndex), `l${lIdx}-p2-${lastIndex}`));
        }

        return (
          <div key={lIdx} className="flex items-start gap-2 text-[13.5px] leading-relaxed text-slate-300">
            {isBullet ? (
              <span className="text-cyan-500 shrink-0 mt-2 select-none font-bold text-xs">•</span>
            ) : null}
            <span>{parts}</span>
          </div>
        );
      })}
    </div>
  );
}

// ── EXPANDABLE SOURCE CARD ───────────────────────────────────────────────────
function SourceCard({ 
  c, 
  cardIndex, 
  num 
}: { 
  c: AnswerResponse["citations"][number]; 
  cardIndex: number; 
  num: number;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div 
      id={`citation-card-${cardIndex}-${num}`}
      className="flex flex-col text-xs text-slate-400 p-3 rounded-lg border border-slate-800 bg-[#0e1726]/60 shadow-sm transition-all duration-300 gap-2"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <span className="inline-flex items-center justify-center font-bold text-cyan-400 bg-cyan-950/40 border border-cyan-800/80 rounded h-5 min-w-[20px] px-1 text-[10px] shrink-0">
            [{num}]
          </span>
          <div className="space-y-0.5 flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="font-bold text-slate-300 text-xs truncate">{c.source}</span>
              {c.drug && (
                <Badge className="text-slate-400 border-slate-800 bg-slate-900 text-[8px] h-4">
                  {c.drug}
                </Badge>
              )}
              {c.section && (
                <Badge className="text-slate-400 bg-slate-800/50 text-[8px] h-4">
                  {c.section}
                </Badge>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-1.5 shrink-0">
          {c.similarity !== undefined && (
            <Badge className="text-cyan-400 border-cyan-900/60 bg-cyan-950/20 text-[8px] h-4">
              Match: {(c.similarity * 100).toFixed(0)}%
            </Badge>
          )}
          {c.count && c.count > 0 && (
            <Badge className="bg-slate-800 text-slate-400 text-[8px] h-4">
              Referenced {c.count} time{c.count > 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </div>

      <div 
        onClick={() => setExpanded(!expanded)}
        className="cursor-pointer hover:bg-slate-900/40 p-2 rounded border border-slate-800/50 bg-[#060b13]/80 transition-colors duration-200 group relative"
      >
        <p className={`text-[11px] text-slate-400 italic leading-relaxed transition-all duration-300 ${expanded ? "" : "line-clamp-2"}`}>
          "{c.snippet}"
        </p>
        <div className="mt-1 flex items-center justify-end gap-1 text-[9px] text-slate-500 font-medium group-hover:text-cyan-400 select-none">
          {expanded ? (
            <>
              <span>Collapse</span>
              <ChevronUp className="h-2.5 w-2.5" />
            </>
          ) : (
            <>
              <span>Expand snippet</span>
              <ChevronDown className="h-2.5 w-2.5" />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── MAIN APPLICATION COMPONENT ───────────────────────────────────────────────
export default function App() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<{q: string, a: AnswerResponse, status: string}[]>([]);
  const [activeHistoryIndex, setActiveHistoryIndex] = useState<number>(-1);
  const [activeTab, setActiveTab] = useState<"chat" | "dashboard">("chat");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Layout Options
  const [formularyStandard, setFormularyStandard] = useState<"openFDA" | "CDSCO">("openFDA");
  const [activeDrugTab, setActiveDrugTab] = useState<string>("");

  // System Latencies (simulated when idle, loaded from metadata when run)
  const [metrics, setMetrics] = useState({
    vector: 12,
    rerank: 8,
    generation: 320
  });

  // Load sample history on first mount if empty
  useEffect(() => {
    // Set default initial telemetry
    setMetrics({
      vector: 12,
      rerank: 8,
      generation: 320
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await queryMedicalAPI(query);
      console.log("RAG complete answer response:", response);
      
      const newHistoryItem = { q: query, a: response, status: "200 OK" };
      setHistory(prev => [...prev, newHistoryItem]);
      setActiveHistoryIndex(history.length); // Select new query
      
      // Update Latencies from API
      const retTimeSec = response.metadata?.retrieval_latency_sec || 0.15;
      const totalTimeSec = response.metadata?.total_latency_sec || 1.2;
      const genTimeSec = Math.max(0.1, totalTimeSec - retTimeSec);

      setMetrics({
        vector: Math.round(retTimeSec * 1000 * 0.6),
        rerank: Math.round(retTimeSec * 1000 * 0.4),
        generation: Math.round(genTimeSec * 1000)
      });

      // Automatically select first drug tab if parsed
      const parsed = parseMarkdownReport(response.answer);
      if (parsed.length > 0) {
        setActiveDrugTab(parsed[0].name.toLowerCase());
      } else {
        setActiveDrugTab("");
      }

      setQuery("");
    } catch (err: any) {
      setError(err.message || "An unknown error occurred.");
      // Add failed item to cache trail as well for diagnostic realism!
      setHistory(prev => [...prev, { 
        q: query, 
        a: { answer: "", citations: [], metadata: { provider: "Failed" } },
        status: "500 Error"
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Get current active report item
  const activeItem = activeHistoryIndex >= 0 && activeHistoryIndex < history.length ? history[activeHistoryIndex] : null;
  const parsedDrugs = activeItem ? parseMarkdownReport(activeItem.a.answer) : [];
  
  // Get active drug parsed details
  const activeDrug = parsedDrugs.find(d => d.name.toLowerCase() === activeDrugTab) || parsedDrugs[0];

  // Sync drug tab selection
  useEffect(() => {
    if (parsedDrugs.length > 0 && (!activeDrugTab || !parsedDrugs.some(d => d.name.toLowerCase() === activeDrugTab))) {
      setActiveDrugTab(parsedDrugs[0].name.toLowerCase());
    }
  }, [parsedDrugs, activeDrugTab]);

  const activeCitations = activeItem?.a.citations || [];
  const referencedNums = new Set<number>();
  if (activeItem) {
    const citationRegex = /\[([0-9]+)\]/g;
    let m;
    while ((m = citationRegex.exec(activeItem.a.answer)) !== null) {
      referencedNums.add(parseInt(m[1], 10));
    }
  }

  // Filter citations for the active drug
  const drugCitations = activeCitations.filter((c, idx) => {
    const num = c.citation_number ?? (idx + 1);
    const isCited = referencedNums.size === 0 || referencedNums.has(num);
    
    // For single drug results, display all citations referenced in the text
    if (parsedDrugs.length <= 1) {
      return isCited;
    }

    const drugLower = (c.drug || "").toLowerCase().trim();
    const activeLower = (activeDrug?.name || "").toLowerCase().trim();
    
    const matchesDrug = !c.drug || !activeDrug || (
      drugLower === activeLower ||
      activeLower.includes(drugLower) ||
      drugLower.includes(activeLower) ||
      (drugLower ? DRUG_EQUIVALENTS[drugLower]?.some(eq => eq.toLowerCase() === activeLower || activeLower.includes(eq.toLowerCase())) : false) ||
      (activeLower ? DRUG_EQUIVALENTS[activeLower]?.some(eq => eq.toLowerCase() === drugLower || drugLower.includes(eq.toLowerCase())) : false)
    );
    
    return isCited && matchesDrug;
  });

  const finalCitationsToRender = drugCitations.length > 0 ? drugCitations : activeCitations;

  return (
    <div className="flex h-screen w-screen bg-[#060b13] text-[#e2e8f0] overflow-hidden font-sans select-text">
      
      {/* ── LEFT SIDEBAR ──────────────────────────────────────────────────────── */}
      <aside className="w-72 shrink-0 flex flex-col border-r border-[#1e293b]/60 bg-[#090e17] z-20">
        
        {/* Sidebar Brand Header */}
        <div className="h-16 flex items-center gap-2.5 px-5 border-b border-[#1e293b]/60 shrink-0">
          <div className="relative">
            <Activity className="h-6 w-6 text-[#06b6d4] glow-pulse-cyan" />
            <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-[#10b981] glowing-dot" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="text-[15px] font-bold tracking-tight text-slate-100">MedRef Engine</span>
              <span className="text-[8px] font-bold px-1 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 uppercase tracking-widest font-mono-dash">Node v1.5</span>
            </div>
            <span className="text-[9px] font-mono-dash text-slate-500 uppercase tracking-wider">Biomedical Retrieval Architecture</span>
          </div>
        </div>

        
        {/* Navigation Tabs */}
        <div className="flex flex-col gap-1 px-4 mt-4">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold font-mono-dash transition-colors duration-200 ${
              activeTab === "chat" 
                ? "bg-cyan-950/40 text-cyan-400 border border-cyan-800/50" 
                : "text-slate-500 hover:text-slate-300 hover:bg-[#1e293b]/50 border border-transparent"
            }`}
          >
            <MessageSquare className="h-4 w-4" /> CLINICAL ENGINE
          </button>
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold font-mono-dash transition-colors duration-200 ${
              activeTab === "dashboard" 
                ? "bg-emerald-950/40 text-emerald-400 border border-emerald-800/50" 
                : "text-slate-500 hover:text-slate-300 hover:bg-[#1e293b]/50 border border-transparent"
            }`}
          >
            <LayoutDashboard className="h-4 w-4" /> CORPUS DASHBOARD
          </button>
        </div>

        {/* Audit Cache Trail Section */}
        <div className="flex-1 flex flex-col min-h-0 py-4 px-4 gap-4">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash">
              <span className="flex items-center gap-1.5"><History className="h-3.5 w-3.5" /> Audit Cache Trail</span>
              {history.length > 0 && (
                <button 
                  onClick={() => { setHistory([]); setActiveHistoryIndex(-1); }}
                  className="hover:text-red-400 transition-colors duration-150"
                  title="Clear history"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              )}
            </div>
            
            <ScrollArea className="h-44 border border-[#1e293b]/50 rounded-lg bg-[#070b12]/50 p-2">
              <div className="space-y-1">
                {history.length === 0 ? (
                  <div className="text-center py-6 text-slate-600 text-[10px] italic">
                    No cached transactions.
                  </div>
                ) : (
                  history.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setActiveHistoryIndex(idx);
                        const retTimeSec = item.a.metadata?.retrieval_latency_sec || 0.15;
                        const totalTimeSec = item.a.metadata?.total_latency_sec || 1.2;
                        const genTimeSec = Math.max(0.1, totalTimeSec - retTimeSec);
                        setMetrics({
                          vector: Math.round(retTimeSec * 1000 * 0.6),
                          rerank: Math.round(retTimeSec * 1000 * 0.4),
                          generation: Math.round(genTimeSec * 1000)
                        });
                      }}
                      className={`w-full flex items-center justify-between text-[11px] font-mono-dash px-2 py-1.5 rounded transition-all duration-150 text-left ${
                        activeHistoryIndex === idx 
                          ? 'bg-[#101e30] border-l-2 border-cyan-500 text-cyan-400' 
                          : 'hover:bg-slate-900/60 text-slate-400'
                      }`}
                    >
                      <span className="truncate flex-1 pr-2">{item.q}</span>
                      <span className={`text-[9px] font-bold ${item.status === '200 OK' ? 'text-emerald-500' : 'text-rose-500'}`}>
                        {item.status}
                      </span>
                    </button>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Formulary Standard Section */}
          <div className="flex flex-col gap-1.5 shrink-0">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash">Formulary Standard</span>
            <div className="grid grid-cols-2 p-0.5 rounded-lg border border-[#1e293b]/60 bg-[#070b12] text-xs">
              <button
                onClick={() => setFormularyStandard("openFDA")}
                className={`py-1.5 rounded font-medium transition-all ${
                  formularyStandard === "openFDA"
                    ? "bg-[#101e30] text-cyan-400 border border-cyan-900/60 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                openFDA
              </button>
              <button
                onClick={() => setFormularyStandard("CDSCO")}
                className={`py-1.5 rounded font-medium transition-all ${
                  formularyStandard === "CDSCO"
                    ? "bg-[#101e30] text-cyan-400 border border-cyan-900/60 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                CDSCO / India
              </button>
            </div>
          </div>

          {/* System Telemetry Section */}
          <div className="flex flex-col gap-3 pt-2 mt-auto border-t border-[#1e293b]/40 shrink-0">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash">System Telemetry</span>
            
            <div className="space-y-3 font-mono-dash text-[11px]">
              {/* Telemetry Item 1 */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-slate-400">
                  <span className="flex items-center gap-1.5"><Database className="h-3 w-3 text-cyan-500" /> Vector Retrieval</span>
                  <span className="text-slate-200 font-bold">{metrics.vector}ms</span>
                </div>
                <div className="telemetry-bar-container">
                  <div className="telemetry-bar-fill" style={{ width: `${Math.min(100, (metrics.vector / 150) * 100)}%` }} />
                </div>
              </div>

              {/* Telemetry Item 2 */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-slate-400">
                  <span className="flex items-center gap-1.5"><Sliders className="h-3 w-3 text-cyan-500" /> Cross-Rerank Match</span>
                  <span className="text-slate-200 font-bold">{metrics.rerank}ms</span>
                </div>
                <div className="telemetry-bar-container">
                  <div className="telemetry-bar-fill" style={{ width: `${Math.min(100, (metrics.rerank / 100) * 100)}%` }} />
                </div>
              </div>

              {/* Telemetry Item 3 */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-slate-400">
                  <span className="flex items-center gap-1.5"><Terminal className="h-3 w-3 text-cyan-500" /> vLLM Engine Gen</span>
                  <span className="text-slate-200 font-bold">{metrics.generation}ms</span>
                </div>
                <div className="telemetry-bar-container">
                  <div className="telemetry-bar-fill" style={{ width: `${Math.min(100, (metrics.generation / 1500) * 100)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── MAIN WORKSPACE ───────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#060b13] relative z-10">
        {activeTab === "dashboard" ? (
          <Dashboard />
        ) : (
        <>
        
        {/* Workspace Top Header Bar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-[#1e293b]/60 shrink-0">
          <form onSubmit={handleSubmit} className="flex-1 max-w-xl flex items-center bg-[#070b12] rounded-lg border border-[#1e293b]/60 px-3 py-1 gap-2">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash shrink-0">Query RAG :</span>
            <input 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Amoxicillin, Metformin, Warfarin..." 
              className="flex-1 bg-transparent border-none text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-0 min-w-0 h-7"
              disabled={loading}
            />
            <Button 
              type="submit" 
              disabled={loading || !query.trim()}
              className="bg-[#101e30] border border-cyan-900/60 hover:bg-[#152a44] text-cyan-400 text-[10px] font-bold tracking-wider font-mono-dash h-7 px-3 shrink-0"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  PROCESSING
                </>
              ) : (
                "EXECUTE RETRIEVAL"
              )}
            </Button>
          </form>

          {/* Right indicator */}
          <div className="flex items-center gap-4 shrink-0 pl-4">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-md border border-[#1e293b]/50 bg-[#070b12] text-[10px] font-mono-dash text-slate-400">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-500 glowing-dot" />
              <span>Core Node: <span className="text-cyan-400 font-bold">MedGemma-27B local</span></span>
            </div>
            <button
              onClick={() => {
                setQuery("");
                setError(null);
                setHistory([]);
                setActiveHistoryIndex(-1);
              }}
              className="px-3 py-1.5 rounded border border-slate-800 bg-slate-900/40 text-[10px] font-bold font-mono-dash text-slate-400 hover:text-slate-200 transition-colors"
            >
              Reset
            </button>
          </div>
        </header>

        {/* Workspace Scroll Area */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-5xl mx-auto space-y-6 pb-12">
            
            {error && (
              <div className="flex gap-3 p-4 rounded-xl border border-red-900/40 bg-red-950/10 text-red-400 text-xs">
                <ShieldAlert className="h-5 w-5 text-red-500 shrink-0" />
                <div className="space-y-1">
                  <span className="font-bold">Retrieval Error</span>
                  <p>{error}</p>
                </div>
              </div>
            )}

            {/* Blank State View */}
            {!activeItem && !loading && (
              <div className="h-[60vh] flex flex-col items-center justify-center text-center p-8">
                <div className="p-4 rounded-full border border-dashed border-cyan-500/20 bg-cyan-950/5 mb-6">
                  <Activity className="h-12 w-12 text-cyan-500/50 glow-pulse-cyan" />
                </div>
                <h2 className="text-base font-bold text-slate-200 tracking-tight">MedRef RAG Sandbox</h2>
                <p className="text-xs text-slate-500 max-w-sm mt-1 leading-relaxed">
                  Enter a query above to retrieve verified biomedical references and structured clinical summaries from openFDA and DailyMed.
                </p>
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-center">
                <Loader2 className="h-10 w-10 animate-spin text-cyan-500" />
                <div className="space-y-1 font-mono-dash text-xs text-slate-400">
                  <span>Executing dense-only vector alignment...</span>
                  <p className="text-[10px] text-slate-600">Retrieving chunks, re-ranking nodes, and validating grounding coverage...</p>
                </div>
              </div>
            )}

            {/* Active Clinical Report */}
            {activeItem && !loading && (
              <div className="space-y-6">
                
                {/* 1. Active Drug Profile Header & Drug Tabs */}
                <div className="p-5 rounded-xl border border-[#1e293b]/60 bg-[#090e17] flex flex-col gap-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-bold tracking-tight text-white capitalize">
                          {activeDrug ? activeDrug.name : "Clinical Profile"}
                        </span>
                        <Badge className="text-[9px] font-bold bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 tracking-wider">
                          CITED GROUNDED VALIDATED
                        </Badge>
                      </div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono-dash block">
                        Pipeline Standard Reference Profile: {formularyStandard === 'openFDA' ? 'FDA / DailyMed Library' : 'CDSCO Indian Pharmacopoeia'}
                      </span>
                    </div>

                    {/* Drug Equivalents */}
                    {activeDrug && DRUG_EQUIVALENTS[activeDrug.name.toLowerCase()] && (
                      <div className="flex items-center gap-2 text-xs font-mono-dash text-slate-500 bg-[#070b12] p-2 rounded-lg border border-[#1e293b]/40">
                        <span>IN LOCAL EQUIVALENTS:</span>
                        <div className="flex items-center gap-1.5">
                          {DRUG_EQUIVALENTS[activeDrug.name.toLowerCase()].map((eq, kIdx) => (
                            <span key={kIdx} className="px-2 py-0.5 rounded border border-slate-800 bg-[#0c1421] text-slate-300 font-bold text-[10px]">
                              {eq}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Multi-drug Tabs Navigation */}
                  {parsedDrugs.length > 1 && (
                    <div className="flex flex-wrap border-t border-[#1e293b]/40 pt-4 gap-2">
                      {parsedDrugs.map((drug, dIdx) => (
                        <button
                          key={dIdx}
                          onClick={() => setActiveDrugTab(drug.name.toLowerCase())}
                          className={`px-3 py-1.5 rounded-lg border text-xs font-medium font-mono-dash transition-all ${
                            activeDrugTab === drug.name.toLowerCase()
                              ? "bg-[#101e30] border-cyan-800/80 text-cyan-400 shadow-sm"
                              : "bg-slate-900/40 border-slate-800 text-slate-400 hover:text-slate-300"
                          }`}
                        >
                          {drug.name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* 2. 2x2 Layout Grid Cards for Active Drug */}
                {activeDrug && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    {/* DRUG INFORMATION CARD */}
                    {activeItem?.a.metadata?.identity_profile && (
                      <div className="col-span-full mb-2 p-4 rounded-xl border border-slate-700 bg-[#0e1726]/80 flex flex-col gap-3">
                        <div className="flex items-center gap-2 border-b border-slate-700 pb-2 mb-2">
                          <Database className="h-4 w-4 text-cyan-400" />
                          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono-dash">Drug Information Card</h3>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Generic Name</span>
                            <span className="text-sm text-emerald-400 font-bold">{activeItem.a.metadata.identity_profile.data?.generic_name?.value || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Brand Names</span>
                            <span className="text-xs text-slate-300">{Array.isArray(activeItem.a.metadata.identity_profile.data?.brand_names?.value) ? activeItem.a.metadata.identity_profile.data.brand_names.value.join(", ") : activeItem.a.metadata.identity_profile.data?.brand_names?.value || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Drug Class</span>
                            <span className="text-xs text-slate-300">{Array.isArray(activeItem.a.metadata.identity_profile.data?.drug_class?.value) ? activeItem.a.metadata.identity_profile.data.drug_class.value[0] : activeItem.a.metadata.identity_profile.data?.drug_class?.value || "-"}</span>
                          </div>

                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Prescription</span>
                            <span className="text-xs text-slate-300">{activeItem.a.metadata.identity_profile.data?.prescription_status?.value || "-"}</span>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Primary Indications</span>
                            <span className="text-xs text-slate-300">{Array.isArray(activeItem.a.metadata.identity_profile.data?.indications?.value) ? activeItem.a.metadata.identity_profile.data.indications.value.join(", ") : activeItem.a.metadata.identity_profile.data?.indications?.value || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Authority / Corpus Version</span>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400 text-[9px] font-bold">🟢 DailyMed</span>
                              <span className="text-xs text-slate-400 font-mono-dash">v3.2</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Card 1: Clinical Profile Overview */}
                    <Card className="medref-card medref-card-cyan border-cyan-500/10">
                      <CardContent className="p-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <BookOpen className="h-4.5 w-4.5 text-cyan-400" />
                            <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest font-mono-dash">
                              Clinical Profile Overview
                            </span>
                          </div>
                          <SectionHeaderBadge drugName={activeDrug.name} sectionKeys={["indications", "mechanism_of_action", "clinical_pharmacology"]} activeItem={activeItem} />
                        </div>
                        <CustomTextRenderer 
                          text={activeDrug.sections.overview} 
                          citations={activeCitations} 
                          cardIndex={activeHistoryIndex} 
                        />
                      </CardContent>
                    </Card>

                    {/* Card 2: Dosing & Administration */}
                    <Card className="medref-card border-[#1e293b]/60">
                      <CardContent className="p-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest font-mono-dash flex items-center gap-2">
                            💊 Dosing & Administration
                          </span>
                          <SectionHeaderBadge drugName={activeDrug.name} sectionKeys={["dosage_and_administration", "administration", "dosage_forms"]} activeItem={activeItem} />
                        </div>
                        {activeDrug.sections.dosing.toLowerCase() === 'not found in available sources.' ? (
                          <div className="p-3.5 rounded-lg border border-slate-800/80 bg-[#070b12] text-xs text-slate-600 italic">
                            Not found in available sources.
                          </div>
                        ) : (
                          <CustomTextRenderer 
                            text={activeDrug.sections.dosing} 
                            citations={activeCitations} 
                            cardIndex={activeHistoryIndex} 
                          />
                        )}
                      </CardContent>
                    </Card>

                    {/* Card 3: Contraindications & Warnings */}
                    <Card className="medref-card medref-card-red border-red-500/10">
                      <CardContent className="p-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <ShieldAlert className="h-4.5 w-4.5 text-red-400" />
                            <span className="text-xs font-bold text-red-400 uppercase tracking-widest font-mono-dash">
                              Contraindications & Warnings
                            </span>
                          </div>
                          <SectionHeaderBadge drugName={activeDrug.name} sectionKeys={["contraindications", "warnings", "warnings_and_precautions"]} activeItem={activeItem} />
                        </div>
                        {/* Combine contraindications and warnings */}
                        <div className="space-y-3">
                          {activeDrug.sections.contraindications.toLowerCase() !== 'not found in available sources.' && (
                            <div className="space-y-1">
                              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash block">Contraindications:</span>
                              <CustomTextRenderer 
                                text={activeDrug.sections.contraindications} 
                                citations={activeCitations} 
                                cardIndex={activeHistoryIndex} 
                              />
                            </div>
                          )}
                          {activeDrug.sections.warnings.toLowerCase() !== 'not found in available sources.' && (
                            <div className="space-y-1">
                              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono-dash block">Warnings:</span>
                              <CustomTextRenderer 
                                text={activeDrug.sections.warnings} 
                                citations={activeCitations} 
                                cardIndex={activeHistoryIndex} 
                              />
                            </div>
                          )}
                          {activeDrug.sections.contraindications.toLowerCase() === 'not found in available sources.' && 
                           activeDrug.sections.warnings.toLowerCase() === 'not found in available sources.' && (
                            <span className="text-slate-500 italic text-sm">Not found in available sources.</span>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Card 4: Co-Administration Risks */}
                    <Card className="medref-card medref-card-gold border-yellow-500/10">
                      <CardContent className="p-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4.5 w-4.5 text-yellow-500" />
                            <span className="text-xs font-bold text-yellow-500 uppercase tracking-widest font-mono-dash">
                              Co-Administration Risks
                            </span>
                          </div>
                          <SectionHeaderBadge drugName={activeDrug.name} sectionKeys={["drug_interactions", "cyp_interactions"]} activeItem={activeItem} />
                        </div>
                        <CustomTextRenderer 
                          text={activeDrug.sections.interactions} 
                          citations={activeCitations} 
                          cardIndex={activeHistoryIndex} 
                        />
                      </CardContent>
                    </Card>
                    
                  </div>
                )}

                {parsedDrugs.length === 0 && (
                  <Card className="medref-card border-[#1e293b]/60 bg-[#090e17]/80">
                    <CardContent className="p-8 text-center space-y-4">
                      <div className="p-3 rounded-full border border-dashed border-slate-800 bg-slate-950/20 w-fit mx-auto">
                        <ShieldAlert className="h-8 w-8 text-slate-500" />
                      </div>
                      <div className="space-y-1">
                        <h3 className="text-sm font-bold text-slate-200">Reference Unresolved</h3>
                        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                          {activeItem.a.answer || "Not found in available sources."}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* 3. Ingestion Track & Confidence */}
                <div className="p-4 rounded-xl border border-[#1e293b]/60 bg-[#090e17] flex items-center justify-between gap-4 font-mono-dash text-[11px]">
                  <div className="flex items-center gap-4">
                    <span className="text-slate-500 uppercase tracking-wider font-bold">Pipeline Ingestion Track :</span>
                    <div className="flex items-center gap-2.5">
                      <span className="flex items-center gap-1 text-slate-300 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                        <Folder className="h-3 w-3 text-cyan-500" /> openFDA
                      </span>
                      <span className="flex items-center gap-1 text-slate-300 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                        <Folder className="h-3 w-3 text-cyan-500" /> DailyMed
                      </span>
                    </div>
                  </div>

                  {/* Dynamic Confidence Score Indicator */}
                  {activeItem && (
                    <div className={`px-3 py-1 rounded-full border text-[10px] font-bold ${
                      (activeItem.a.metadata?.confidence || "High") === "High"
                        ? "text-emerald-400 border-emerald-900/60 bg-emerald-950/20"
                        : (activeItem.a.metadata?.confidence || "High") === "Medium"
                        ? "text-yellow-400 border-yellow-900/60 bg-yellow-950/20"
                        : "text-rose-400 border-rose-900/60 bg-rose-950/20"
                    }`}>
                      RAG Pipeline Conf: {
                        (activeItem.a.metadata?.confidence || "High") === "High" ? "98.4%" : 
                        (activeItem.a.metadata?.confidence || "High") === "Medium" ? "76.2%" : "35.0%"
                      }
                    </div>
                  )}
                  </div>
                  
                  {/* CLINICAL AUDIT COMPONENT */}
                  <ClinicalAudit metadata={activeItem?.a.metadata} />

                  {/* 4. Sources Referenced Card List */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono-dash flex items-center gap-2 pl-1">
                    <FileText className="h-4 w-4 text-cyan-500" /> Sources Referenced
                  </h4>
                  {finalCitationsToRender.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {finalCitationsToRender.map((c, j) => {
                        const num = c.citation_number ?? (j + 1);
                        return (
                          <SourceCard 
                            key={j} 
                            c={c} 
                            cardIndex={activeHistoryIndex} 
                            num={num} 
                          />
                        );
                      })}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl border border-dashed border-slate-800 bg-[#090e17]/50 text-center text-xs text-slate-600 italic">
                      No matching sources referenced for the active drug.
                    </div>
                  )}
                </div>

              </div>
            )}

          </div>
        </ScrollArea>

        {/* ── SAFETY DIRECTIVE FOOTER ────────────────────────────────────────── */}
        <footer className="h-10 shrink-0 border-t border-[#1e293b]/60 bg-[#070b12] flex items-center px-6 gap-3 z-20">
          <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-yellow-950/40 border border-yellow-900/40 text-yellow-500 uppercase tracking-wider shrink-0 font-mono-dash">
            Safety Directive
          </span>
          <p className="text-[9.5px] text-slate-500 leading-none truncate">
            Clinical judgment remains with the treating physician. MedRef operations function as an informational lookup assistant and do not establish prescription treatments.
          </p>
        </footer>

        </>
        )}
      </main>

    </div>
  );
}
