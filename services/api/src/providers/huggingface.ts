import axios from 'axios';
import type { AIProvider, ChatMessage } from './ai';

const HF_TOKEN = process.env.HF_TOKEN || '';
const HF_BASE_URL = process.env.HF_BASE_URL || 'https://api-inference.huggingface.co/models';

export class HuggingFaceProvider implements AIProvider {
  async infer(messages: ChatMessage[], opts?: { model?: string; temperature?: number }): Promise<{ content: string }> {
    if (!HF_TOKEN) throw new Error('Missing HF_TOKEN (Hugging Face API Key)');
    const model = opts?.model || process.env.HF_MODEL || 'gpt2';

    // دمج الرسائل في نص واحد (HF لا يدعم محادثة مباشرة)
    const input = messages.map(m => `${m.role.toUpperCase()}: ${m.content}`).join("\n");

    const resp = await axios.post(
      `${HF_BASE_URL}/${model}`,
      { inputs: input, parameters: { temperature: opts?.temperature ?? 0.7, max_new_tokens: 128 } },
      { headers: { Authorization: `Bearer ${HF_TOKEN}`, 'Content-Type': 'application/json' } }
    );

    let content = '';
    if (Array.isArray(resp.data)) {
      // بعض النماذج ترجع array من النصوص
      content = resp.data[0]?.generated_text || '';
    } else if (resp.data?.generated_text) {
      content = resp.data.generated_text;
    } else {
      content = JSON.stringify(resp.data);
    }

    return { content };
  }
}

