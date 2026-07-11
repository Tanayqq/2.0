import { useState } from "react";
import { queryMedicalAPI, type AnswerResponse } from "./services/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { Info, Activity, ShieldAlert, Loader2 } from "lucide-react";

function CitationRenderer({ 
  text, 
  citations, 
  cardIndex 
}: { 
  text: string; 
  citations: AnswerResponse["citations"]; 
  cardIndex: number;
}) {
  // Regex to match [X] where X is sequential number, or [Unsupported Citation Removed]
  const regex = /\[([0-9]+)\]|\[Unsupported Citation Removed\]/g;
  const parts = [];
  let lastIndex = 0;
  
  const handleCitationClick = (e: React.MouseEvent, docId: string) => {
    e.preventDefault();
    const citation = citations.find(c => c.document_id === docId);
    if (citation && citation.uuid) {
      const elementId = `citation-${cardIndex}-${citation.uuid}`;
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        element.classList.add("ring-2", "ring-teal-400", "bg-teal-50", "transition-all", "duration-300");
        setTimeout(() => {
          element.classList.remove("ring-2", "ring-teal-400", "bg-teal-50");
        }, 2000);
      }
    }
  };

  let match;
  while ((match = regex.exec(text)) !== null) {
    // Push preceding text
    if (match.index > lastIndex) {
      parts.push(<span key={lastIndex}>{text.substring(lastIndex, match.index)}</span>);
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
      const citation = citations.find(c => c.document_id === docId);
      
      if (citation) {
        parts.push(
          <HoverCard key={match.index} openDelay={200}>
            <HoverCardTrigger asChild>
              <sup className="align-super select-none">
                <span 
                  onClick={(e) => handleCitationClick(e, docId)}
                  className="inline-flex items-center justify-center text-[9px] leading-none font-bold px-1.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 hover:text-teal-800 transition-all cursor-pointer shadow-sm hover:shadow active:scale-95 ml-0.5"
                >
                  {docId}
                </span>
              </sup>
            </HoverCardTrigger>
            <HoverCardContent className="w-80 border-slate-200 shadow-xl bg-white p-4 rounded-xl z-50">
              <div className="space-y-2.5 text-left">
                <div className="flex items-center justify-between border-b pb-1.5 border-slate-100">
                  <span className="text-xs font-bold uppercase tracking-wider text-teal-600">{citation.source.split(" – ")[0]}</span>
                  {citation.similarity !== undefined && (
                    <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                      Match: {(citation.similarity * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Drug Context</span>
                  <span className="text-sm font-bold text-slate-800">{citation.drug || "N/A"}</span>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Section</span>
                  <span className="text-xs font-medium text-slate-700 block bg-slate-50 p-1.5 rounded border border-slate-100 line-clamp-1">
                    {citation.section || "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Excerpt</span>
                  <p className="text-xs text-slate-600 italic bg-slate-50 p-2 rounded border border-slate-100 leading-normal line-clamp-4">
                    "{citation.snippet}"
                  </p>
                </div>
              </div>
            </HoverCardContent>
          </HoverCard>
        );
      } else {
        parts.push(<sup key={match.index} className="align-super text-slate-500 font-medium">[{docId}]</sup>);
      }
    }
    
    lastIndex = match.index + match[0].length;
  }
  
  if (lastIndex < text.length) {
    parts.push(<span key={lastIndex}>{text.substring(lastIndex)}</span>);
  }
  
  return <div className="leading-relaxed whitespace-pre-wrap">{parts}</div>;
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
          <span className="font-semibold text-teal-400">Environment: </span> Development
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
                    {item.a.citations.length > 0 ? (
                      <div className="space-y-2 w-full">
                        {item.a.citations.map((c, j) => (
                          <div 
                            key={j} 
                            id={`citation-${i}-${c.uuid}`}
                            className="flex items-center text-sm text-slate-600 p-2 rounded-lg border border-slate-200 bg-white shadow-sm transition-all duration-300"
                          >
                            <span className="inline-flex items-center justify-center font-bold text-teal-700 bg-teal-50 border border-teal-200 rounded-full h-5 w-5 text-xs mr-3 shrink-0">
                              {c.document_id}
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="font-semibold text-slate-800 truncate">{c.source}</p>
                            </div>
                            {c.count && c.count > 1 && (
                              <Badge variant="secondary" className="ml-2 bg-slate-100 text-slate-600 border border-slate-200 text-[10px] shrink-0">
                                Referenced {c.count} times
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-sm text-slate-500 italic">No references retrieved for this query.</span>
                    )}
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
