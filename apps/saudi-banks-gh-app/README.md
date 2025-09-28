# Saudi Banks GitHub App (Quickstart)

This app listens to `pull_request` webhooks and posts a comment using the contents of `message.md`.

## Prerequisites
- Node.js >= 18
- A GitHub App with:
  - Webhooks: Active
  - Webhook URL: your Smee proxy URL
  - Webhook secret: set and copied into `.env`
  - Repository permissions: Pull requests (Read & write)
  - Subscribed events: Pull request
- A private key (`.pem`) generated from the app settings.

## Local setup
1. Copy `.env.example` to `.env` and fill values:
   - `APP_ID`, `WEBHOOK_SECRET`, `PRIVATE_KEY_PATH`
2. Place your private key at the path you set in `PRIVATE_KEY_PATH`.
3. Install deps:
   ```bash
   npm install
   ```
4. Start Smee proxy in one terminal:
   ```bash
   SMEE_URL="https://smee.io/your-channel" npm run smee
   ```
5. Start the server in another terminal:
   ```bash
   npm run server
   ```
6. Open or update a PR in a repository where your app is installed; you should see a comment from the app using `message.md`.

## Notes
- Endpoint: `POST /api/webhook`
- Stop with Ctrl+C in both terminals.
