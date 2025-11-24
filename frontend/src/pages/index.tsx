/**
 * Home Page - Landing Page
 * الصفحة الرئيسية - صفحة الهبوط
 */
import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { apiService } from '@/services/api';

interface HealthStatus {
  status: string;
  service: string;
  environment: string;
  version: string;
}

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealthStatus();
  }, []);

  const fetchHealthStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.checkHealth();
      setHealthStatus(data);
    } catch (err: any) {
      console.error('Failed to fetch health status:', err);
      setError(err.message || 'Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout 
      title="Top-TieR Global HUB AI - Home"
      description="OSINT Intelligence Platform"
    >
      <div className="space-y-8">
        {/* Hero Section */}
        <section className="text-center py-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Top-TieR Global HUB AI
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            منصة استخبارات OSINT المتقدمة
          </p>
          <p className="text-xl text-gray-600">
            Advanced OSINT Intelligence Platform
          </p>
        </section>

        {/* Health Status Card */}
        <section className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center justify-between">
              <span>System Status</span>
              <span className="text-base font-normal text-gray-600">حالة النظام</span>
            </h2>

            {loading && (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <p className="mt-4 text-gray-600">Loading... جاري التحميل</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700">❌ {error}</p>
                <button
                  onClick={fetchHealthStatus}
                  className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
                >
                  Retry / إعادة المحاولة
                </button>
              </div>
            )}

            {healthStatus && !loading && !error && (
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-semibold ${
                    healthStatus.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {healthStatus.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
                  </span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-600">Service:</span>
                  <span className="font-semibold">{healthStatus.service}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-600">Environment:</span>
                  <span className="font-semibold">{healthStatus.environment}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Version:</span>
                  <span className="font-semibold">{healthStatus.version}</span>
                </div>
                <button
                  onClick={fetchHealthStatus}
                  className="w-full mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition"
                >
                  Refresh / تحديث
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Features Section */}
        <section className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Telegram Bot</h3>
            <p className="text-gray-600">
              Interact with the platform through Telegram
            </p>
            <p className="text-gray-600 text-sm mt-1">
              تفاعل مع المنصة عبر تيليجرام
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">FastAPI Backend</h3>
            <p className="text-gray-600">
              High-performance API with async capabilities
            </p>
            <p className="text-gray-600 text-sm mt-1">
              واجهة برمجية عالية الأداء
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Modern UI</h3>
            <p className="text-gray-600">
              Next.js with TypeScript and Tailwind CSS
            </p>
            <p className="text-gray-600 text-sm mt-1">
              واجهة مستخدم عصرية
            </p>
          </div>
        </section>
      </div>
    </Layout>
  );
}
