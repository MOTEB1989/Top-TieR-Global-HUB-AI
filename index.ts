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

/* ---------------- Unified DB Query ---------------- */
app.post('/v1/db/query', async (req, res) => {
  try {
    const body = req.body as {
      db: string;          // "sqlite" | "postgres" | "mongo" | "mysql" | "redis" | "neo4j" | "clickhouse"
      action?: string;     // نوع العملية (مثل health, get, set, query)
      payload?: any;       // البيانات المطلوب تمريرها
    };

    if (!body.db) return res.status(400).json({ error: "db field required" });

    const map: Record<string, string> = {
      sqlite: "http://db_sqlite:5001",
      postgres: "http://db_postgres:5002",
      mongo: "http://db_mongo:5003",
      mysql: "http://db_mysql:5004",
      redis: "http://db_redis:5005",
      neo4j: "http://db_neo4j:5006",
      clickhouse: "http://db_clickhouse:5007"
    };

    const baseUrl = map[body.db];
    if (!baseUrl) return res.status(400).json({ error: `Unsupported db: ${body.db}` });

    // افتراضي: health
    const action = body.action || "health";

    // نقرر URL حسب نوع الـ action
    let url = `${baseUrl}/${action}`;
    let method = "get";
    let data: any = undefined;

    if (["set", "add", "documents", "query"].includes(action)) {
      method = "post";
      data = body.payload || {};
    }

    const r = await axios({ method, url, data });
    res.json({ db: body.db, response: r.data });

  } catch (e: any) {
    res.status(500).json({ error: e?.message || "db_query_failed" });
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
