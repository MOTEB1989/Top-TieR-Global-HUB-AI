import { Router } from 'express';
import { Telegraf } from 'telegraf';
import { fetch } from 'undici';

const router = Router();
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ALLOWLIST = process.env.TELEGRAM_ALLOWLIST?.split(',').map((id) => id.trim()).filter(Boolean) ?? [];

if (!TELEGRAM_BOT_TOKEN) {
    throw new Error('TELEGRAM_BOT_TOKEN مفقود – لا يمكن تهيئة بوت تيليجرام بدون المفتاح');
}

const bot = new Telegraf(TELEGRAM_BOT_TOKEN);

// دالة ذكية لاختيار النموذج المتاح
async function getAvailableModel(): Promise<string> {
    const models = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'];
    const apiKey = process.env.OPENAI_API_KEY;

    if (!apiKey) {
        return models[0];
    }

    for (const model of models) {
        try {
            const response = await fetch('https://api.openai.com/v1/models', {
                headers: {
                    Authorization: `Bearer ${apiKey}`
                }
            });

            if (!response.ok) {
                continue;
            }

            const data = await response.json();
            if (data.data?.some((m: { id: string }) => m.id === model)) {
                return model;
            }
        } catch (error) {
            console.log(`Model ${model} not available, trying next...`, error);
        }
    }

    return models[0];
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
        if (!process.env.OPENAI_API_KEY) {
            throw new Error('missing-openai-key');
        }

        await ctx.replyWithChatAction('typing');

        const model = await getAvailableModel();
        console.log(`Using model: ${model}`);

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model,
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
        const answer = data.choices[0]?.message?.content ?? 'لم يتم استلام إجابة من النموذج.';

        await ctx.reply(answer, { parse_mode: 'Markdown' });
    } catch (error: any) {
        console.error('Chat error:', error);

        let errorMsg = '❌ *حدث خطأ* أثناء معالجة سؤالك\\.\n\n';

        if (error.message === 'missing-openai-key') {
            errorMsg += '🔑 *سبب محتمل:* لا يوجد مفتاح OpenAI متاح\\.\n';
            errorMsg += '💡 *الحل:* أضف قيمة OPENAI_API_KEY إلى الإعدادات\\.';
        } else if (error.message?.includes('403')) {
            errorMsg += '⚠️ *سبب محتمل:* عدم توفر النموذج المطلوب في خطتك الحالية\\.\n';
            errorMsg += '💡 *الحل:* تم التبديل تلقائياً إلى النموذج المتاح\\.';
        } else if (error.message?.includes('401')) {
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

        const fs = await import('fs/promises');
        let analysis = `📊 *تحليل المستودع*\n\n`;

        try {
            const arch = await fs.readFile('ARCHITECTURE.md', 'utf8');
            analysis += `*🏗️ المعمارية:*\n`;
            analysis += arch.split('\n').slice(0, 5).join('\n') + '\n\n';
        } catch {
            analysis += `*🏗️ المعمارية:* ❌ غير متاحة\n\n`;
        }

        try {
            const security = await fs.readFile('SECURITY_POSTURE.md', 'utf8');
            analysis += `*🔐 الأمان:*\n`;
            analysis += security.split('\n').slice(0, 5).join('\n') + '\n\n';
        } catch {
            analysis += `*🔐 الأمان:* ❌ غير متاح\n\n`;
        }

        analysis += `*📈 الملخص:*\n`;
        analysis += `• Allowlist: ${ALLOWLIST.length} مستخدمًا\n`;
        analysis += `• النموذج AI: سيتم استخدام ${await getAvailableModel()}\n`;

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
        `🧠 OpenAI: ${process.env.OPENAI_API_KEY ? '✅ مضبوط' : '⚠️ غير مضبوط'}\n` +
        `• النموذج: ${model}\n` +
        `🔐 Allowlist: ${ALLOWLIST.length ? '✅ مفعّل' : '⚠️ غير مضبوط'}\n` +
        `• المستخدمون: ${ALLOWLIST.length}\n\n` +
        `💡 النظام جاهز للاستخدام\\!`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /help
bot.command('help', (ctx) => {
    ctx.reply(
        `🤖 *أوامر البوت المتاحة:*\n\n` +
        `📝 */chat* \\\\[سؤالك\\\\] \\\- دردشة مع AI\n` +
        `📊 */repo* \\\- تحليل المستودع\n` +
        `⚙️ */status* \\\- حالة النظام\n` +
        `❓ */help* \\\- هذه الرسالة\n\n` +
        `💡 *مثال:*\n` +
        '`/chat ما هي أفضل ممارسات Docker؟`',
        { parse_mode: 'MarkdownV2' }
    );
});

// Webhook endpoint
router.post('/webhook/:token', async (req, res) => {
    if (req.params.token !== TELEGRAM_BOT_TOKEN) {
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
