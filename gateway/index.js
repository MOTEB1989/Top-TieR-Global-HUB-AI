import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Render يوفر PORT تلقائياً
// API_PORT نستخدمه فقط محلياً
const PORT = process.env.PORT || process.env.API_PORT || 3000;

app.use(express.json());

// اختبار سريع
app.get("/", (req, res) => {
  res.json({
    status: "ok",
    message: "API Gateway running",
    port: PORT,
    render_detected: !!process.env.PORT
  });
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API status endpoint
app.get("/api/status", (req, res) => {
  res.json({
    api: "Top-TieR Global HUB AI",
    version: "1.0.0",
    environment: process.env.NODE_ENV || "development",
    services: {
      gateway: "online",
      render: !!process.env.PORT
    }
  });
});

// تشغيل السيرفر
app.listen(PORT, () => {
  console.log(`🚀 API Gateway listening on port ${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`☁️  Render detected: ${!!process.env.PORT}`);
});
