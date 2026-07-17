# Stage 1: Build the React application
FROM node:20-slim AS builder

WORKDIR /app

# Copy package descriptors first to leverage Docker caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the project (pass environment variables at build-time if needed)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Serve build assets using Nginx
FROM nginx:alpine

# Copy the built assets to Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
