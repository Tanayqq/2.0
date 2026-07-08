# API Specifications

## REST API Standards
- **Base URL**: `/api/v1`
- **Format**: JSON (`application/json`)
- **Naming**: Plural nouns for resources (e.g., `/api/v1/queries`).

## Endpoint Conventions

### `POST /api/v1/query`
Submit a clinical query for the RAG platform.

**Request:**
```json
{
  "question": "What are the contraindications for Lisinopril?",
  "session_id": "uuid-v4",
  "filters": {
    "source_types": ["openFDA", "DailyMed"]
  }
}
```

**Response:**
```json
{
  "answer": "Lisinopril is contraindicated in patients with a history of angioedema...",
  "citations": [
    {
      "source": "openFDA",
      "document_id": "12345",
      "snippet": "Contraindicated in history of angioedema..."
    }
  ],
  "disclaimer": "Clinical judgment remains with the treating physician.",
  "metadata": {
    "processing_time_ms": 1250,
    "provider_used": "Groq"
  }
}
```

### `GET /health`
System health check endpoint for orchestration probes.

**Response:**
```json
{
  "status": "healthy",
  "dependencies": {
    "qdrant": "up",
    "llm_provider": "up"
  }
}
```

## Error Responses
Consistent error structure mapped to standard HTTP status codes:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Question cannot be empty.",
    "details": []
  }
}
```

## Authentication Strategy (Future)
- **Phase 2**: JWT-based authentication via OAuth2 (e.g., Keycloak or Auth0).
- Role-based access control (RBAC) to differentiate between admin staff and physicians.

## Versioning Strategy
- URI Versioning (`/v1/`, `/v2/`).
- Deprecation notices must be sent via response headers (`Sunset`) 6 months prior to removal.
