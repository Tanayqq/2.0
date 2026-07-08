# Testing Strategy

## Unit Testing
- **Framework**: `pytest`.
- **Target**: Domain logic, Prompt formatters, Utilities, Validation models.
- **Coverage**: Minimum 80% coverage required.
- **Mocks**: Mock external LLM responses and Qdrant queries to ensure tests are fast, cheap, and deterministic.

## Integration Testing
- Test the API endpoints (`FastAPI TestClient`) against a real (but localized/Dockerized) Qdrant instance and a test database.
- Test the configuration swapping of LLM providers using lightweight stubs to ensure the factory pattern operates correctly.

## End-to-End Testing
- Automated UI tests using Playwright or Cypress.
- Simulate a full query flow: Frontend request -> Backend routing -> Vector DB retrieval -> Mock LLM generation -> Frontend citation rendering.

## Evaluation Phase (Pre-UI)
- An evaluation phase will be inserted *before* building the React UI.
- Build a curated "golden dataset" of clinical questions with known exact answers.
- Implement a benchmark harness to programmatically evaluate the RAG pipeline.
- Automate evaluation using frameworks like `Ragas` or `TruLens`.
- **Metrics**:
  - **Context Precision**: Are the retrieved documents relevant to the medical query?
  - **Answer Faithfulness**: Is the answer derived *strictly* from the retrieved context, or did it hallucinate?
  - **Answer Relevancy**: Does it actually address the user's clinical question?

## Regression Testing
- Run the RAG evaluation pipeline on every major model upgrade, prompt tweak, or embedding model change to ensure clinical accuracy does not degrade over time.
