# Docker Deployment Guide
# دليل النشر باستخدام Docker

## 🐳 ملفات Docker المتوفرة:

1. **Dockerfile** - Python AI Engine
2. **gateway/Dockerfile** - Node.js Gateway
3. **Dockerfile.telegram** - Telegram Bot
4. **docker-compose.full.yml** - جميع الخدمات

---

## 🚀 التشغيل السريع:

### 1. تشغيل جميع الخدمات:
```bash
# انسخ ملف البيئة
cp .env.example .env

# عدّل .env وأضف المفاتيح

# شغّل الكل
docker-compose -f docker-compose.full.yml up -d

# شاهد السجلات
docker-compose -f docker-compose.full.yml logs -f
```

### 2. تشغيل خدمة واحدة:
```bash
# Python AI فقط
docker-compose -f docker-compose.full.yml up -d python-ai

# Telegram Bot فقط
docker-compose -f docker-compose.full.yml up -d telegram-bot
```

### 3. إعادة البناء:
```bash
# إعادة بناء الصور
docker-compose -f docker-compose.full.yml build

# إعادة بناء وتشغيل
docker-compose -f docker-compose.full.yml up -d --build
```

---

## 📦 بناء صورة واحدة:

### Python AI Engine:
```bash
docker build -t top-tier-ai:latest .
docker run -p 3000:3000 --env-file .env top-tier-ai:latest
```

### Node Gateway:
```bash
cd gateway
docker build -t top-tier-gateway:latest .
docker run -p 3001:3001 --env-file ../.env top-tier-gateway:latest
```

### Telegram Bot:
```bash
docker build -t top-tier-telegram:latest -f Dockerfile.telegram .
docker run --env-file .env top-tier-telegram:latest
```

---

## 🔍 إدارة الحاويات:

### عرض الحالة:
```bash
docker-compose -f docker-compose.full.yml ps
```

### السجلات:
```bash
# جميع الخدمات
docker-compose -f docker-compose.full.yml logs -f

# خدمة محددة
docker-compose -f docker-compose.full.yml logs -f python-ai
```

### إيقاف:
```bash
# إيقاف مؤقت
docker-compose -f docker-compose.full.yml stop

# إيقاف وحذف
docker-compose -f docker-compose.full.yml down

# إيقاف وحذف البيانات
docker-compose -f docker-compose.full.yml down -v
```

### الدخول للحاوية:
```bash
docker exec -it python-ai-engine bash
docker exec -it node-gateway sh
docker exec -it telegram-bot bash
```

---

## 🌐 الوصول للخدمات:

| الخدمة | المنفذ | URL |
|--------|--------|-----|
| Python AI | 3000 | http://localhost:3000 |
| Node Gateway | 3001 | http://localhost:3001 |
| Redis | 6379 | redis://localhost:6379 |
| Qdrant | 6333 | http://localhost:6333 |
| Neo4j UI | 7474 | http://localhost:7474 |
| Neo4j Bolt | 7687 | bolt://localhost:7687 |

---

## 📊 المراقبة:

### استخدام الموارد:
```bash
docker stats
```

### فحص الصحة:
```bash
# Python AI
curl http://localhost:3000/health

# Node Gateway
curl http://localhost:3001/health
```

### تنظيف:
```bash
# حذف الصور غير المستخدمة
docker image prune -a

# حذف الحاويات المتوقفة
docker container prune

# حذف كل شيء
docker system prune -a --volumes
```

---

## 🔐 الأمان:

### Best Practices:

1. **لا ترفع .env إلى Git:**
```bash
echo ".env" >> .gitignore
```

2. **استخدم secrets في Production:**
```yaml
# docker-compose.yml
secrets:
  openai_key:
    file: ./secrets/openai_key.txt
```

3. **قيّد الشبكات:**
```yaml
networks:
  ai-network:
    driver: bridge
    internal: true  # لا اتصال خارجي
```

4. **استخدم user غير root:**
```dockerfile
USER node  # في Node.js
USER nobody  # في Python
```

---

## 🚢 النشر على Production:

### 1. Docker Swarm:
```bash
# تهيئة Swarm
docker swarm init

# نشر Stack
docker stack deploy -c docker-compose.full.yml top-tier-ai

# عرض الخدمات
docker service ls

# توسيع خدمة
docker service scale top-tier-ai_python-ai=3
```

### 2. Kubernetes:
```bash
# تحويل إلى Kubernetes manifests
kompose convert -f docker-compose.full.yml

# تطبيق
kubectl apply -f .
```

### 3. Docker Registry:
```bash
# تسجيل الدخول
docker login

# وسم الصورة
docker tag top-tier-ai:latest username/top-tier-ai:v1.0

# رفع
docker push username/top-tier-ai:v1.0
```

---

## 🐛 Troubleshooting:

### مشكلة: الحاوية تتوقف فوراً
```bash
# شاهد السجلات
docker logs python-ai-engine

# تحقق من الخطأ
docker inspect python-ai-engine
```

### مشكلة: Cannot connect to Redis
```bash
# تحقق من الشبكة
docker network inspect top-tier-global-hub-ai_ai-network

# تحقق من Redis
docker exec -it redis-cache redis-cli ping
```

### مشكلة: Port already in use
```bash
# ابحث عن العملية
lsof -i :3000

# غيّر المنفذ في docker-compose.yml
ports:
  - "3002:3000"
```

---

## 📝 ملفات مهمة:

- `Dockerfile` - Python AI
- `gateway/Dockerfile` - Node Gateway
- `Dockerfile.telegram` - Telegram Bot
- `docker-compose.full.yml` - جميع الخدمات
- `.dockerignore` - ملفات لتجاهلها

---

## 🎯 أمثلة سريعة:

### تشغيل فوري:
```bash
# بناء وتشغيل
docker-compose -f docker-compose.full.yml up -d --build

# انتظر 30 ثانية
sleep 30

# اختبر
curl http://localhost:3000/health
curl http://localhost:3001/health
```

### إعادة تشغيل خدمة:
```bash
docker-compose -f docker-compose.full.yml restart python-ai
```

### تحديث صورة:
```bash
docker-compose -f docker-compose.full.yml pull
docker-compose -f docker-compose.full.yml up -d
```

---

**جاهز للتشغيل باستخدام Docker!** 🐳
