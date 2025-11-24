/**
 * Admin Dashboard Page
 * صفحة لوحة التحكم الإدارية
 */
import React, { useState } from 'react';
import Layout from '@/components/Layout';

export default function AdminDashboard() {
  const [stats] = useState({
    totalUsers: 0,
    activeServices: 3,
    apiCalls: 0,
    uptime: '99.9%',
  });

  return (
    <Layout 
      title="Admin Dashboard - Top-TieR Global HUB AI"
      description="Administrative dashboard for system management"
    >
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-1">لوحة التحكم الإدارية</p>
          </div>
          <div className="flex items-center space-x-3">
            {/* TODO: Add language switcher for i18n */}
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              System Online
            </span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.totalUsers}
                </p>
              </div>
              <div className="text-3xl">👥</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active Services</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.activeServices}
                </p>
              </div>
              <div className="text-3xl">⚙️</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">API Calls Today</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.apiCalls}
                </p>
              </div>
              <div className="text-3xl">📊</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Uptime</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.uptime}
                </p>
              </div>
              <div className="text-3xl">🚀</div>
            </div>
          </div>
        </div>

        {/* Services Status */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Services Status</h2>
            <p className="text-gray-600 text-sm">حالة الخدمات</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="font-medium text-gray-900">Backend API</p>
                    <p className="text-sm text-gray-500">FastAPI Service</p>
                  </div>
                </div>
                <span className="text-green-600 font-medium">Running</span>
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="font-medium text-gray-900">Telegram Bot</p>
                    <p className="text-sm text-gray-500">Aiogram Service</p>
                  </div>
                </div>
                <span className="text-green-600 font-medium">Running</span>
              </div>

              <div className="flex items-center justify-between py-3">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="font-medium text-gray-900">Frontend</p>
                    <p className="text-sm text-gray-500">Next.js Service</p>
                  </div>
                </div>
                <span className="text-green-600 font-medium">Running</span>
              </div>
            </div>
          </div>
        </div>

        {/* Future Features Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-2">
            🚧 Under Development / قيد التطوير
          </h3>
          <p className="text-blue-800 mb-3">
            This admin dashboard is a placeholder. Future features will include:
          </p>
          <ul className="list-disc list-inside text-blue-800 space-y-1">
            <li>Real-time monitoring and analytics</li>
            <li>User management and authentication</li>
            <li>API usage statistics and rate limiting controls</li>
            <li>System configuration and environment management</li>
            <li>Database management and migrations</li>
            <li>Error monitoring integration (Sentry)</li>
            <li>WebSocket connection management</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
