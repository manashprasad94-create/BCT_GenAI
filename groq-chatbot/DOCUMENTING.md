# Technical Documentation

Architecture, API reference, and a walkthrough of how each file works — for
anyone extending or maintaining this project.

---

## 1. Architecture overview

```
┌──────────────┐        POST /api/chat         ┌──────────────┐        stream       ┌──────────┐
│   Browser    │ ─────────────────────────────▶ │   Express    │ ──────────────────▶ │   Groq   │
│ (script.js)  │ ◀───────────────────────────── │  (server.js) │ ◀────────────────── │   API    │
└──────────────┘     streamed text tokens       └──────────────┘   streamed tokens    └──────────┘
       │                                                │
       ▼                                                ▼
  localStorage                                   in-memory rate
 (chat history)                                   limiter (Map)
```

- **One Express server** serves the static frontend *and* the `/api/chat`
  endpoint, so there's no CORS complexity and only one process to run.
- **No database** — conversation state lives in the browser's
  `localStorage`; the server is stateless between requests except for the
  in-memory rate-limit map.
- **Streaming end-to-end** — Groq streams tokens to the backend, the backend
  streams them to the browser via chunked `text/plain` responses, and the
  frontend reads them with `ReadableStream.getReader()`.

---

## 2. Backend (`backend/server.js`)

### Startup sequence
1. Loads `.env` via `dotenv`.
2. Exits immediately with a clear error if `GROQ_API_KEY` is missing —
   fail fast rather than crashing later mid-conversation.
3. Initializes the Groq SDK client and Express app.
4. Registers middleware: `cors()`, `express.json({ limit: '1mb' })`, and
   static file serving for `frontend/`.

### Rate limiting
A simple in-memory, per-IP sliding-window limiter:
- **Limit:** 20 requests per 60 seconds per IP (`RATE_LIMIT`, `RATE_WINDOW_MS`).
- Implemented with a `Map<ip, timestamp[]>` — timestamps older than the
  window are filtered out on every request.
- This is intentionally simple and resets if the server restarts. For real
  production traffic, swap it for `express-rate-limit` backed by Redis.

### Endpoints

#### `GET /api/health`
Returns server status and the active model. Useful for uptime checks and
hosting-platform health probes.

**Response:**
```json
{ "status": "ok", "model": "openai/gpt-oss-120b" }
```

#### `POST /api/chat`
The main chat endpoint.

**Request body:**
```json
{
  "messages": [
    { "role": "user", "content": "Hello!" },
    { "role": "assistant", "content": "Hi there!" },
    { "role": "user", "content": "How are you?" }
  ]
}
```

**Validation performed:**
- `messages` must be a non-empty array.
- Every message must have `role` of `"user"` or `"assistant"` and a
  non-empty string `content`.
- Only the **last 20 messages** are forwarded to Groq (`messages.slice(-20)`)
  to keep requests fast, cheap, and within context limits.

**Processing:**
1. A system prompt is prepended, defining the assistant's persona
   (see [Customization](#4-customization-points) to change it).
2. Calls `groq.chat.completions.create({ ..., stream: true })`.
3. Iterates the async stream, writing each token to the HTTP response as it
   arrives (`res.write(token)`), with headers set for a plain-text,
   no-cache stream.

**Success response:** `200 OK`, `Content-Type: text/plain`, body streamed as
raw text chunks (not JSON, not SSE — just plain text over time).

**Error responses** (only if sent before streaming starts):
| Status | Condition |
|---|---|
| `400` | Malformed or empty `messages` |
| `401` | Invalid Groq API key |
| `429` | Rate limit exceeded |
| `500` | Any other Groq/API failure |

If an error occurs *after* streaming has already begun, the server can't
send a clean JSON error anymore (headers are already sent) — it just ends
the response, and the frontend's empty-response check catches it.

#### Catch-all `/api` 404
Any unrecognized route under `/api` returns `404 { "error": "Not found" }`.
Registered last so it doesn't shadow the real routes above it.

---

## 3. Frontend (`frontend/`)

### `index.html`
Minimal semantic structure: header (title + Clear button), a scrollable
message list (`#chatWindow`), a dismissible error banner, and a form with an
auto-growing `<textarea>` and submit button.

### `script.js`
Owns all client-side behavior. Key pieces:

- **State:** a single `conversation` array (`{ role, content }[]`) is the
  source of truth, loaded from and saved to `localStorage` under the key
  `groq-chatbot-history`.
- **`handleSend()`** — the core flow on submit:
  1. Push the user message into `conversation`, render it optimistically, persist it.
  2. Render an empty "typing" bubble for the assistant reply.
  3. `fetch('/api/chat', { method: 'POST', body: JSON.stringify({ messages: conversation }) })`.
  4. If the response isn't OK, parse the JSON error body and throw.
  5. Otherwise read the stream via `response.body.getReader()`, decoding and
     appending each chunk to the bubble's `textContent` live.
  6. On completion, push the full assistant reply into `conversation` and save.
  7. On any failure, remove the incomplete bubble and show the error banner
     instead of leaving a broken message.
- **UX details:** Enter sends (Shift+Enter for newline), the textarea
  auto-grows, input/send button are disabled while streaming
  (`setStreaming`), and `Clear` wipes both state and `localStorage`.

### `style.css`
Defines the visual theme via CSS custom properties at the top of the file —
this is the fastest place to reskin the app (see below).

---

## 4. Customization points

| Want to change... | Edit... |
|---|---|
| Bot personality / instructions | `systemMessage.content` in `server.js` |
| AI model | `GROQ_MODEL` in `.env` (see [console.groq.com/docs/models](https://console.groq.com/docs/models)) |
| Colors / theme | CSS variables at the top of `style.css` |
| How much history is sent to the model | `messages.slice(-20)` in `server.js` |
| Rate limit thresholds | `RATE_LIMIT` / `RATE_WINDOW_MS` in `server.js` |
| Reply length cap | `max_tokens` in the `groq.chat.completions.create()` call |
| Creativity/randomness | `temperature` in the same call (`0` = focused, `1+` = more random) |

---

## 5. Security & reliability notes

- ✅ The Groq API key never leaves the server — it's read from `.env` and
  used only in server-side SDK calls, never sent to the browser.
- ✅ Every request to `/api/chat` is validated for shape and content before
  it touches the Groq API.
- ✅ Basic per-IP rate limiting protects against runaway API costs.
- ✅ Startup validation prevents the app from running in a broken,
  half-configured state.
- ✅ Errors are surfaced to the user via the error banner instead of silent
  failures or infinite spinners.

### Known limitations (by design, for simplicity)
- Chat history is per-browser (`localStorage`), not per-user-account — it
  won't sync across devices.
- The rate limiter is in-memory, so it resets on server restart and doesn't
  work across multiple server instances.
- No markdown rendering in the UI yet, even though the system prompt asks
  the model to use markdown formatting.

### Suggested next steps if you keep building
- Swap the in-memory rate limiter for `express-rate-limit` + Redis for real
  production traffic.
- Add user authentication for per-user chat history instead of relying on
  one browser's `localStorage`.
- Add a database (Postgres/SQLite) so history survives across devices.
- Render markdown in assistant replies (e.g. with `marked.js`).

---

## 6. Dependencies

| Package | Purpose |
|---|---|
| `express` | HTTP server & routing |
| `cors` | Cross-origin request handling |
| `dotenv` | Loads `.env` into `process.env` |
| `groq-sdk` | Official Groq API client |
