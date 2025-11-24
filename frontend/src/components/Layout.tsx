/**
 * Layout Component
 * مكون التخطيط
 */
import React, { ReactNode } from 'react';
import Head from 'next/head';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  title = 'Top-TieR Global HUB AI',
  description = 'OSINT Intelligence Platform - منصة استخبارات OSINT'
}) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary-600">
                  Top-TieR Global HUB AI
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                {/* TODO: Add navigation links and i18n language switcher */}
                <a href="/" className="text-gray-700 hover:text-primary-600 transition">
                  Home
                </a>
                <a href="/admin" className="text-gray-700 hover:text-primary-600 transition">
                  Admin
                </a>
              </div>
            </div>
          </nav>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="text-center text-gray-600">
              <p>
                &copy; {new Date().getFullYear()} Top-TieR Global HUB AI. 
                {/* TODO: Add i18n support for Arabic/English */}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Layout;
