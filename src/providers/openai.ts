import axios, { AxiosError } from 'axios';

import type { AIProvider, ChatMessage, InferenceOptions, InferenceResult } from './ai';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY ?? '';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL ?? 'https://api.openai.com/v1';
const DEFAULT_MODEL = process.env.OPENAI_MODEL ?? 'gpt-4o-mini';

export class OpenAIProvider implements AIProvider {
  public readonly name = 'openai';
  private readonly apiKey = OPENAI_API_KEY;
  private readonly baseUrl = OPENAI_BASE_URL;

  isConfigured(): boolean {
    return Boolean(this.apiKey);
  }

  async infer(messages: ChatMessage[], opts?: InferenceOptions): Promise<InferenceResult> {
    if (!Array.isArray(messages) || messages.length === 0) {
      throw new Error('messages must not be empty');
    }

    const model = opts?.model ?? DEFAULT_MODEL;
    const temperature = typeof opts?.temperature === 'number' ? opts.temperature : 0.2;

    const lastUserMessage = [...messages]
      .reverse()
      .find((message) => message.role === 'user')?.content ?? messages[messages.length - 1]!.content;

    if (!this.isConfigured()) {
      return {
        provider: 'mock-openai',
        model,
        content: `OPENAI_API_KEY not configured. Echo: ${lastUserMessage}`,
        details: {
          reason: 'missing_api_key',
        },
      };
    }

    try {
      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        { model, messages, temperature, stream: false },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        },
      );

      const data = response.data ?? {};
      const choice = data.choices?.[0];
      const content: string = choice?.message?.content ?? '';
      const usedModel = typeof data.model === 'string' ? data.model : model;

      return {
        provider: this.name,
        model: usedModel,
        content,
        details: {
          id: data.id,
          usage: data.usage,
        },
      };
    } catch (error) {
      const err = error as AxiosError<{ error?: { message?: string } }>;
      const message = err.response?.data?.error?.message ?? err.message ?? 'OpenAI request failed';
      throw new Error(message);
    }
  }
}
