# TopTire AI - Next.js Frontend

## Setup
```bash
npm install
npm run dev
```

Open http://localhost:3000

## Deploy to Railway
```bash
npm run build
npm start
```

## Environment Variables
Create a `.env.local` file with:
```
NEXT_PUBLIC_API_URL=https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer
```

## Features
- Real-time chat interface
- Arabic language support (RTL)
- Responsive design for mobile and desktop
- Connection to Railway-deployed backend
- Error handling and loading states
