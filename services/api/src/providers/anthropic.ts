import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const ANTHROPIC_API_KEY = process.env.KEY2 || process.env.ANTHROPIC_API_KEY || '';
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com/v1';

export class AnthropicProvider implements AIProvider {
  async infer(messages: ChatMessage[], opts?: { model?: string; temperature?: number }): Promise<{ content: string }> {
    if (!ANTHROPIC_API_KEY) throw new Error('Missing Anthropic API Key (KEY2 or ANTHROPIC_API_KEY)');
    const model = opts?.model || process.env.ANTHROPIC_MODEL || 'claude-3-opus-20240229';
    const temperature = typeof opts?.temperature === 'number' ? opts!.temperature : 0.2;

    // Anthropic يتوقع رسالة واحدة (user) + system اختياري
    const userContent = messages.filter(m => m.role === 'user').map(m => m.content).join("\n");
    const systemContent = messages.find(m => m.role === 'system')?.content;

    const resp = await axios.post(
      `${ANTHROPIC_BASE_URL}/messages`,
      {
        model,
        temperature,
        max_tokens: 512,
        system: systemContent,
        messages: [{ role: "user", content: userContent }]
      },
      {
        headers: {
          "x-api-key": ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
          "Content-Type": "application/json"
        }
      }
    );

    const content = resp.data?.content?.[0]?.text || '';
    return { content };
  }
}
