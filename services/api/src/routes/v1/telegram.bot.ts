import { Router } from 'express';
import { Telegraf, Context, Markup } from 'telegraf';

const router = Router();
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN!);

// قائمة النماذج (LexNexus هو القائد)
const MODELS = {
    leader: process.env.CUSTOM_GPT_ID!,
    sub_models: {
        'Saudi-Nexus': 'g-68d85ae6a19881919a7699aede6f6366',
        'Saudi-Banks': 'g-68d83741405881918336c921a412c7c4'
    }
};

// قائمة المستخدمين المصرح لهم
const ALLOWLIST = process.env.TELEGRAM_ALLOWLIST?.split(',') || [];

// دالة للتحقق من الصلاحيات
const isAdmin = (ctx: Context) => {
    const userId = ctx.from?.id.toString();
    return userId && ALLOWLIST.includes(userId);
};

// دالة لاستدعاء GPT (مع routing ذكي)
async function callGPT(model: string, prompt: string) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 1000
        })
    });

    const data = await response.json();
    return data.choices?.[0]?.message?.content || '⚠️ لم يتم الحصول على رد من النموذج.';
}

// ==================== BOT COMMANDS ====================

// أمر /start
bot.start((ctx) => {
    const userId = ctx.from?.id.toString();
    const username = ctx.from?.username || 'غير محدد';

    ctx.reply(
        `🤖 *مرحباً إلى LexNexus AI Bot*\n\n` +
        `👤 معرفك: \\\`${userId}\\\`\n` +
        `🔖 اسم المستخدم: @${username}\n` +
        `🔐 الصلاحيات: ${isAdmin(ctx) ? '*مشرف* ✅' : 'مستخدم عادي'}\n\n` +
        `*🏆 LexNexus القائد* هو الذكاء الاصطناعي الرئيسي\n` +
        `*النماذج المتاحة:*\n` +
        `• 🇸🇦 Saudi-Nexus (التحقق والأمن)\n` +
        `• 🏦 Saudi-Banks (الخدمات المصرفية)\n` +
        `• 🤖 LexNexus (القائد - المختار تلقائياً)\n\n` +
        `*الأوامر:*\n` +
        `• /model - اختيار نموذج محدد\n` +
        `• /chat <سؤال> - سؤال LexNexus\n` +
        `• /ask <نموذج> <سؤال> - سؤال نموذج محدد\n` +
        `• /status - حالة النماذج\n` +
        `• /leader - معلومات LexNexus\n` +
        `• /help - المساعدة`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /leader - معلومات LexNexus
bot.command('leader', (ctx) => {
    ctx.reply(
        `🏆 *LexNexus Leader System*\n\n` +
        `🆔 المعرف: \\\`${MODELS.leader}\\\`\n` +
        `📊 الوضع: *ACTIVE*\n` +
        `🎛️ التحكم: النموذج الرئيسي للأنظمة\n` +
        `🔗 النماذج الفرعية: ${Object.keys(MODELS.sub_models).join(', ')}`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /model - اختيار نموذج محدد
bot.command('model', async (ctx) => {
    if (!isAdmin(ctx)) {
        return ctx.reply('🚫 هذا الأمر للمشرفين فقط');
    }

    const keyboard = Markup.inlineKeyboard([
        [Markup.button.callback('🇸🇦 Saudi-Nexus', 'model_saudi_nexus')],
        [Markup.button.callback('🏦 Saudi-Banks', 'model_saudi_banks')],
        [Markup.button.callback('🤖 LexNexus (Leader)', 'model_lexnexus')]
    ]);

    ctx.reply('اختر نموذجاً للاستخدام:', keyboard);
});

// Callback handlers للأزرار
bot.action('model_saudi_nexus', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: Saudi-Nexus');
});

bot.action('model_saudi_banks', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: Saudi-Banks');
});

bot.action('model_lexnexus', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: LexNexus (القائد)');
});

// أمر /ask - سؤال نموذج محدد
bot.command('ask', async (ctx) => {
    const parts = ctx.message.text.split(' ').slice(1);
    const modelName = parts[0];
    const question = parts.slice(1).join(' ');

    if (!modelName || !question) {
        return ctx.reply('الصيغة: /ask <نموذج> <سؤال>\nمثال: `/ask Saudi-Nexus ما هي إجراءات الأمان؟`');
    }

    const modelId = MODELS.sub_models[modelName as keyof typeof MODELS.sub_models] || MODELS.leader;
    await ctx.replyWithChatAction('typing');

    const answer = await callGPT(modelId, question);
    ctx.reply(answer, { parse_mode: 'Markdown' });
});

// أمر /chat - سؤال LexNexus (القائد)
bot.command('chat', async (ctx) => {
    const question = ctx.message.text.replace('/chat', '').trim();

    if (!question) {
        return ctx.reply('❌ أدخل سؤال بعد الأمر.\nمثال: `/chat ما هي خطتك كقائد؟`');
    }

    await ctx.replyWithChatAction('typing');

    const enhancedPrompt = `أنت LexNexus، القائد الذكي لنظام Top-Tier Global Hub. \n    السؤال: ${question}\n\n    إذا كان السؤال يتعلق بالتحقق أو الأمان، استخدم معرفة Saudi-Nexus.\n    إذا كان السؤال يتعلق بالبنوك أو المالية، استخدم معرفة Saudi-Banks.\n    إذا كان السؤال عاماً، استخدم حكمك كقائد.`;

    const answer = await callGPT(MODELS.leader, enhancedPrompt);
    ctx.reply(answer, { parse_mode: 'Markdown' });
});

// أمر /status - حالة كل النماذج
bot.command('status', async (ctx) => {
    const status = `📊 *حالة النماذج الذكية*\n\n` +
        `🏆 *LexNexus (القائد)*:\n` +
        `   المعرف: \\\`${MODELS.leader}\\\`\n` +
        `   الحالة: *ONLINE* 🟢\n\n` +
        `📦 *النماذج الفرعية*:\n` +
        `• Saudi-Nexus: ${MODELS.sub_models['Saudi-Nexus']}\n` +
        `• Saudi-Banks: ${MODELS.sub_models['Saudi-Banks']}\n\n` +
        `🔗 كل النماذج متصلة بالمستودع:\n` +
        `https://github.com/${process.env.GITHUB_REPO}`;

    ctx.reply(status, { parse_mode: 'MarkdownV2' });
});

// أمر /help
bot.command('help', (ctx) => {
    ctx.reply(
        `❓ *دليل استخدام LexNexus Bot*\n\n` +
        `*الأوامر الرئيسية:*\n` +
        `• /start - بدء المحادثة\n` +
        `• /chat <سؤال> - سؤال LexNexus القائد\n` +
        `• /ask <نموذج> <سؤال> - سؤال نموذج محدد\n` +
        `• /model - اختيار نموذج (مشرف)\n` +
        `• /leader - معلومات القائد\n` +
        `• /status - حالة كل النماذج\n\n` +
        `*أمثلة:*\n` +
        '`/chat ما هي خطة اليوم؟`\n' +
        '`/ask Saudi-Nexus تحقق من الكود`',
        { parse_mode: 'MarkdownV2' }
    );
});

// Webhook handler
router.post('/webhook/:token', async (req, res) => {
    if (req.params.token !== process.env.TELEGRAM_BOT_TOKEN) {
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
