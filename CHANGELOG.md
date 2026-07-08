# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial system architecture designs (Phase 0).
- Engineering rules, API specifications, and database designs.
- Comprehensive security and testing strategies.
- Roadmap and vision documents.

### Engineering Decisions
- **LLM Strategy**: Groq is the primary development provider; MedGemma is the target production model. Abstraction ensures interchangeability.
- **Embeddings**: MedCPT will run locally; no external APIs.
- **Ingestion**: Kept as simple sequential scripts for MVP; deferred Celery/Airflow.
- **Frontend UI**: Adopted shadcn/ui with TailwindCSS. Citations will use inline references with hover previews and a full bibliography.
- **Evaluation**: Inserted a strict evaluation phase (benchmark harness + golden dataset) prior to UI development.
- **Database**: Qdrant designed for multiple collections from the start.
- **Stack**: Selected FastAPI (Python 3.11) and React (Vite/Tailwind) as the core web stack.
