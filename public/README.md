# TopTire AI - Web Interface

## الوصف / Description
واجهة دردشة عربية RTL متكاملة للتفاعل مع TopTire AI API.

A complete Arabic RTL chat interface for interacting with the TopTire AI API.

## الوصول / Access
- **Local Development**: http://localhost:3000/
- **Railway Production**: https://top-tier-global-hub-ai-production.up.railway.app/

## الميزات / Features
- ✅ واجهة دردشة عربية RTL / Arabic RTL chat interface
- ✅ اتصال مباشر بـ API / Direct API connection
- ✅ تصميم متجاوب (موبايل + ديسكتوب) / Responsive design (mobile + desktop)
- ✅ معالجة أخطاء شاملة / Comprehensive error handling
- ✅ تاريخ المحادثة / Conversation history
- ✅ مؤشرات تحميل متحركة / Animated loading indicators

## API Endpoint
- **URL**: `/v1/ai/infer`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "messages": [
      { "role": "user", "content": "Your message here" }
    ],
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }
  ```
- **Response**:
  ```json
  {
    "provider": "openai",
    "content": "AI response here"
  }
  ```

## استكشاف الأخطاء / Troubleshooting

### إذا لم تعمل الواجهة / If the interface doesn't work:

1. **تأكد من أن Railway deployment نجح**
   - Check Railway deployment logs
   - Ensure build completed successfully

2. **تحقق من متغيرات البيئة / Check environment variables**
   - `OPENAI_API_KEY` must be set in Railway Variables
   - Verify API key is valid and has credits

3. **اختبر API مباشرة / Test API directly**
   ```bash
   curl -X POST https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"Hello"}]}'
   ```

4. **تحقق من السجلات / Check logs**
   ```bash
   # View Railway logs
   railway logs
   ```

## التطوير المحلي / Local Development

### Prerequisites
- Node.js 18+
- npm or yarn
- OpenAI API key

### Setup
```bash
# Install dependencies
npm install

# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Run development server
npm run dev

# Or build and run production
npm run build
npm start
```

### Testing the Interface
1. Start the server: `npm run dev`
2. Open browser: http://localhost:3000/
3. Type a message in Arabic or English
4. Click "إرسال" (Send) or press Enter
5. Wait for AI response

## التقنيات المستخدمة / Technologies Used
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Express.js, TypeScript
- **AI Provider**: OpenAI API (GPT-4o-mini)
- **Styling**: Custom CSS with RTL support
- **Animations**: CSS keyframes

## الأمان / Security
- No credentials stored in frontend code
- API calls made through backend proxy
- CORS enabled for secure cross-origin requests
- Input sanitization on backend

## المساهمة / Contributing
To improve the interface:
1. Fork the repository
2. Make changes to `public/index.html`
3. Test locally
4. Submit a pull request

## الدعم / Support
For issues or questions:
- Open an issue on GitHub
- Contact: @MOTEB1989
- Check Railway logs for server errors

## الإصدار / Version
- v1.0.0 - Initial release with Arabic RTL interface

## الترخيص / License
Part of Top-TieR-Global-HUB-AI project.
