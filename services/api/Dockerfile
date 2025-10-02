FROM node:20-alpine AS base
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app

COPY --from=base /app/package*.json ./
RUN npm install --omit=dev

COPY --from=base /app/dist ./dist

ENV PORT=3000
EXPOSE 3000
CMD ["node", "dist/index.js"]
