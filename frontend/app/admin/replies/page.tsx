'use client';

import { useState } from 'react';
import { useLocale } from '@/hooks/useLocale';
import { sendMessage, ApiError } from '@/services/api';

export default function RepliesConsolePage() {
  const { locale, t } = useLocale();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [lastResponse, setLastResponse] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      return;
    }

    setLoading(true);
    setMessage(null);
    setLastResponse(null);

    try {
      const response = await sendMessage({
        content: content.trim(),
        locale,
      });

      setLastResponse(response);
      setMessage({
        type: 'success',
        text: t.repliesConsole.successMessage,
      });
      setContent('');
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessage({
        type: 'error',
        text: error instanceof ApiError 
          ? error.message 
          : t.repliesConsole.errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {t.repliesConsole.title}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t.repliesConsole.subtitle}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={t.repliesConsole.placeholder}
            className="w-full h-48 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     resize-none"
            disabled={loading}
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading || !content.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium
                     hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                     transition-colors"
          >
            {loading ? t.common.loading : t.repliesConsole.send}
          </button>
        </div>
      </form>

      {/* Status Messages */}
      {message && (
        <div
          className={`mt-6 p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
              : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Response Details */}
      {lastResponse && (
        <div className="mt-6 p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
            Response Details:
          </h3>
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-gray-600 dark:text-gray-400 inline">Message ID:</dt>{' '}
              <dd className="text-gray-900 dark:text-white inline font-mono">
                {lastResponse.id}
              </dd>
            </div>
            <div>
              <dt className="text-gray-600 dark:text-gray-400 inline">Locale:</dt>{' '}
              <dd className="text-gray-900 dark:text-white inline">
                {lastResponse.locale}
              </dd>
            </div>
            <div>
              <dt className="text-gray-600 dark:text-gray-400 inline">Telegram Status:</dt>{' '}
              <dd className={`inline font-medium ${
                lastResponse.delivered 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-yellow-600 dark:text-yellow-400'
              }`}>
                {lastResponse.delivered 
                  ? `✓ ${t.repliesConsole.delivered}`
                  : `⚠ ${t.repliesConsole.notDelivered}`
                }
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
