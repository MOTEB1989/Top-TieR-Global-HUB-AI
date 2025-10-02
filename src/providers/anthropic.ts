import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || process.env.KEY2 || '';
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com/v1';
const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL || 'claude-3-haiku-20240307';

export class AnthropicProvider implements AIProvider {
  async infer(
    messages: ChatMessage[],
    opts?: { model?: string; temperature?: number }
  ): Promise<{ content: string }> {
    if (!ANTHROPIC_API_KEY) throw new Error('Missing ANTHROPIC_API_KEY');

    const model = opts?.model || ANTHROPIC_MODEL;
    const temperature = typeof opts?.temperature === 'number' ? opts.temperature : 0.2;

    const payload = {
      model,
      max_tokens: 1024,
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      temperature,
    };

    const response = await axios.post(`${ANTHROPIC_BASE_URL}/messages`, payload, {
      headers: {
        'content-type': 'application/json',
        'anthropic-version': '2023-06-01',
        'x-api-key': ANTHROPIC_API_KEY,
      },
    });

    const content = response.data?.content?.[0]?.text ?? '';
    return { content };
  }
}
