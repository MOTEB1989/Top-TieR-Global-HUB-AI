'use client';

import Link from 'next/link';
import { useLocale } from '@/hooks/useLocale';

export default function Home() {
  const { t } = useLocale();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            {t.common.appName}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            {t.language.arabic === 'العربية' 
              ? 'منصة OSINT مع دعم ثنائي اللغة والسمة الداكنة' 
              : 'OSINT Platform with Bilingual Support and Dark Theme'}
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              🌍 {t.language.arabic === 'العربية' ? 'دعم ثنائي اللغة' : 'Bilingual Support'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {t.language.arabic === 'العربية'
                ? 'التبديل بسلاسة بين اللغة العربية والإنجليزية مع دعم كامل من اليمين إلى اليسار'
                : 'Seamlessly switch between Arabic and English with full RTL support'}
            </p>
          </div>

          <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              🌙 {t.language.arabic === 'العربية' ? 'السمة الداكنة' : 'Dark Theme'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {t.language.arabic === 'العربية'
                ? 'السمة الداكنة الافتراضية مع التبديل السهل بين الوضعين الفاتح والداكن'
                : 'Default dark theme with easy toggle between light and dark modes'}
            </p>
          </div>

          <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              💬 {t.language.arabic === 'العربية' ? 'وحدة الردود' : 'Replies Console'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {t.language.arabic === 'العربية'
                ? 'إرسال الرسائل مباشرة إلى الخادم الخلفي مع التكامل الاختياري مع تيليجرام'
                : 'Send messages directly to the backend with optional Telegram integration'}
            </p>
          </div>

          <div className="p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              🤖 {t.language.arabic === 'العربية' ? 'بوت تيليجرام' : 'Telegram Bot'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {t.language.arabic === 'العربية'
                ? 'بوت تيليجرام بالدعم متعدد اللغات لاستلام الرسائل والأوامر'
                : 'Telegram bot with multilingual support for receiving messages and commands'}
            </p>
          </div>
        </div>

        {/* CTA Button */}
        <div className="text-center">
          <Link
            href="/admin/replies"
            className="inline-block px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold
                     hover:bg-blue-700 transition-colors text-lg"
          >
            {t.nav.repliesConsole} →
          </Link>
        </div>
      </div>
    </div>
  );
}
