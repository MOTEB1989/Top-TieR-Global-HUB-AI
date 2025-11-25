import { Router } from 'express';
import { Telegraf } from 'telegraf';

// --- Configuration & Environment ---
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const RAW_ALLOWLIST = process.env.TELEGRAM_ALLOWLIST || '';
const WEBHOOK_SECRET = process.env.TELEGRAM_WEBHOOK_SECRET || '';
const OPENAI_KEY = process.env.OPENAI_API_KEY || '';
const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-3.5-turbo'; // normalized

function parseAllowlist(raw: string): Set<string> {
  if (!raw.trim()) return new Set();
  return new Set(
    raw.split(',')
      .map(v => v.trim())
      .filter(v => v.length > 0)
  );
}
const ALLOWLIST = parseAllowlist(RAW_ALLOWLIST);

const router = Router();
let bot: Telegraf | null = null;

// Initialize bot only if token exists
if (TELEGRAM_BOT_TOKEN) {
  bot = new Telegraf(TELEGRAM_BOT_TOKEN);
  console.log('[telegram.bot] ✅ Bot token loaded. Allowlist size:', ALLOWLIST.size);
  if (ALLOWLIST.size === 0) {
    console.warn('[telegram.bot] ⚠️ Allowlist empty - all users can interact. Set TELEGRAM_ALLOWLIST to restrict.');
  }
} else {
  console.warn('[telegram.bot] ❌ TELEGRAM_BOT_TOKEN missing - bot commands disabled.');
}

// --- Helper: Model selection (simple fallback) ---
async function chooseModel(): Promise<string> {
  // If OPENAI_KEY missing, still return a model string (will fail later gracefully)
  return OPENAI_MODEL;
}

function userAllowed(userId?: number): boolean {
  if (!userId) return false;
  if (ALLOWLIST.size === 0) return true; // open mode
  return ALLOWLIST.has(String(userId));
}

// --- Command Registration (only if bot active) ---
if (bot) {
  bot.command('help', async ctx => {
    await ctx.reply(
      '🤖 *أوامر متاحة*:\n' +
      '/chat <سؤال> - دردشة مع النموذج\n' +
      '/repo - تحليل سريع للمستودع\n' +
      '/status - حالة التكوين\n' +
      '/help - هذه الرسالة',
      { parse_mode: 'Markdown' }
    );
  });

  bot.command('status', async ctx => {
    if (!userAllowed(ctx.from?.id)) {
      return ctx.reply('🚫 غير مسموح لك باستخدام هذا الأمر.');
    }
    const model = await chooseModel();
    await ctx.reply(
      `⚙️ *حالة النظام*\n` +
      `• OpenAI Key: ${OPENAI_KEY ? '✅ موجود' : '❌ مفقود'}\n` +
      `• النموذج: ${model}\n` +
      `• Allowlist: ${ALLOWLIST.size === 0 ? 'مفتوح للجميع' : ALLOWLIST.size + ' مستخدم'}\n`,
      { parse_mode: 'Markdown' }
    );
  });

  bot.command('chat', async ctx => {
    const message = ctx.message.text.replace('/chat', '').trim();
    if (!message) {
      return ctx.reply('❌ يرجى كتابة سؤالك بعد الأمر. مثال: /chat ما حالة CI/CD؟');
    }

    if (!userAllowed(ctx.from?.id)) {
      return ctx.reply('🚫 غير مسموح لك باستخدام هذا الأمر (خارج Allowlist).');
    }

    if (!OPENAI_KEY) {
      return ctx.reply('⚠️ لا يمكن تنفيذ الطلب الآن (مفتاح OpenAI مفقود).');
    }

    try {
      await ctx.replyWithChatAction('typing');
      const model = await chooseModel();
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_KEY}`
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: 'أنت مساعد داخل مستودع GitHub، أجب باحتراف وبالعربية الفصحى.' },
            { role: 'user', content: message }
          ],
          max_tokens: 800,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        console.error('[telegram.bot] OpenAI error:', errData);
        return ctx.reply('❌ فشل في استدعاء النموذج. حاول لاحقاً.');
      }

      const data = await response.json();
      const answer = data.choices?.[0]?.message?.content || 'لا توجد إجابة واضحة.';
      await ctx.reply(answer);
    } catch (e) {
      console.error('[telegram.bot] Chat exception:', e);
      await ctx.reply('❌ حدث خطأ أثناء المعالجة.');
    }
  });

  bot.command('repo', async ctx => {
    if (!userAllowed(ctx.from?.id)) {
      return ctx.reply('🚫 غير مسموح لك باستخدام هذا الأمر.');
    }
    // Minimal placeholder analysis (avoid reading large files here for safety)
    const summary = '📊 تحليل سريع (Placeholder)\n• يوصى باستخدام /insights في البوت Python للمزيد.';
    await ctx.reply(summary);
  });
}

// --- Webhook Endpoint ---
// Hardened: no token in path; optional secret header validation if WEBHOOK_SECRET set.
router.post('/webhook', async (req, res) => {
  if (!bot) {
    return res.status(503).json({ error: 'bot_inactive' });
  }
  if (WEBHOOK_SECRET) {
    const provided = req.headers['x-telegram-secret'];
    if (provided !== WEBHOOK_SECRET) {
      return res.status(403).json({ error: 'forbidden' });
    }
  }
  try {
    await bot.handleUpdate(req.body);
    res.status(200).json({ ok: true });
  } catch (e) {
    console.error('[telegram.bot] Webhook error:', e);
    res.status(500).json({ error: 'internal_error' });
  }
});

export default router;
