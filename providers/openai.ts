/**
 * Comprehensive OpenAI Provider
 * 
 * This is a standalone, comprehensive implementation of OpenAI API integration.
 * Note: This returns `string` directly from infer(), unlike the src/providers/openai.ts
 * which implements AIProvider interface and returns `{ content: string }` for compatibility.
 * 
 * Use this provider when you want direct string responses.
 * Use src/providers/openai.ts when you need AIProvider interface compatibility.
 */
import axios from 'axios';

export type ChatMessage = { 
  role: 'user' | 'assistant' | 'system'; 
  content: string 
};

export interface InferOptions {
  model?: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export class OpenAIProvider {
  private apiKey: string;
  private baseURL: string;
  private defaultModel: string;

  constructor() {
    this.apiKey = process.env.OPENAI_API_KEY || '';
    this.baseURL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';
    this.defaultModel = process.env.OPENAI_MODEL || 'gpt-4o-mini';

    if (!this.apiKey) {
      throw new Error('OPENAI_API_KEY is required but not set');
    }
  }

  async infer(
    messages: ChatMessage[], 
    options?: InferOptions
  ): Promise<string> {
    const model = options?.model || this.defaultModel;
    const temperature = options?.temperature ?? 0.7;
    const max_tokens = options?.max_tokens ?? 1000;

    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model,
          messages,
          temperature,
          max_tokens,
          stream: false,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 60s timeout
        }
      );

      if (!response.data?.choices?.[0]?.message?.content) {
        throw new Error('Invalid response structure from OpenAI API');
      }

      return response.data.choices[0].message.content;
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.error?.message || error.message;
        throw new Error(`OpenAI API Error (${status || 'unknown'}): ${message}`);
      }
      throw error;
    }
  }

  async inferStream(
    messages: ChatMessage[],
    options?: InferOptions,
    onChunk?: (chunk: string) => void
  ): Promise<string> {
    const model = options?.model || this.defaultModel;
    const temperature = options?.temperature ?? 0.7;
    const max_tokens = options?.max_tokens ?? 1000;

    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model,
          messages,
          temperature,
          max_tokens,
          stream: true,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          responseType: 'stream',
          timeout: 60000,
        }
      );

      let fullContent = '';

      return new Promise((resolve, reject) => {
        response.data.on('data', (chunk: Buffer) => {
          const lines = chunk.toString().split('\n').filter(line => line.trim());
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                resolve(fullContent);
                return;
              }
              
              try {
                const parsed = JSON.parse(data);
                const content = parsed.choices?.[0]?.delta?.content;
                if (content) {
                  fullContent += content;
                  onChunk?.(content);
                }
              } catch (e) {
                // Skip invalid JSON chunks from streaming response
                // This is expected as some chunks may be incomplete or metadata
              }
            }
          }
        });

        response.data.on('error', (error: Error) => {
          reject(new Error(`Stream error: ${error.message}`));
        });

        response.data.on('end', () => {
          resolve(fullContent);
        });
      });
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.error?.message || error.message;
        throw new Error(`OpenAI Stream API Error (${status || 'unknown'}): ${message}`);
      }
      throw error;
    }
  }

  isConfigured(): boolean {
    return !!this.apiKey;
  }

  getModel(): string {
    return this.defaultModel;
  }
}

export default OpenAIProvider;
