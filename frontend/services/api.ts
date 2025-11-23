/**
 * API service for communicating with the backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export interface MessageRequest {
  content: string;
  locale: string;
}

export interface MessageResponse {
  id: string;
  content: string;
  locale: string;
  delivered: boolean;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Send a message to the backend API
 */
export async function sendMessage(data: MessageRequest): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE}/api/v1/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Failed to send message');
  }

  return response.json();
}

/**
 * Check the health of the messages API
 */
export async function checkMessagesHealth(): Promise<any> {
  const response = await fetch(`${API_BASE}/api/v1/messages/health`);
  
  if (!response.ok) {
    throw new ApiError(response.status, 'Health check failed');
  }

  return response.json();
}
