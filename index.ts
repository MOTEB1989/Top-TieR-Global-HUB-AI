import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { z } from 'zod';
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';

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

/** ---------------- AI Inference ---------------- */
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

/* ---------------- Unified DB SQL (Safe by default) ---------------- */
app.post('/v1/db/sql', async (req, res) => {
  try {
    const body = req.body as {
      db: 'sqlite' | 'postgres' | 'mysql';
      sql: string;
      params?: any[];
      allowWrites?: boolean;
    };
    if (!body?.db || !body?.sql) return res.status(400).json({ error: 'db and sql are required' });

    const isWrite = /\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE)\b/i.test(body.sql);
    const allowWrites = body.allowWrites === true || process.env.ALLOW_WRITE_SQL === 'true';
    if (isWrite && !allowWrites) {
      return res
        .status(403)
        .json({ error: 'Write SQL blocked. Enable allowWrites or ALLOW_WRITE_SQL=true.' });
    }

    const map: Record<string, string> = {
      sqlite: 'http://db_sqlite:5001',
      postgres: 'http://db_postgres:5002',
      mysql: 'http://db_mysql:5004',
    };
    const base = map[body.db];
    if (!base) return res.status(400).json({ error: `Unsupported SQL db: ${body.db}` });

    const r = await axios.post(`${base}/sql`, { sql: body.sql, params: body.params || [] });
    res.json({ db: body.db, rows: r.data.rows, columns: r.data.columns });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'db_sql_failed' });
  }
});

/* ---------------- DB Health Map ---------------- */
app.get('/v1/db/healthmap', async (_req, res) => {
  try {
    const services = {
      sqlite: 'http://db_sqlite:5001/health',
      postgres: 'http://db_postgres:5002/health',
      mongo: 'http://db_mongo:5003/health',
      mysql: 'http://db_mysql:5004/health',
      redis: 'http://db_redis:5005/health',
      neo4j: 'http://db_neo4j:5006/health',
      clickhouse: 'http://db_clickhouse:5007/health',
    };
    const entries = await Promise.all(
      Object.entries(services).map(async ([k, url]) => {
        try {
          const r = await axios.get(url);
          return [k, r.data] as const;
        } catch (e: any) {
          return [k, { error: e?.message }] as const;
        }
      }),
    );
    res.json(Object.fromEntries(entries));
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'healthmap_failed' });
  }
});

/* ---------------- Simple Natural Router ---------------- */
app.post('/v1/db/auto', async (req, res) => {
  try {
    const { ask } = req.body as { ask: string };
    if (!ask) return res.status(400).json({ error: 'ask required' });

    let target: 'sqlite' | 'postgres' | 'mysql' | 'mongo' | 'redis' | 'neo4j' | 'clickhouse' = 'sqlite';
    const t = ask.toLowerCase();
    if (t.includes('postgres')) target = 'postgres';
    else if (t.includes('mysql')) target = 'mysql';
    else if (t.includes('mongo')) target = 'mongo';
    else if (t.includes('redis')) target = 'redis';
    else if (t.includes('neo4j')) target = 'neo4j';
    else if (t.includes('clickhouse')) target = 'clickhouse';

    const sqlMatch = ask.match(/select .*?;/i);
    const gatewayBase = process.env.GATEWAY_BASE_URL || `http://localhost:${PORT}`;
    if (sqlMatch && ['sqlite', 'postgres', 'mysql'].includes(target)) {
      const sql = sqlMatch[0];
      const r = await axios.post(`${gatewayBase}/v1/db/sql`, { db: target, sql });
      return res.json({ routed: target, kind: 'sql', result: r.data });
    }

    const r = await axios.post(`${gatewayBase}/v1/db/query`, { db: target, action: 'health' });
    res.json({ routed: target, kind: 'health', result: r.data });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'auto_failed' });
  }
});

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
