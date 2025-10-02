import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import client from 'prom-client';
import { z } from 'zod';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.API_PORT || 3000);
const CORE_URL = process.env.CORE_URL || 'http://localhost:8080';
let embedder: unknown = null;

const registry = new client.Registry();
client.collectDefaultMetrics({ register: registry });

const httpReqs = new client.Counter({
  name: 'gw_http_requests_total',
  help: 'HTTP requests',
  labelNames: ['route', 'method', 'status'],
});

registry.registerMetric(httpReqs);

app.use((req, res, next) => {
  const originalEnd = res.end;
  res.end = function (...args: any[]) {
    httpReqs.inc({ route: req.path, method: req.method, status: String(res.statusCode) });
    // @ts-ignore - express typings don't like rest args passthrough
    return originalEnd.apply(this, args);
  } as typeof res.end;
  next();
});

app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', registry.contentType);
  res.end(await registry.metrics());
});

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

app.post('/v1/kb/reload', (_req, res) => {
  embedder = null;
  res.json({ ok: true, reloaded: true });
});

app.post('/v1/kb/search_os', async (req, res) => {
  const query = typeof req.body?.query === 'string' ? req.body.query.trim() : '';
  if (!query) {
    return res.status(400).json({ error: 'query is required' });
  }
  try {
    const response = await axios.post('http://opensearch:9200/lexcode_kb/_search', {
      query: { match: { text: query } },
      size: 5,
    });
    res.json(response.data);
  } catch (error: any) {
    res.status(502).json({ error: error?.message || 'opensearch_error' });
  }
});

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});


/** ---------------- AI Inference ---------------- */
import type { ChatMessage } from './ai';
import { OpenAIProvider } from './openai';

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
