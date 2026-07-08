# Engineering Rules

## Naming Conventions
- **Python**: PEP 8. `snake_case` for variables/functions, `PascalCase` for classes.
- **TypeScript/React**: `camelCase` for variables, `PascalCase` for components.
- **Interfaces/Protocols**: Suffix with `Protocol` in Python (e.g., `LLMProviderProtocol`).
- **Database**: `snake_case` for collection names and fields.

## Folder Conventions
- Keep folders shallow where possible.
- Use `index.ts` in frontend to export components cleanly.
- Keep domain models completely free of framework imports (e.g., no FastAPI/Pydantic in core domain entities if possible, or use purely declarative Pydantic).

## Coding Standards (SOLID, DRY, KISS)
- **Dependency Injection**: Pass dependencies (database sessions, LLM clients) via FastAPI `Depends()`. Avoid global singletons where possible.
- **Single Responsibility**: A class or function should do one thing. 
- **Fail Fast**: Validate inputs immediately at the API boundaries.
- **KISS**: Do not over-engineer solutions until scale demands it (e.g., start with sync database calls if async isn't proving a bottleneck).

## Commenting Standards
- Use docstrings (Google format) for all public functions, classes, and modules.
- Explain *why* a decision was made, not *what* the code does, for inline comments.

## Error Handling
- Use custom exception classes inheriting from a base `MedRefException`.
- Never expose internal stack traces to the client.
- Always log the full stack trace internally.

## Logging Rules
- Use structured JSON logging (e.g., using `structlog`).
- **Levels**: INFO for business events, DEBUG for development, ERROR for exceptions, CRITICAL for system failures.
- **Context**: Inject Request IDs into logs for traceability across microservices.
- **SECURITY (PHI)**: NEVER log Personally Identifiable Information (PII) or Protected Health Information (PHI).

## Documentation Strategy
- Maintain updated OpenAPI (Swagger) specs natively through FastAPI.
- Update `CHANGELOG.md` and `ARCHITECTURE.md` with every major PR.

## Git Conventions
- **Branching**: `feature/branch-name`, `bugfix/branch-name`, `hotfix/branch-name`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).
- **PRs**: Require at least 1 approval, passing CI/CD, and 80%+ test coverage.

## Technical Debt Prevention Plan
- Run static analysis (`mypy`, `ruff`, `eslint`) on every commit via `pre-commit` hooks.
- Schedule regular tech-debt reduction sprints (1 per quarter).
- Ensure modules remain decoupled so replacing an obsolete technology (e.g., switching Vector DBs) takes <1 sprint.
