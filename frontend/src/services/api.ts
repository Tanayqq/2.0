export interface Citation {
  document_id: string;
  source: string;
  snippet: string;
  uuid?: string;
  drug?: string;
  section?: string;
  similarity?: number;
  count?: number;
}

export interface AnswerResponse {
  answer: string;
  citations: Citation[];
  metadata: {
    retrieval_latency_sec?: number;
    llm_latency_sec?: number;
    total_latency_sec?: number;
    provider?: string;
  };
}

// Fallback to localhost if environment variable is not set (useful for local dev)
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const queryMedicalAPI = async (question: string): Promise<AnswerResponse> => {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
};
