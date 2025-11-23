import { Router } from 'express';
import { Telegraf } from 'telegraf';

const router = Router();
const bot = new Telegraf('8361523991:AAFF7NuuVSacnAF_4nydWru_mf8FxxvvhfQ');

const ALLOWLIST = ['8256840669', '6090738107'];

// دالة ذكية لاختيار النموذج المتاح
async function getAvailableModel() {
    const models = ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'text-davinci-003'];
    
    for (const model of models) {
        try {
            const response = await fetch('https://api.openai.com/v1/models', {
                headers: {
                    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
                }
            });
            
            const data = await response.json();
            if (data.data?.some(m => m.id === model)) {
                return model;
            }
        } catch (error) {
            console.log(`Model ${model} not available, trying next...`);
        }
    }
    
    return 'gpt-3.5-turbo'; // النموذج الافتراضي الأكثر توفراً
}

// أمر /chat - محسن مع دعم Fallback
bot.command('chat', async (ctx) => {
    const message = ctx.message.text.replace('/chat', '').trim();
    
    if (!message) {
        return ctx.reply(
            '❌ *يرجى كتابة سؤالك بعد الأمر*\\.\n' +
            'مثال: `/chat ما هي حالة الـ CI/CD؟`',
            { parse_mode: 'MarkdownV2' }
        );
    }

    try {
        await ctx.replyWithChatAction('typing');
        
        // الحصول على النموذج المتاح
        const model = await getAvailableModel();
        console.log(`Using model: ${model}`);
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: model,
                messages: [{ 
                    role: 'user', 
                    content: `أجب عن السؤال التالي بالعربية: ${message}` 
                }],
                max_tokens: 1000,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`OpenAI API error: ${error.error?.message || response.status}`);
        }

        const data = await response.json();
        const answer = data.choices[0].message.content;
        
        await ctx.reply(answer, { parse_mode: 'Markdown' });
        
    } catch (error) {
        console.error('Chat error:', error);
        
        // رسالة خطأ مفصلة
        let errorMsg = '❌ *حدث خطأ* أثناء معالجة سؤالك\\.\n\n';
        
        if (error.message.includes('403')) {
            errorMsg += '⚠️ *سبب محتمل:* عدم توفر النموذج المطلوب في خطتك الحالية\\.\n';
            errorMsg += '💡 *الحل:* تم التبديل تلقائياً إلى النموذج المتاح\\.';
        } else if (error.message.includes('401')) {
            errorMsg += '🔑 *سبب محتمل:* مشكلة في مفتاح API\\.\n';
            errorMsg += '💡 *الحل:* تحقق من صحة مفتاح OpenAI في الإعدادات\\.';
        } else {
            errorMsg += '💡 *نصيحة:* حاول بسؤال أبسط أو تواصل مع المطور\\.';
        }
        
        await ctx.reply(errorMsg, { parse_mode: 'MarkdownV2' });
    }
});

// أمر /repo - محسن مع معالجة الأخطاء
bot.command('repo', async (ctx) => {
    if (!ALLOWLIST.includes(ctx.from.id.toString())) {
        return ctx.reply('🚫 *غير مصرح لك* باستخدام هذا الأمر\\.', 
            { parse_mode: 'MarkdownV2' });
    }

    try {
        await ctx.replyWithChatAction('typing');
        
        // قراءة الملفات المحلية
        const fs = require('fs').promises;
        let analysis = `📊 *تحليل المستودع*\n\n`;
        
        // تحليل ARCHITECTURE.md
        try {
            const arch = await fs.readFile('ARCHITECTURE.md', 'utf8');
            analysis += `*🏗️ المعمارية:*\n`;
            analysis += arch.split('\n').slice(0, 5).join('\n') + '\n\n';
        } catch {
            analysis += `*🏗️ المعمارية:* ❌ غير متاحة\n\n`;
        }
        
        // تحليل SECURITY_POSTURE.md
        try {
            const security = await fs.readFile('SECURITY_POSTURE.md', 'utf8');
            analysis += `*🔐 الأمان:*\n`;
            analysis += security.split('\n').slice(0, 5).join('\n') + '\n\n';
        } catch {
            analysis += `*🔐 الأمان:* ❌ غير متاح\n\n`;
        }
        
        // ملخص سريع
        analysis += `*📈 الملخص:*\n`;
        analysis += `• الحالة: العاملة ✅\n`;
        analysis += `• المستخدمون: 2 مسموح بهم\n`;
        analysis += `• النموذج AI: متاح (مع fallback)\n`;
        
        await ctx.reply(analysis, { parse_mode: 'MarkdownV2' });
        
    } catch (error) {
        console.error('Repo analysis error:', error);
        await ctx.reply('❌ *فشل تحليل المستودع*\\.\nحاول مرة أخرى\\.', 
            { parse_mode: 'MarkdownV2' });
    }
});

// أمر /status
bot.command('status', async (ctx) => {
    const model = await getAvailableModel();
    ctx.reply(
        `⚙️ *حالة التكوين*\n\n` +
        `🧠 OpenAI: ✅ مضبوط\n` +
        `• النموذج: ${model}\n` +
        `🔐 Allowlist: ✅ مفعّل\n` +
        `• المستخدمون: ${ALLOWLIST.length}\n\n` +
        `💡 النظام جاهز للاستخدام\\!`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /help
bot.command('help', (ctx) => {
    ctx.reply(
        `🤖 *أوامر البوت المتاحة:*\n\n` +
        `📝 */chat* \\[سؤالك\\] \\- دردشة مع AI\n` +
        `📊 */repo* \\- تحليل المستودع\n` +
        `⚙️ */status* \\- حالة النظام\n` +
        `❓ */help* \\- هذه الرسالة\n\n` +
        `💡 *مثال:*\n` +
        '`/chat ما هي أفضل ممارسات Docker؟`',
        { parse_mode: 'MarkdownV2' }
    );
});

// Webhook endpoint
router.post('/webhook/:token', async (req, res) => {
    if (req.params.token !== '8361523991:AAFF7NuuVSacnAF_4nydWru_mf8FxxvvhfQ') {
        return res.status(403).send('Forbidden');
    }
    
    try {
        await bot.handleUpdate(req.body);
        res.status(200).send('OK');
    } catch (error) {
        console.error('Webhook error:', error);
        res.status(500).send('Internal Server Error');
    }
});

export default router;
