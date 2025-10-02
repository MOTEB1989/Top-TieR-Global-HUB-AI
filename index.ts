import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import { z } from 'zod';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.API_PORT || 3000);
const CORE_URL = process.env.CORE_URL || 'http://localhost:8080';

app.get('/v1/health', async (_req, res) => {
  try {
    const r = await axios.get(`${CORE_URL}/health`);
    res.json({ gateway: 'ok', core: r.data });
  } catch (e: any) {
    res.status(500).json({ gateway: 'ok', core: 'down', error: e?.message });
  }
});

const EmbedSchema = z.object({ text: z.string().min(1) });

app.post('/v1/embed', async (req, res) => {
  const parsed = EmbedSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.format());
  try {
    const r = await axios.post(`${CORE_URL}/embed`, parsed.data);
    res.json(r.data);
  } catch (e: any) {
    res.status(500).json({ error: e?.message });
  }
});

/* ---------------- Repo Status (GitHub API) ---------------- */
app.get('/v1/repo/status', async (_req, res) => {
  try {
    const GITHUB_TOKEN = process.env.LEXCODE_GITHUB_TOKEN;
    if (!GITHUB_TOKEN) {
      return res.status(400).json({ error: 'Missing LEXCODE_GITHUB_TOKEN in environment' });
    }

    const owner = 'MOTEB1989';
    const repo = 'Top-TieR-Global-HUB-AI';

    const headers = { Authorization: `token ${GITHUB_TOKEN}`, 'User-Agent': 'LexCode-Gateway' };

    const commits = await axios.get(`https://api.github.com/repos/${owner}/${repo}/commits`, { headers });
    const branches = await axios.get(`https://api.github.com/repos/${owner}/${repo}/branches`, { headers });
    const pulls = await axios.get(`https://api.github.com/repos/${owner}/${repo}/pulls?state=open`, { headers });

    res.json({
      repo: `${owner}/${repo}`,
      latest_commit: {
        sha: commits.data[0].sha,
        message: commits.data[0].commit.message,
        author: commits.data[0].commit.author,
      },
      branches: branches.data.map((b: any) => b.name),
      open_prs: pulls.data.map((p: any) => ({ number: p.number, title: p.title, user: p.user.login })),
    });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'github_status_failed' });
  }
});

app.listen(PORT, () => {
  console.log(`LexCode API on http://localhost:${PORT}`);
});


/** ---------------- AI Inference ---------------- */
import type { ChatMessage } from './providers/ai';
import { OpenAIProvider } from './providers/openai';

const provider = new OpenAIProvider();

app.post('/v1/ai/infer', async (req, res) => {
  try {
    const body = req.body as { messages: ChatMessage[]; model?: string; temperature?: number };
    if (!body?.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return res.status(400).json({ error: 'messages: ChatMessage[] is required' });
    }
    const out = await provider.infer(body.messages, { model: body.model, temperature: body.temperature });
    res.json({ provider: 'openai', ...out });
  } catch (e: any) {
    res.status(500).json({ error: e?.message || 'inference_failed' });
  }
});
