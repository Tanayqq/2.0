# Security Strategy

## Secrets Management
- All secrets (API Keys, DB passwords, Provider Keys) are strictly stored in `.env` files for local development.
- In production, utilize Kubernetes Secrets or HashiCorp Vault.
- NEVER commit `.env` files to source control.

## Rate Limiting
- Apply rate limiting at the API Gateway level using FastAPI `Slowapi` + Redis.
- Prevents abuse and manages variable costs associated with external LLM providers.

## Input Validation
- Strict Pydantic models for all incoming API requests.
- Sanitize inputs to prevent prompt injection attacks (e.g., escaping system instruction override attempts).

## Dependency Security
- Use `Dependabot` or `Snyk` to continuously scan for vulnerable packages.
- Pin dependencies in `requirements.txt` with hashes, or use `Poetry` for deterministic builds.

## Audit Logging
- Log all queries and responses for system performance tuning and usage auditing.
- **CRITICAL**: Ensure no Patient Health Information (PHI) is ever logged. If users input patient data despite warnings, employ an anonymization layer (e.g., Microsoft Presidio) before logging or processing.

## Future Authentication
- Integrate OAuth2/OIDC (OpenID Connect) for secure access control.
- Implement Role-Based Access Control (RBAC) to restrict sensitive databases (e.g., internal hospital protocols) to authorized physicians only.
