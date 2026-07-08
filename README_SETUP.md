# MedRef Local Setup Guide

Follow these steps to ensure a fully reproducible local development and benchmarking environment for MedRef.

## Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose**

## 1. Backend Environment
Create and activate a Python virtual environment to isolate dependencies:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

## 2. Environment Variables
Copy the `.env.example` file to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Ensure `GROQ_API_KEY` is populated for LLM generation and evaluation.

## 3. Vector Database (Qdrant)
Start the Qdrant container using Docker Compose:
```bash
docker-compose up -d
```

## 4. Data Ingestion
Ingest the authentic medical corpus (Dense + Sparse vectors) into Qdrant:
```bash
python backend/ingestion/seed_qdrant.py
```

## 5. Run the Application
Start the FastAPI backend:
```bash
# Ensure you are at the root '2.0/' directory
uvicorn backend.app.main:app --reload
```
Start the React frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

## 6. Run Evaluations (Phase 1.5 & 2A Benchmarking)
To run the automated benchmark harness and generate the physical `EVALUATION_REPORT.md`:
```bash
python backend/eval/eval_harness.py
```
