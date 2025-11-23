/**
 * API Service for communicating with backend
 * خدمة API للتواصل مع الخلفية
 */
import axios, { AxiosInstance } from 'axios';

// API Base URL - should be set via environment variable in production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 
  (process.env.NODE_ENV === 'production' 
    ? (() => { throw new Error('NEXT_PUBLIC_API_BASE must be set in production') })()
    : 'http://localhost:8000');

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth tokens (future)
    this.client.interceptors.request.use(
      (config) => {
        // TODO: Add authentication token from localStorage/cookies
        // const token = localStorage.getItem('token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Health check endpoint
   * نقطة فحص الصحة
   */
  async checkHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Get examples (demo endpoint)
   * الحصول على أمثلة (نقطة نهاية تجريبية)
   */
  async getExamples() {
    const response = await this.client.get('/api/v1/examples');
    return response.data;
  }

  /**
   * Get example by ID
   * الحصول على مثال بالمعرف
   */
  async getExample(id: number) {
    const response = await this.client.get(`/api/v1/examples/${id}`);
    return response.data;
  }

  /**
   * Create example
   * إنشاء مثال
   */
  async createExample(data: any) {
    const response = await this.client.post('/api/v1/examples', data);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
