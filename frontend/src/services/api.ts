export interface Citation {
  document_id: string;
  source: string;
  snippet: string;
  uuid?: string;
  drug?: string;
  section?: string;
  similarity?: number;
  count?: number;
  citation_number?: number;
}

export interface AnswerResponse {
  answer: string;
  citations: Citation[];
  metadata: {
    retrieval_latency_sec?: number;
    llm_latency_sec?: number;
    total_latency_sec?: number;
    provider?: string;
    confidence?: string;
    audit?: any;
    identity_profile?: any;
    
    // MedRef Phase 2 Enriched Metadata
    section_status?: Record<string, Record<string, {
      status: string;
      confidence_stars: string;
      original_section: string | null;
      evidence_count: number;
      evidence_diversity: string | null;
      authority: string;
      missing_reason: string | null;
    }>>;
    retrieval_trace?: any[];
    clinical_coverage?: {
      sections: Record<string, boolean>;
      overall_percentage: number;
    };
    provenance_block?: {
      authority: string;
      document: string;
      version: string;
      corpus: string;
      chunk_id: string;
    }[];
    groundedness?: string;
    groundedness_details?: string;
    latency_breakdown?: {
      alias_resolution_ms: number;
      identity_lookup_ms: number;
      vector_search_ms: number;
      rerank_ms: number;
      generation_ms: number;
    };
  };
}

// Fallback to localhost if environment variable is not set (useful for local dev)
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const queryMedicalAPI = async (question: string): Promise<AnswerResponse> => {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    let errorMsg = response.statusText;
    try {
      const errorData = await response.json();
      if (errorData.error) errorMsg = errorData.error;
    } catch (e) {
      // Ignore JSON parse errors if response is not JSON
    }
    throw new Error(`API Error: ${errorMsg}`);
  }

  return response.json();
};
