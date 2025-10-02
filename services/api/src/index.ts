import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { z } from 'zod';
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider, openaiEmbed } from './providers/openai';

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

/* ---------------- Vector Index & Search (Proxy with Embeddings) ---------------- */
app.post('/v1/index', async (req, res) => {
  try {
    const { id, text } = req.body as { id?: string; text?: string };
    if (!id || !text) return res.status(400).json({ error: 'id and text required' });

    const vec = await openaiEmbed(text);
    const r = await axios.post(`${CORE_URL}/index`, { id, text });
    res.json({ ...r.data, embedding_dim: vec.length });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'index_failed' });
  }
});

app.post('/v1/index/bulk', async (req, res) => {
  try {
    const items = (req.body as { items?: any[] }).items;
    if (!Array.isArray(items)) return res.status(400).json({ error: 'items array required' });

    const enriched = await Promise.all(
      items.map(async (it: any) => {
        const vec = await openaiEmbed(it.text);
        return { ...it, embedding_dim: vec.length };
      })
    );

    const r = await axios.post(`${CORE_URL}/index/bulk`, { items });
    res.json({ ...r.data, enriched });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'index_bulk_failed' });
  }
});

const provider = new OpenAIProvider();

/** ---------------- AI Inference ---------------- */
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

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});
