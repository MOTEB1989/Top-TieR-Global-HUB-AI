import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { z } from 'zod';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.API_PORT || 3000);
const CORE_URL = process.env.CORE_URL || 'http://localhost:8080';

app.get('/v1/health', async (_req, res) => {
  try {
    const r = await axios.get(`${CORE_URL}/health`);
    res.json({ gateway: 'ok', core: r.data });
  } catch (e: any) {
    res.status(500).json({ gateway: 'ok', core: 'down', error: e?.message });
  }
});

const EmbedSchema = z.object({ text: z.string().min(1) });

app.post('/v1/embed', async (req, res) => {
  const parsed = EmbedSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.format());
  try {
    const r = await axios.post(`${CORE_URL}/embed`, parsed.data);
    res.json(r.data);
  } catch (e: any) {
    res.status(500).json({ error: e?.message });
  }
});

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});

/* ---------------- AI Inference (Multi-Provider) ---------------- */
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';
import { AnthropicProvider } from './providers/anthropic';

const openai = new OpenAIProvider();
const anthropic = new AnthropicProvider();

app.post('/v1/ai/infer', async (req, res) => {
  try {
    const body = req.body as { messages: ChatMessage[]; model?: string; temperature?: number; provider?: string };
    if (!body?.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return res.status(400).json({ error: 'messages: ChatMessage[] is required' });
    }

    let out;
    if (body.provider === 'anthropic') {
      out = await anthropic.infer(body.messages, { model: body.model, temperature: body.temperature });
      res.json({ provider: 'anthropic', ...out });
    } else {
      out = await openai.infer(body.messages, { model: body.model, temperature: body.temperature });
      res.json({ provider: 'openai', ...out });
    }

  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'inference_failed' });
  }
});

export default app;
