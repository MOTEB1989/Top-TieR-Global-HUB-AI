const fs = require("fs");
const path = require("path");
const express = require("express");
const dotenv = require("dotenv");
const { App } = require("@octokit/app");
const { Webhooks, createNodeMiddleware } = require("@octokit/webhooks");

dotenv.config();

const APP_ID = process.env.APP_ID;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const PRIVATE_KEY_PATH = process.env.PRIVATE_KEY_PATH || "./private-key.pem";
const PORT = process.env.PORT || 3000;

if (!APP_ID || !WEBHOOK_SECRET || !PRIVATE_KEY_PATH) {
  console.error("Missing APP_ID, WEBHOOK_SECRET, or PRIVATE_KEY_PATH in environment.");
  process.exit(1);
}

let privateKey;
try {
  privateKey = fs.readFileSync(PRIVATE_KEY_PATH, "utf8");
} catch (e) {
  console.error(`Failed to read private key at ${PRIVATE_KEY_PATH}:`, e.message);
  process.exit(1);
}

const app = new App({ appId: APP_ID, privateKey });
const webhooks = new Webhooks({ secret: WEBHOOK_SECRET });

function getMessageBody() {
  const msgPath = path.join(__dirname, "..", "message.md");
  try {
    return fs.readFileSync(msgPath, "utf8");
  } catch {
    return "PR received by Saudi Banks GitHub App.";
  }
}

webhooks.on("pull_request.opened", async ({ payload }) => {
  await handlePullRequestEvent(payload, "opened");
});
webhooks.on("pull_request.reopened", async ({ payload }) => {
  await handlePullRequestEvent(payload, "reopened");
});
webhooks.on("pull_request.synchronize", async ({ payload }) => {
  await handlePullRequestEvent(payload, "synchronize");
});

async function handlePullRequestEvent(payload, reason) {
  try {
    const installationId = payload.installation?.id;
    const owner = payload.repository.owner.login;
    const repo = payload.repository.name;
    const issue_number = payload.pull_request.number;

    const octokit = await app.getInstallationOctokit(installationId);
    const body = getMessageBody();

    await octokit.rest.issues.createComment({
      owner,
      repo,
      issue_number,
      body
    });

    console.log(`[OK] Commented on PR #${issue_number} in ${owner}/${repo} (reason=${reason})`);
  } catch (err) {
    console.error("[ERROR] Failed to handle pull_request event:", err);
  }
}

const server = express();
server.use(createNodeMiddleware(webhooks, { path: "/api/webhook" }));
server.get("/", (_req, res) => res.send("Saudi Banks GitHub App is running."));
server.listen(PORT, () => {
  console.log(`Server is listening at http://localhost:${PORT}/api/webhook`);
});
