# syntax=docker/dockerfile:1

# Builder stage: install dependencies and compile TypeScript
FROM node:20-alpine AS deps
WORKDIR /app

# Copy only dependency manifests to leverage Docker cache
COPY package*.json pnpm-lock.yaml* yarn.lock* ./
RUN npm ci --ignore-scripts

# Build stage: copy source and run the build
FROM deps AS builder
# Copy application source (see .dockerignore for exclusions)
COPY . .
RUN npm run build

# Runtime stage: minimal footprint image
FROM node:20-alpine AS runner
ENV NODE_ENV=production
WORKDIR /app

# Create non-root user for better security
USER node

# Install production dependencies only
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force

# Copy compiled application artifacts
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# Basic healthcheck to ensure the server responds
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start the application
CMD ["node", "dist/index.js"]
