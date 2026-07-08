# MedRef Deployment Guide

## Architecture Overview
- **Frontend**: Hosted on Vercel (React + Vite)
- **Backend**: Hosted on Render (FastAPI Web Service)
- **Database**: Hosted on Qdrant Cloud (Managed Vector DB)

## 1. Database (Qdrant Cloud)
1. Create a free cluster on [Qdrant Cloud](https://cloud.qdrant.io/).
2. Obtain your **Cluster URL** and **API Key**.
3. Save these for the Backend configuration.

## 2. Backend (Render)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New > Blueprint**.
3. Connect your repository. Render will automatically read `render.yaml`.
4. In the Render Dashboard, navigate to the Web Service environment variables and fill in:
   - `GROQ_API_KEY`: Your Groq token.
   - `QDRANT_URL`: URL from Step 1.
   - `QDRANT_API_KEY`: API Key from Step 1.
   - `FRONTEND_URL`: (You will set this after deploying the frontend in Step 3).
5. Deploy the backend and copy the Render service URL (e.g., `https://medref-api.onrender.com`).

## 3. Frontend (Vercel)
1. Sign in to [Vercel](https://vercel.com) and click **Add New Project**.
2. Import the GitHub repository.
3. Edit the **Framework Preset** to `Vite`.
4. Edit the **Root Directory** to `frontend`.
5. Add an Environment Variable:
   - `VITE_API_URL`: Paste the Render URL from Step 2 (e.g., `https://medref-api.onrender.com/api/v1`).
6. Deploy the project.

## 4. Finalizing Network Security
1. Copy the deployed Vercel domain (e.g., `https://medref.vercel.app`).
2. Go back to Render -> Dashboard -> Environment Variables.
3. Set `FRONTEND_URL` to your Vercel domain.
4. Restart the Render Web Service to enforce the strict CORS policy.

## Testing Production
Once deployed, test the health check endpoint:
```bash
curl https://medref-api.onrender.com/api/v1/health
```
