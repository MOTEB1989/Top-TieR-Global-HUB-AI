import express from "express";
import bodyParser from "body-parser";
import fetch from "node-fetch";
import cors from "cors";

const app = express();
app.use(cors());
app.use(bodyParser.json());

const CORE_URL = process.env.CORE_URL || "http://core:3000";
const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || "http://orchestrator:3100";

const HUB_SERVICES = [
  {
    id: "health",
    name: "Gateway Health",
    description: "Diagnostic endpoint for gateway and downstream services.",
    method: "GET",
    path: "/v1/health"
  },
  {
    id: "core-infer",
    name: "Core AI Inference",
    description: "Direct LLM inference via the Core service.",
    method: "POST",
    path: "/v1/ai/infer",
    target: `${CORE_URL}/v1/ai/infer`
  },
  {
    id: "lex-run",
    name: "Lex Orchestrator",
    description: "Coordinate the tri-agent orchestrator for repo analysis and operations.",
    method: "POST",
    path: "/v1/lex/run",
    target: `${ORCHESTRATOR_URL}/v1/lex/run`
  }
];

const summarizeServiceStatus = (ok) => (ok ? "ok" : "error");

app.get("/", (req, res) => {
  const baseUrl = `${req.protocol}://${req.get("host")}`;
  const links = HUB_SERVICES.map(
    (service) => `      <li><strong>${service.name}</strong> — ${service.description}<br/><code>${service.method} ${baseUrl}${service.path}</code></li>`
  ).join("\n");

  res.type("html").send(`<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Lex Gateway Hub</title>
    <style>
      body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; background: #0f172a; color: #f8fafc; }
      h1 { color: #38bdf8; }
      a { color: #38bdf8; }
      code { background: rgba(148, 163, 184, 0.2); padding: 0.15rem 0.35rem; border-radius: 0.35rem; display: inline-block; margin-top: 0.25rem; }
      ul { list-style: none; padding: 0; }
      li { margin-bottom: 1.5rem; }
      footer { margin-top: 3rem; font-size: 0.9rem; color: #94a3b8; }
    </style>
  </head>
  <body>
    <h1>🔗 Lex Gateway Hub</h1>
    <p>لوحة تحكم موحدة للوصول إلى الخدمات الأساسية من أي جهاز، بما في ذلك iPhone.</p>
    <ul>
${links}
    </ul>
    <footer>Powered by Top-TieR Global HUB AI</footer>
  </body>
</html>`);
});

app.get("/v1/hub", (req, res) => {
  const baseUrl = `${req.protocol}://${req.get("host")}`;
  res.json({
    status: "online",
    services: HUB_SERVICES.map((service) => ({
      id: service.id,
      name: service.name,
      description: service.description,
      method: service.method,
      url: `${baseUrl}${service.path}`,
      target: service.target
    }))
  });
});

app.get("/v1/health", async (req, res) => {
  const results = {};
  let isHealthy = true;

  const checkService = async (label, url) => {
    if (!url) {
      results[label] = { status: "ok" };
      return;
    }
    try {
      const response = await fetch(url);
      const data = await response.json().catch(() => ({}));
      const ok = response.ok;
      if (!ok) isHealthy = false;
      results[label] = {
        status: summarizeServiceStatus(ok),
        httpStatus: response.status,
        data
      };
    } catch (error) {
      isHealthy = false;
      results[label] = {
        status: "error",
        error: error.message
      };
    }
  };

  await Promise.all([
    checkService("core", `${CORE_URL}/v1/health`),
    checkService("orchestrator", `${ORCHESTRATOR_URL}/v1/health`)
  ]);

  const statusCode = isHealthy ? 200 : 503;
  res.status(statusCode).json({
    status: summarizeServiceStatus(isHealthy),
    services: results
  });
});

const proxyJson = async (targetUrl, payload, res) => {
  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const text = await response.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch (parseError) {
      data = { raw: text };
    }

    if (!response.ok) {
      return res.status(response.status).json({
        error: "Upstream service error",
        details: data
      });
    }

    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};

app.post("/v1/ai/infer", async (req, res) => {
  await proxyJson(`${CORE_URL}/v1/ai/infer`, req.body, res);
});

app.post("/v1/lex/run", async (req, res) => {
  await proxyJson(`${ORCHESTRATOR_URL}/v1/lex/run`, req.body, res);
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`🚀 Gateway running on http://localhost:${PORT}`);
});
