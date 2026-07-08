# Roadmap

## Phase 0: Architecture & Foundation (Approved)
- Define overall system architecture, engineering guidelines, and API specifications.
- Establish database design, RAG flow, security, and testing strategies.

## Phase 1: Core MVP (Current Focus)
- Setup project repositories utilizing Clean Architecture folder structures.
- Implement the Provider Pattern for LLMs (Groq for dev, MedGemma for prod).
- Setup Qdrant (multi-collection design) and basic sequential data ingestion scripts.
- Build the foundational FastAPI backend and integrate local MedCPT embeddings.
- **Evaluation Phase**: Build a benchmark harness and curated golden dataset to evaluate RAG metrics.
- Build the React/Vite frontend (using shadcn/ui) with inline citation rendering, hover previews, and a bibliography.
- Enforce strict prompts, zero-hallucination policies, and citation rendering.

## Phase 2: Feature Expansion
- Introduce the Drug Interaction Engine.
- Implement Medical Calculators (e.g., eGFR, CHADS2-VASc).
- Enhance the RAG pipeline with Cross-Encoder Reranking and Query Expansion.
- Expand data sources to include PubMed and RxNorm.

## Phase 3: Platform Ecosystem
- Add Authentication and User Profiles (Search history, bookmarks).
- Integrate Indian Drug Database (CDSCO, National Formulary of India).
- Enable Hospital Protocol Search.

## Phase 4: Offline & Enterprise
- Package a fully offline hospital deployment (Local LLM + Local DB).
- Build an Admin dashboard for hospital protocol ingestion and management.
