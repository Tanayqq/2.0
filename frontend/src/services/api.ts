export interface Citation {
  document_id: string;
  source: string;
  snippet: string;
  uuid?: string;
  drug?: string;
  section?: string;
  authority?: string;
  authority_priority?: number;
  freshness_factor?: number;
  domain?: string;
  similarity?: number;
  count?: number;
  citation_number?: number;
}

export interface PatientProfilePayload {
  age?: number;
  gender?: string;
  eGFR?: number;
  hepatic_stage?: string;
  pregnancy?: boolean;
  smoking?: boolean;
  comorbidities?: string[];
  active_medications?: string[];
  allergies?: string[];
  vitals?: Record<string, any>;
  recent_labs?: Record<string, any>;
}

export interface AnswerResponse {
  answer: string;
  citations: Citation[];
  disclaimer?: string;
  metadata: {
    retrieval_latency_sec?: number;
    llm_latency_sec?: number;
    total_latency_sec?: number;
    provider?: string;
    confidence?: string;
    retrieval_confidence?: string;
    retrieval_stats?: {
      retrieval_latency_sec?: number;
      retrieved_count?: number;
      resolved_drug?: string | null;
      detected_sections?: string[];
      section_statuses?: Record<string, any>;
      retrieval_trace?: any[];
    };
    identity_profile?: any;
    zero_parametric_guard_triggered?: boolean;
    explainability?: any;
    conflict_resolution?: any;
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
    [key: string]: any;  // Allow additional backend fields without TS errors
  };
}

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const queryMedicalAPI = async (
  question: string,
  mode: string = "DRUG_CHAT",
  country_context: string = "GLOBAL",
  patient_profile?: PatientProfilePayload,
  conversation_id?: string
): Promise<AnswerResponse> => {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      mode,
      country_context,
      patient_profile,
      conversation_id
    }),
  });

  if (!response.ok) {
    let errorMsg = response.statusText;
    try {
      const errorData = await response.json();
      if (errorData.error) errorMsg = errorData.error;
    } catch (e) {
      // Ignore JSON parse error
    }
    throw new Error(`API Error: ${errorMsg}`);
  }

  return response.json();
};

export const fetchConversationIntake = async (
  question: string,
  conversation_id?: string,
  patient_profile?: PatientProfilePayload
) => {
  const response = await fetch(`${API_BASE_URL}/intake`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id, patient_profile }),
  });
  return response.json();
};

export const fetchQualityTelemetry = async () => {
  const response = await fetch(`${API_BASE_URL}/quality`);
  return response.json();
};
