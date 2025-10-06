FROM node:24-alpine
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm install || true
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
