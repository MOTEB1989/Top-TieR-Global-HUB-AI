'use client';

import Link from 'next/link';
import { useLocale } from '@/hooks/useLocale';
import { useTheme } from '@/hooks/useTheme';

export default function Navigation() {
  const { locale, setLocale, t } = useLocale();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="bg-gray-100 dark:bg-gray-800 shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo/Brand */}
          <Link href="/" className="text-xl font-bold text-gray-800 dark:text-white">
            {t.common.appName}
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
            >
              {t.nav.home}
            </Link>
            <Link
              href="/admin/replies"
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
            >
              {t.nav.repliesConsole}
            </Link>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              aria-label={t.theme.toggle}
              title={t.theme.toggle}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            {/* Language Toggle */}
            <button
              onClick={() => setLocale(locale === 'en' ? 'ar' : 'en')}
              className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium"
              aria-label={t.language.toggle}
            >
              {locale === 'en' ? 'ع' : 'EN'}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
