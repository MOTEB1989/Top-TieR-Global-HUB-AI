export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };

export type InferenceOptions = {
  model?: string;
  temperature?: number;
};

export type InferenceResult = {
  provider: string;
  model: string;
  content: string;
  details?: Record<string, unknown>;
};

export interface AIProvider {
  readonly name: string;
  infer(messages: ChatMessage[], opts?: InferenceOptions): Promise<InferenceResult>;
  isConfigured(): boolean;
}
