import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_KEY || '';
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com/v1';
const ANTHROPIC_VERSION = process.env.ANTHROPIC_VERSION || '2023-06-01';

export class AnthropicProvider implements AIProvider {
  async infer(messages: ChatMessage[], opts?: { model?: string; temperature?: number }): Promise<{ content: string }> {
    if (!ANTHROPIC_API_KEY) throw new Error('Missing ANTHROPIC_API_KEY');

    const model = opts?.model || process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20240620';
    const temperature = typeof opts?.temperature === 'number' ? opts.temperature : 0.5;

    const systemPrompt = messages
      .filter(m => m.role === 'system')
      .map(m => m.content)
      .join('\n');

    const conversation = messages
      .filter(m => m.role !== 'system')
      .map(m => ({
        role: m.role === 'assistant' ? 'assistant' : 'user',
        content: [{ type: 'text', text: m.content }],
      }));

    const resp = await axios.post(
      `${ANTHROPIC_BASE_URL}/messages`,
      {
        model,
        max_tokens: 1024,
        temperature,
        system: systemPrompt || undefined,
        messages: conversation,
      },
      {
        headers: {
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': ANTHROPIC_VERSION,
          'content-type': 'application/json',
        },
      }
    );

    const parts = Array.isArray(resp.data?.content) ? resp.data.content : [];
    const content = parts.map((p: any) => p?.text ?? '').join('').trim();

    return { content };
  }
}
