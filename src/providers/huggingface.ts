import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const HF_TOKEN = process.env.HUGGINGFACE_API_KEY || process.env.HF_TOKEN || '';
const HF_BASE_URL = process.env.HUGGINGFACE_BASE_URL || 'https://api-inference.huggingface.co';
const HF_MODEL = process.env.HUGGINGFACE_MODEL || 'mistralai/Mistral-7B-Instruct-v0.2';

export class HuggingFaceProvider implements AIProvider {
  async infer(
    messages: ChatMessage[],
    opts?: { model?: string; temperature?: number }
  ): Promise<{ content: string }> {
    if (!HF_TOKEN) throw new Error('Missing HUGGINGFACE_API_KEY');

    const model = opts?.model || HF_MODEL;
    const temperature = typeof opts?.temperature === 'number' ? opts.temperature : 0.2;

    const prompt = messages
      .map((m) => `${m.role.toUpperCase()}: ${m.content}`)
      .join('\n');

    const response = await axios.post(
      `${HF_BASE_URL}/models/${model}`,
      { inputs: prompt, parameters: { temperature } },
      {
        headers: {
          Authorization: `Bearer ${HF_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );

    const data = Array.isArray(response.data) ? response.data[0] : response.data;
    const content = data?.generated_text ?? data?.choices?.[0]?.text ?? '';
    return { content };
  }
}
