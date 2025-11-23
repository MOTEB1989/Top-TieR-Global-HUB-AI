FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY *.ts ./
COPY tsconfig.json ./
RUN npm install typescript tsx @types/node @types/express @types/cors --save-dev
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
