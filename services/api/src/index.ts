import express, { Request, Response } from "express";
import cors from "cors";
import axios from "axios";

const app = express();
app.use(cors());

const PORT = process.env.PORT || 3000;

app.get("/v1/repo/status", async (_req: Request, res: Response) => {
  const owner = process.env.GITHUB_REPO_OWNER || process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO || process.env.GITHUB_PROJECT;

  if (!owner || !repo) {
    res.status(500).json({ error: "GITHUB_REPO_OWNER and GITHUB_REPO env variables are required" });
    return;
  }

  const token = process.env.GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "repo-status-service"
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const [commits, branches, pulls] = await Promise.all([
      axios.get(`https://api.github.com/repos/${owner}/${repo}/commits`, { headers }),
      axios.get(`https://api.github.com/repos/${owner}/${repo}/branches`, { headers }),
      axios.get(`https://api.github.com/repos/${owner}/${repo}/pulls?state=open`, { headers })
    ]);

    const since = new Date();
    since.setDate(since.getDate() - 7);
    const commitsWeek = await axios.get(
      `https://api.github.com/repos/${owner}/${repo}/commits?since=${since.toISOString()}`,
      { headers }
    );

    res.json({
      repo: `${owner}/${repo}`,
      latest_commit: {
        sha: commits.data[0]?.sha,
        message: commits.data[0]?.commit?.message,
        author: commits.data[0]?.commit?.author
      },
      branches: branches.data.map((b: any) => b.name),
      open_prs: pulls.data.map((p: any) => ({ number: p.number, title: p.title, user: p.user.login })),
      commits_last_week: commitsWeek.data.map((c: any) => ({
        sha: c.sha,
        message: c.commit.message,
        date: c.commit.author.date
      }))
    });
  } catch (error: any) {
    const status = error?.response?.status || 500;
    const message = error?.response?.data || error?.message || "Unknown error";
    res.status(status).json({ error: message });
  }
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});

export default app;
