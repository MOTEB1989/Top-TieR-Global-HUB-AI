import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';

/* ---------------- Embeddings ---------------- */
export async function openaiEmbed(input: string, model?: string): Promise<number[]> {
  if (!OPENAI_API_KEY) throw new Error('Missing OPENAI_API_KEY');
  const embedModel = model || process.env.OPENAI_EMBED_MODEL || 'text-embedding-3-small';

  const resp = await axios.post(
    `${OPENAI_BASE_URL}/embeddings`,
    { model: embedModel, input },
    { headers: { Authorization: `Bearer ${OPENAI_API_KEY}`, 'Content-Type': 'application/json' } }
  );

  return resp.data?.data?.[0]?.embedding || [];
}

export class OpenAIProvider implements AIProvider {
  async infer(messages: ChatMessage[], opts?: { model?: string; temperature?: number }): Promise<{ content: string }> {
    if (!OPENAI_API_KEY) throw new Error('Missing OPENAI_API_KEY');
    const model = opts?.model || process.env.OPENAI_MODEL || 'gpt-4o-mini';
    const temperature = typeof opts?.temperature === 'number' ? opts!.temperature : 0.2;

    const resp = await axios.post(
      `${OPENAI_BASE_URL}/chat/completions`,
      { model, messages, temperature, stream: false },
      { headers: { Authorization: `Bearer ${OPENAI_API_KEY}`, 'Content-Type': 'application/json' } }
    );

    const choice = resp.data?.choices?.[0];
    const content = choice?.message?.content ?? '';
    return { content };
  }
}
