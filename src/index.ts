import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios, { AxiosError, isAxiosError } from 'axios';
import { z } from 'zod';

import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.API_PORT ?? 3000);
const CORE_URL = process.env.CORE_URL ?? 'http://localhost:8080';

const http = axios.create({
  baseURL: CORE_URL,
  timeout: 10_000,
});

const ChatMessageSchema = z.object({
  role: z.enum(['system', 'user', 'assistant']),
  content: z.string().min(1),
});

const ChatRequestSchema = z.object({
  messages: z.array(ChatMessageSchema).min(1),
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
});

const InternalInferSchema = z.object({
  input: z.string().min(1),
  metadata: z.record(z.any()).optional(),
});

const ExternalRequestSchema = z.object({
  message: z.string().min(1),
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
});

const UnifiedRequestSchema = ExternalRequestSchema.extend({
  provider: z.enum(['internal', 'openai']).default('openai'),
});

type InternalInferResponse = {
  provider: string;
  model: string;
  response: string;
  metrics: {
    char_count: number;
    word_count: number;
    contains_non_ascii: boolean;
  };
};

const provider = new OpenAIProvider();

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

async function callInternalInfer(input: string): Promise<InternalInferResponse> {
  const { data } = await http.post<InternalInferResponse>('/v1/ai/infer', { input });
  return data;
}

function mapAxiosError(error: unknown): { status: number; body: Record<string, unknown> } {
  if (isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: string } | Record<string, unknown>>;
    const status = axiosError.response?.status ?? 502;
    const payload = axiosError.response?.data;
    if (payload && typeof payload === 'object') {
      return { status, body: payload as Record<string, unknown> };
    }
    return { status, body: { error: axiosError.message } };
  }
  const err = error as Error;
  return { status: 500, body: { error: err.message ?? 'internal_error' } };
}

function buildExternalMessages(message: string): ChatMessage[] {
  const systemPrompt =
    'You are LexCode external AI pipeline. Provide concise, actionable insights rooted in multilingual understanding.';
  return [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: message },
  ];
}

app.post('/v1/ai/infer', async (req, res) => {
  const payload = req.body ?? {};

  if (typeof payload === 'object' && payload !== null && 'messages' in payload) {
    const parsed = ChatRequestSchema.safeParse(payload);
    if (!parsed.success) {
      return res.status(400).json(parsed.error.format());
    }

    try {
      const out = await provider.infer(parsed.data.messages, {
        model: parsed.data.model,
        temperature: parsed.data.temperature,
      });
      res.json({ route: 'external', ...out });
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
    return;
  }

  const parsed = InternalInferSchema.safeParse(payload);
  if (!parsed.success) {
    return res.status(400).json(parsed.error.format());
  }

  try {
    const data = await callInternalInfer(parsed.data.input);
    res.json({ route: 'internal', provider: data.provider, model: data.model, content: data.response, metrics: data.metrics });
  } catch (error) {
    const mapped = mapAxiosError(error);
    res.status(mapped.status).json(mapped.body);
  }
});

app.post('/v1/ai/external', async (req, res) => {
  const parsed = ExternalRequestSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json(parsed.error.format());
  }

  try {
    const out = await provider.infer(buildExternalMessages(parsed.data.message), {
      model: parsed.data.model,
      temperature: parsed.data.temperature,
    });
    res.json({ route: 'external', ...out });
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

app.post('/v1/ai/model', async (req, res) => {
  const parsed = UnifiedRequestSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json(parsed.error.format());
  }

  try {
    if (parsed.data.provider === 'internal') {
      const internal = await callInternalInfer(parsed.data.message);
      return res.json({
        route: 'unified',
        provider: internal.provider,
        model: internal.model,
        content: internal.response,
        metrics: internal.metrics,
      });
    }

    const out = await provider.infer(buildExternalMessages(parsed.data.message), {
      model: parsed.data.model,
      temperature: parsed.data.temperature,
    });
    res.json({ route: 'unified', ...out });
  } catch (error) {
    if (parsed.data.provider === 'internal') {
      const mapped = mapAxiosError(error);
      res.status(mapped.status).json(mapped.body);
      return;
    }
    res.status(500).json({ error: (error as Error).message });
  }
});

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});

export { app };
