# Groq AI Chatbot

A lightweight, production-minded AI chatbot powered by [Groq](https://groq.com)'s
ultra-fast inference API. Streaming token-by-token replies, persistent chat
history, a clean vanilla-JS UI, and zero build tools required.

![Node](https://img.shields.io/badge/node-%3E%3D18-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## ✨ Features

- ⚡ **Real-time streaming** — replies appear token-by-token, ChatGPT-style
- 🧠 **Conversation memory** — full chat history is sent with every request
- 💾 **Persistent history** — saved in `localStorage`, survives page refresh
- 🛡️ **Hardened backend** — startup validation, input validation, per-IP rate limiting
- 🎨 **Clean, responsive UI** — no frameworks, no build step
- 🚀 **One server** — Express serves both the API and the frontend

---

## 📁 Project structure

```
groq-chatbot/
├── backend/
│   ├── server.js         # Express server + Groq API integration
│   ├── package.json      # Dependencies & npm scripts
│   ├── .env.example      # Template for your environment variables
│   └── .gitignore
├── frontend/
│   ├── index.html        # Chat UI markup
│   ├── style.css         # Styling (CSS variables for theming)
│   └── script.js         # Streaming fetch logic + state management
├── README.md              # You are here — overview & quick start
├── SETUP.md                # Detailed install, run, and deploy instructions
└── DOCUMENTING.md          # Architecture, API reference & code walkthrough
```

---

## 🚀 Quick start

```bash
cd groq-chatbot/backend
npm install
cp .env.example .env        # then paste your Groq API key into .env
npm start
```

Open **http://localhost:3000** — that's it.

Need more detail (prerequisites, troubleshooting, deployment)? See **[SETUP.md](./SETUP.md)**.

---

## 🧩 How it works (30-second version)

1. You type a message → the frontend appends it to a `conversation` array and
   `POST`s the whole array to `/api/chat`.
2. The backend validates the request, adds a system prompt, and calls Groq
   with `stream: true`.
3. Groq streams tokens back; the backend forwards each one to the browser
   immediately over a chunked HTTP response.
4. The frontend reads the stream and appends each chunk to the message bubble
   live, then saves the finished reply to `localStorage`.

For the full technical walkthrough, request/response shapes, and customization
points, see **[DOCUMENTING.md](./DOCUMENTING.md)**.

---

## 🛠️ Tech stack

| Layer    | Technology |
|----------|------------|
| Backend  | Node.js, Express, `groq-sdk` |
| Frontend | Vanilla HTML/CSS/JavaScript (no framework) |
| AI       | Groq API (`openai/gpt-oss-120b` by default) |
| Storage  | Browser `localStorage` (no database) |

---

## 📄 License

MIT — free to use, modify, and deploy.
