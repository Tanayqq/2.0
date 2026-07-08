# RAG Architecture & Design

## Retrieval Pipeline
1. **Query Processing**: Clean, anonymize, and semantically expand the user's medical query.
2. **Embedding**: Convert the processed query to a high-dimensional vector using MedCPT.
3. **Vector Search**: Query Qdrant for top-K nearest chunks based on cosine similarity.
4. **Reranking (Phase 2)**: Use a cross-encoder model to re-rank results based on strict relevance to the query.
5. **Context Window Assembly**: Fit top chunks into the LLM context window while rigidly reserving space for the generated answer.

## Prompt Architecture
The system relies on a rigid prompt template to eliminate hallucinations.

```text
System Prompt:
You are MedRef, a highly strict Clinical Reference Assistant.
You must answer the user's question using ONLY the provided context documents.
If the answer is not clearly contained in the documents, output exactly: "Not found in available sources."
DO NOT hallucinate. DO NOT recommend treatments. DO NOT invent drug doses.
Always append citations to your facts using the [Document ID] provided.

Context:
[Document ID: 123] ...
[Document ID: 456] ...

Question: {user_question}
```

## LLM Provider Abstraction
To avoid vendor lock-in, all generations pass through a standard interface:
- Define `LLMProviderProtocol` in Python.
- Implement `GroqProvider`, `OllamaProvider`, `OpenAIProvider`, `AzureOpenAIProvider`.
- Use Dependency Injection to instantiate the provider based on configuration.
- The backend application only calls `provider.generate(prompt)`.

## Embedding Strategy
- **Model**: MedCPT (optimized for medical and clinical text).
- **Dimension**: Typical 768.
- **Hardware Profile**: MedCPT embeddings will be run locally on the RTX 3050. External embedding APIs will not be used to ensure data privacy and reduce dependencies.

## Chunking Strategy
- **Size**: 512 tokens with 50-token overlap to maintain medical context boundaries.
- **Semantic Chunking**: Split by document sections (e.g., "Indications", "Warnings", "Adverse Reactions") rather than purely by character count to ensure cohesive clinical thoughts are maintained in a single chunk.

## Medical Data Ingestion Architecture
- **Pipeline Architecture**: Extract -> Transform -> Chunk -> Embed -> Load.
- **Sources**: openFDA, DailyMed, PubMed (Future).
- **Tools**: For the MVP, ingestion will be implemented as simple sequential scripts. Advanced task runners like Celery or Airflow are deferred to future phases to keep the initial architecture lightweight.

## Failure Handling
- **LLM Outage**: If the primary LLM API fails, fallback to a secondary provider (e.g., Groq -> OpenAI -> Local Ollama).
- **Database Outage**: If Vector DB is unreachable, fail gracefully with `503 Service Unavailable` and a clean user-facing error message.
