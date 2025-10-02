export type ChatMessage = { role: 'system' | 'user' | 'assistant'; content: string };

export interface AIProvider {
  infer(messages: ChatMessage[], opts?: { model?: string; temperature?: number }): Promise<{ content: string }>;
}
