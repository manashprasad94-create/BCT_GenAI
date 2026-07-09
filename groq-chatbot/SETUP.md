# Setup Guide

Everything you need to get the Groq AI Chatbot running locally, testing it,
and deploying it to production.

---

## 1. Prerequisites

- **Node.js 18 or newer** — check with:
  ```bash
  node -v
  ```
  Install from [nodejs.org](https://nodejs.org) if you don't have it.
- **A free Groq API key** — sign up at [console.groq.com](https://console.groq.com)
  → **API Keys** → **Create API Key**. No credit card required for the free tier.

---

## 2. Local installation (5 minutes)

```bash
# 1. Move into the backend folder — this is where the server and
#    package.json live
cd groq-chatbot/backend

# 2. Install dependencies (express, cors, dotenv, groq-sdk)
npm install

# 3. Create your local environment file from the template
cp .env.example .env

# 4. Open .env in any text editor and paste your real key:
#    GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# 5. Start the server
npm start
```

You should see:

```
✅ Groq chatbot server running at http://localhost:3000
   Using model: openai/gpt-oss-120b
```

Open **http://localhost:3000** in your browser. One server handles both the
API and the chat UI — there's nothing else to run.

### Development mode

Use `npm run dev` instead of `npm start` while you're actively editing code.
It uses Node's built-in `--watch` flag to auto-restart the server on every
save.

---

## 3. Environment variables

Defined in `backend/.env` (copy from `.env.example`):

| Variable       | Required | Default              | Description |
|----------------|----------|-----------------------|--------------|
| `GROQ_API_KEY` | ✅ Yes   | —                     | Your Groq API key. The server refuses to start without it. |
| `PORT`         | No       | `3000`                | Port the Express server listens on. |
| `GROQ_MODEL`   | No       | `openai/gpt-oss-120b` | Which Groq-hosted model to use. See [console.groq.com/docs/models](https://console.groq.com/docs/models) for the current list — Groq updates these periodically. |

---

## 4. Testing it works

**Manual test (recommended for a chatbot):**
1. Send "Hello, who are you?" — you should see a typing indicator, then text streaming in.
2. Send a follow-up like "What did I just ask you?" — confirms conversation memory works.
3. Click **Clear** — confirms history resets.
4. Refresh the page mid-conversation — confirms `localStorage` persistence.

**API test with curl** (server must already be running):
```bash
curl -N -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Say hi in 5 words"}]}'
```
The `-N` flag disables curl's output buffering so you can watch tokens
stream in live.

**Health check:**
```bash
curl http://localhost:3000/api/health
```
Expected response: `{"status":"ok","model":"openai/gpt-oss-120b"}`

---

## 5. Debugging common issues

| Symptom | Cause | Fix |
|---|---|---|
| Server won't start — "Missing GROQ_API_KEY" | `.env` missing or empty | Run `cp .env.example .env` and paste your key |
| `401` error in the browser | Invalid or expired API key | Regenerate a key at [console.groq.com/keys](https://console.groq.com/keys) |
| `429 Too many requests` | Hit the built-in rate limiter (20 req/min per IP) or Groq's own rate limit | Wait a minute, or raise `RATE_LIMIT` in `server.js` |
| Chat bubble stays empty forever | Model name deprecated or invalid | Check current models at [console.groq.com/docs/models](https://console.groq.com/docs/models), update `GROQ_MODEL` in `.env` |
| CORS error in the console | Frontend served from a different origin than backend | Keep using `http://localhost:3000` for both — don't open `index.html` directly via `file://` |
| Changes to `server.js` not taking effect | Server still running the old code | Stop it (`Ctrl+C`) and restart, or use `npm run dev` |

Server-side errors always print to your terminal (`console.error(...)` in
`server.js`) — check there first when something misbehaves.

---

## 6. Deployment

Any Node.js host works. Two straightforward free/cheap options:

### Option A: Render.com (simplest)
1. Push this project to a GitHub repo.
2. On [render.com](https://render.com) → **New → Web Service** → connect your repo.
3. Set **Root Directory** to `backend`.
4. **Build Command:** `npm install`   **Start Command:** `npm start`
5. Add environment variable `GROQ_API_KEY` (and optionally `GROQ_MODEL`) in
   the Render dashboard — never commit `.env` to git.
6. Deploy. Render gives you a public URL serving both your API and frontend.

### Option B: Railway.app
1. Push to GitHub, then **New Project → Deploy from GitHub repo** on
   [railway.app](https://railway.app).
2. Set the root/service directory to `backend`.
3. Add `GROQ_API_KEY` under **Variables**.
4. Railway auto-detects `npm start`. Deploy and you'll get a public URL.

### Pre-deployment checklist
- [ ] `.env` is listed in `.gitignore` (it is, by default) — **never** commit your API key.
- [ ] `npm install` runs cleanly with no errors.
- [ ] You've run `npm start` locally one final time to confirm everything works.
- [ ] `GROQ_API_KEY` is set as an environment variable on the host, not hardcoded anywhere.

---

## 7. Next steps

Once it's running, head to **[DOCUMENTING.md](./DOCUMENTING.md)** to
understand how the code is structured and where to make changes.
