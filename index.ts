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
const EXT_MODEL_URL = process.env.EXT_MODEL_URL || 'https://api.external-llm.com/v1/infer';
const EXT_API_KEY = process.env.EXT_API_KEY;

app.get('/v1/health', async (_req, res) => {
  try {
    const r = await axios.get(`${CORE_URL}/health`);
    res.json({ gateway: 'ok', core: r.data });
  } catch (e: any) {
    res.status(500).json({ gateway: 'ok', core: 'down', error: e?.message });
  }
});

const EmbedSchema = z.object({ text: z.string().min(1) });
const ExternalModelSchema = z.object({ input: z.string().min(1) });

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


/** ---------------- AI Inference ---------------- */
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';

const provider = new OpenAIProvider();

app.post('/v1/ai/infer', async (req, res) => {
  try {
    const body = req.body as { messages: ChatMessage[]; model?: string; temperature?: number };
    if (!body?.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return res.status(400).json({ error: 'messages: ChatMessage[] is required' });
    }
    const out = await provider.infer(body.messages, { model: body.model, temperature: body.temperature });
    res.json({ provider: 'openai', ...out });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'inference_failed' });
  }
});

app.post('/v1/ai/other-model', async (req, res) => {
  const parsed = ExternalModelSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.format());

  try {
    const response = await axios.post(
      EXT_MODEL_URL,
      { prompt: parsed.data.input },
      {
        headers: {
          'Content-Type': 'application/json',
          ...(EXT_API_KEY ? { Authorization: `Bearer ${EXT_API_KEY}` } : {}),
        },
      }
    );
    res.json(response.data);
  } catch (e: any) {
    const status = e?.response?.status ?? 500;
    res.status(status).json({ error: e?.message || 'external_inference_failed' });
  }
});
