# TopTire AI - Vue.js Frontend

## Setup
```bash
npm install
npm run dev
```

Open http://localhost:5173

## Deploy to Railway
```bash
npm run build
npm run preview
```

## Environment Variables
Create a `.env` file with:
```
VITE_API_URL=https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer
```

## Features
- Real-time chat interface with Vue 3 Composition API
- Arabic language support (RTL)
- Responsive design for mobile and desktop
- Connection to Railway-deployed backend
- Error handling and loading states
- Auto-scroll to latest messages
