import { useState } from "react";
import { queryMedicalAPI, type AnswerResponse } from "./services/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Info, Activity, ShieldAlert, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { InlineCitation } from "./components/InlineCitation";

function CitationRenderer({ 
  text, 
  citations, 
  cardIndex 
}: { 
  text: string; 
  citations: AnswerResponse["citations"]; 
  cardIndex: number;
}) {
  console.log("Rendering answer:", text);
  
  const regex = /\[([0-9]+)\]|\[Unsupported Citation Removed\]/g;

  // Split text into individual sentences safely to render one fact per line
  const sentences = text
    .replace(/(\[[0-9]+\]|\[Unsupported Citation Removed\]|[.!?])\s+/g, '$1<SENTENCE_BOUNDARY>')
    .split('<SENTENCE_BOUNDARY>')
    .map(s => s.trim())
    .filter(Boolean);

  const handleCitationClick = (e: React.MouseEvent, docId: string) => {
    e.preventDefault();
    const num = parseInt(docId, 10);
    const citation = citations.find(c => (c.citation_number ?? parseInt(c.document_id, 10)) === num);
    
    if (citation) {
      const elementId = `citation-card-${cardIndex}-${citation.citation_number ?? citation.document_id}`;
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        // Briefly highlight with a fade-out effect for 1 second
        element.classList.add("ring-2", "ring-blue-400", "bg-blue-50/50", "scale-[1.01]");
        setTimeout(() => {
          element.classList.remove("ring-2", "ring-blue-400", "bg-blue-50/50", "scale-[1.01]");
        }, 1000);
      }
    }
  };

  return (
    <div className="space-y-2.5">
      {sentences.map((sentence, idx) => {
        const parts = [];
        let lastIndex = 0;
        let match;
        
        // Reset regex index for this sentence
        regex.lastIndex = 0;
        
        while ((match = regex.exec(sentence)) !== null) {
          if (match.index > lastIndex) {
            parts.push(<span key={lastIndex}>{sentence.substring(lastIndex, match.index)}</span>);
          }
          
          const matchedText = match[0];
          if (matchedText === "[Unsupported Citation Removed]") {
            parts.push(
              <span key={match.index} className="inline-flex px-1.5 py-0.5 text-xs text-red-500 font-bold bg-red-50 border border-red-200 rounded" title="A citation was removed because it was not grounded in the retrieved clinical sources.">
                [Unsupported Citation Removed]
              </span>
            );
          } else {
            const docId = match[1];
            const num = parseInt(docId, 10);
            const citation = citations.find(c => (c.citation_number ?? parseInt(c.document_id, 10)) === num);
            
            if (citation) {
              parts.push(
                <InlineCitation 
                  key={match.index}
                  citation={citation}
                  onClick={(e) => handleCitationClick(e, docId)}
                />
              );
            } else {
              parts.push(
                <span key={match.index} className="inline-flex px-1.5 py-0.5 text-xs text-red-500 font-bold bg-red-50 border border-red-200 rounded" title="A citation was removed because it was not grounded in the retrieved clinical sources.">
                  [Unsupported Citation Removed]
                </span>
              );
            }
          }
          
          lastIndex = match.index + match[0].length;
        }
        
        if (lastIndex < sentence.length) {
          parts.push(<span key={lastIndex}>{sentence.substring(lastIndex)}</span>);
        }
        
        // Determine if it is a list-like fact (e.g. starts with key drug names or contains citations)
        const isIntro = sentence.toLowerCase().startsWith("based on") || sentence.toLowerCase().startsWith("here is") || sentence.endsWith(":");
        const isFact = !isIntro && (sentence.includes("[") || /^(metformin|lisinopril|atorvastatin|warfarin|gabapentin|omeprazole|amoxicillin|albuterol|losartan|ibuprofen)/i.test(sentence));
        
        if (isFact) {
          return (
            <div key={idx} className="flex items-start gap-2.5 text-slate-700 hover:text-slate-900 transition-colors duration-150 pl-1">
              <span className="text-blue-500 shrink-0 mt-2 select-none font-bold text-xs leading-none">•</span>
              <span className="leading-relaxed text-[14.5px]">{parts}</span>
            </div>
          );
        } else {
          return (
            <p key={idx} className="text-slate-800 font-medium leading-relaxed mb-1.5 text-[14.5px]">
              {parts}
            </p>
          );
        }
      })}
    </div>
  );
}

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
      className="flex flex-col text-sm text-slate-700 p-4 rounded-xl border border-slate-200 bg-white shadow-sm transition-all duration-300 gap-3"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span className="inline-flex items-center justify-center font-bold text-blue-700 bg-blue-50 border border-blue-200 rounded-lg h-7 w-7 text-xs mr-1 shrink-0">
            [{num}]
          </span>
          <div className="space-y-1 flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-slate-800 text-sm">{c.source}</span>
              {c.drug && (
                <Badge variant="outline" className="text-slate-500 border-slate-200 bg-slate-50 text-[10px]">
                  {c.drug}
                </Badge>
              )}
              {c.section && (
                <Badge variant="secondary" className="text-slate-500 bg-slate-100 text-[10px]">
                  {c.section}
                </Badge>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 shrink-0">
          {c.similarity !== undefined && (
            <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50 text-[10px]">
              Match: {(c.similarity * 100).toFixed(0)}%
            </Badge>
          )}
          {c.count && c.count > 0 && (
            <Badge className="bg-slate-100 text-slate-600 hover:bg-slate-200 text-[10px] border border-slate-200">
              Referenced {c.count} time{c.count > 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </div>

      {/* Snippet Area (Expandable on click) */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className="cursor-pointer hover:bg-slate-100/50 p-2.5 rounded-lg border border-slate-100 bg-slate-50 transition-colors duration-200 group relative"
        title={expanded ? "Click to collapse" : "Click to expand"}
      >
        <p className={`text-xs text-slate-600 italic leading-relaxed transition-all duration-300 ${expanded ? "" : "line-clamp-2"}`}>
          "{c.snippet}"
        </p>
        <div className="mt-1 flex items-center justify-end gap-1 text-[10px] text-slate-400 font-medium group-hover:text-blue-500 select-none">
          {expanded ? (
            <>
              <span>Click to collapse</span>
              <ChevronUp className="h-3 w-3" />
            </>
          ) : (
            <>
              <span>Click to expand</span>
              <ChevronDown className="h-3 w-3" />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<{q: string, a: AnswerResponse}[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await queryMedicalAPI(query);
      console.log("API response answer:", response.answer);
      setHistory(prev => [...prev, { q: query, a: response }]);
      setQuery("");
    } catch (err: any) {
      setError(err.message || "An unknown error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-slate-900 text-white px-6 py-4 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-6 w-6 text-teal-400" />
          <h1 className="text-xl font-bold tracking-tight">MedRef Clinical Platform</h1>
        </div>
        <div className="text-sm text-slate-400">
          <span className="font-semibold text-teal-400">Environment: </span> {import.meta.env.MODE === 'production' ? 'Production' : 'Development'}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto p-6 space-y-6">
        
        {/* Answer Cards Area */}
        <ScrollArea className="h-[65vh] pr-4">
          <div className="space-y-8">
            {history.length === 0 && !loading && (
              <div className="text-center text-slate-500 mt-20 flex flex-col items-center">
                <ShieldAlert className="h-12 w-12 text-slate-300 mb-4" />
                <h2 className="text-lg font-medium text-slate-700">No Active Queries</h2>
                <p>Submit a clinical question below to retrieve trusted references.</p>
              </div>
            )}
            
            {history.map((item, i) => (
              <Card key={i} className="shadow-md border-slate-200">
                <CardHeader className="bg-slate-100 border-b pb-4 rounded-t-xl">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg text-slate-800 font-semibold">
                      Query: <span className="font-medium text-slate-600 ml-1">{item.q}</span>
                    </CardTitle>
                    <Badge variant="outline" className="text-teal-700 border-teal-200 bg-teal-50 ml-4 shrink-0">
                      {item.a.metadata?.provider || "Groq"} ({item.a.metadata?.total_latency_sec || "N/A"}s)
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 text-slate-800 text-[15px]">
                  <CitationRenderer text={item.a.answer} citations={item.a.citations} cardIndex={i} />
                </CardContent>
                <CardFooter className="flex flex-col items-start gap-4 border-t pt-4 bg-slate-50 rounded-b-xl">
                  <div className="w-full">
                    <h4 className="text-sm font-bold text-slate-700 mb-2">Sources Referenced:</h4>
                    {(() => {
                      const referencedNums = new Set<number>();
                      const citationRegex = /\[([0-9]+)\]/g;
                      let m;
                      while ((m = citationRegex.exec(item.a.answer)) !== null) {
                        referencedNums.add(parseInt(m[1], 10));
                      }
                      
                      const activeCitations = item.a.citations.filter(c => {
                        const num = c.citation_number ?? parseInt(c.document_id, 10);
                        return referencedNums.has(num);
                      });

                      if (activeCitations.length > 0) {
                        return (
                          <div className="space-y-3 w-full">
                            {activeCitations.map((c, j) => {
                              const num = c.citation_number ?? parseInt(c.document_id, 10);
                              return (
                                <SourceCard 
                                  key={j} 
                                  c={c} 
                                  cardIndex={i} 
                                  num={num} 
                                />
                              );
                            })}
                          </div>
                        );
                      } else {
                        return <span className="text-sm text-slate-500 italic">No references retrieved for this query.</span>;
                      }
                    })()}
                  </div>
                  <Alert variant="destructive" className="bg-red-50 border-red-200 mt-2">
                    <Info className="h-4 w-4" />
                    <AlertTitle>Disclaimer</AlertTitle>
                    <AlertDescription className="text-xs">
                      Clinical judgment remains with the treating physician. Verify all outputs against official clinical guidelines.
                    </AlertDescription>
                  </Alert>
                </CardFooter>
              </Card>
            ))}

            {loading && (
              <div className="flex justify-center p-8">
                <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
              </div>
            )}
            
            {error && (
              <Alert variant="destructive">
                <ShieldAlert className="h-4 w-4" />
                <AlertTitle>Retrieval Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="flex gap-4 items-center bg-white p-2 rounded-lg shadow-sm border border-slate-200">
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search diseases, interactions, or dosing (e.g. 'What are the contraindications for Lisinopril?')" 
            className="flex-1 border-0 shadow-none focus-visible:ring-0 text-base"
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !query.trim()} className="bg-slate-900 hover:bg-slate-800 text-white px-6">
            Retrieve
          </Button>
        </form>
        
      </main>
    </div>
  );
}
