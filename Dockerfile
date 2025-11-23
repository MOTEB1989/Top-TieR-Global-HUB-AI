FROM node:22-alpine
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./

# Install dependencies
RUN npm ci --production=false || npm install

# Copy source files
COPY tsconfig.json ./
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# Verify build output
RUN ls -la dist/ || echo "Warning: dist folder not found"

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["npm", "start"]
# Force rebuild
