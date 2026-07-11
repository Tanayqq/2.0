# Deployment Configuration

## Environment Variables

### Render Environment Variables (Backend)
Configure the following environment variables in your Render backend settings:

- `CORS_ORIGINS`: Defines the allowed origins for CORS.
  - **Value**: `http://localhost:5173,https://medref-pearl.vercel.app`

### Vercel Environment Variables (Frontend)
Configure the following environment variables in your Vercel frontend settings:

- `VITE_API_URL`: Points to the production backend.
  - **Value**: `https://medref-38hx.onrender.com`
