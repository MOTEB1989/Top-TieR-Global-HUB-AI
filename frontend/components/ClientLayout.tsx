'use client';

import { useEffect } from 'react';
import { useLocale } from '@/hooks/useLocale';
import Navigation from '@/components/Navigation';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { locale } = useLocale();

  // Update html attributes when locale changes
  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr';
  }, [locale]);

  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-white dark:bg-gray-900">
        {children}
      </main>
    </>
  );
}
