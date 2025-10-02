/**
 * Minimal Express REST API example.
 *
 * The server exposes a `/health` endpoint and a `/proxy` endpoint that
 * demonstrates how to call a third-party API with Axios.  This file is
 * designed to be executed directly or imported into tests.
 */
let express;
let axios;

try {
  express = require('express');
} catch (error) {
  throw new Error("The 'express' package is required. Install it with 'npm install express'.");
}

try {
  axios = require('axios');
} catch (error) {
  throw new Error("The 'axios' package is required. Install it with 'npm install axios'.");
}

function createServer() {
  const app = express();

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok', service: 'top-tier-adapter-example' });
  });

  app.get('/proxy', async (_req, res) => {
    try {
      const response = await axios.get('https://api.github.com/rate_limit', {
        headers: { 'User-Agent': 'top-tier-adapter-example' },
      });
      res.json(response.data);
    } catch (error) {
      res.status(502).json({ error: 'Failed to contact GitHub', details: error.message });
    }
  });

  return app;
}

if (require.main === module) {
  const port = process.env.PORT || 3000;
  const app = createServer();
  app.listen(port, () => {
    console.log(`Express API example listening on http://localhost:${port}`);
  });
}

module.exports = { createServer };
