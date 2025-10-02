import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { z } from 'zod';
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';
import { AnthropicProvider } from './providers/anthropic';
import { HuggingFaceProvider } from './providers/huggingface';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.API_PORT || 3000);
const CORE_URL = process.env.CORE_URL || 'http://localhost:8080';

const openai = new OpenAIProvider();
const anthropic = new AnthropicProvider();
const huggingface = new HuggingFaceProvider();

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

/* ---------------- RAG Query ---------------- */
app.post('/v1/rag/query', async (req, res) => {
  try {
    const body = req.body as {
      query: string;
      provider?: string;
      model?: string;
      temperature?: number;
      top_k?: number;
    };

    if (!body.query) {
      return res.status(400).json({ error: 'query is required' });
    }

    const searchResp = await axios.post(`${CORE_URL}/search`, {
      query: body.query,
      top_k: body.top_k || 3,
    });

    const hits = Array.isArray(searchResp.data?.hits) ? searchResp.data.hits : [];

    const contextText = hits
      .map((h: any) => {
        const score = typeof h?.score === 'number' ? h.score.toFixed(2) : h?.score ?? 'N/A';
        return `Doc ${h?.id ?? 'unknown'} (score ${score})`;
      })
      .join('\n');

    const messages: ChatMessage[] = [
      { role: 'system', content: 'أنت مساعد ذكي يستخدم الوثائق كمرجع للإجابة بدقة.' },
      { role: 'user', content: `السؤال: ${body.query}\n\nالمراجع:\n${contextText}` },
    ];

    const inferOptions = { model: body.model, temperature: body.temperature };

    if (body.provider === 'anthropic') {
      const answer = await anthropic.infer(messages, inferOptions);
      return res.json({ provider: 'anthropic', answer, hits });
    }

    if (body.provider === 'huggingface') {
      const answer = await huggingface.infer(messages, inferOptions);
      return res.json({ provider: 'huggingface', answer, hits });
    }

    const answer = await openai.infer(messages, inferOptions);
    return res.json({ provider: 'openai', answer, hits });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'rag_failed' });
  }
});

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});


/** ---------------- AI Inference ---------------- */
app.post('/v1/ai/infer', async (req, res) => {
  try {
    const body = req.body as { messages: ChatMessage[]; model?: string; temperature?: number };
    if (!body?.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return res.status(400).json({ error: 'messages: ChatMessage[] is required' });
    }
    const out = await openai.infer(body.messages, { model: body.model, temperature: body.temperature });
    res.json({ provider: 'openai', ...out });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'inference_failed' });
  }
});
