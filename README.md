# Aottar AI Backend

FastAPI backend for the Aottar AI shopping assistant. It classifies intent,
extracts entities (brand/category/budget/feature) from the customer's
message, searches the WooCommerce product catalog (hybrid BM25 + FAISS
vector search), re-ranks results, and asks an LLM (Groq/Llama) to write the
final reply — then returns everything to the `aottar-ai-chatbot` WordPress
plugin, which renders it as chat bubbles and product cards.

```
Vendor → WooCommerce → (scheduled sync) → local cache + FAISS index → Chatbot
```

---

## 1. Requirements

- Python 3.11+ (developed/tested against 3.13)
- A WooCommerce store with REST API keys (Settings → Advanced → REST API)
- A Groq API key (https://console.groq.com)

## 2. Setup

```bash
cd aottar-ai-backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# spaCy's English model isn't a normal PyPI package — install it separately
python -m spacy download en_core_web_sm
```

### Environment variables

Copy `.env.example` to `.env` and fill in your real values:

```bash
cp .env.example .env
```

| Variable | What it's for |
|---|---|
| `GROQ_API_KEY` | LLM used for intent classification, entity extraction, and writing the final chat reply |
| `WC_URL` | Your WordPress/WooCommerce site URL, e.g. `https://aottar.com` |
| `WC_CONSUMER_KEY` / `WC_CONSUMER_SECRET` | WooCommerce REST API keys (WP Admin → WooCommerce → Settings → Advanced → REST API → Add key. Needs **Read** access) |

`.env` is already in `.gitignore` — never commit it or share it publicly. If
a key ever leaks, regenerate it from the WooCommerce/Groq dashboard.

## 3. Running the backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then check:

- `http://127.0.0.1:8000/health` → `{"status": "healthy"}`
- `http://127.0.0.1:8000/docs` → interactive API docs (Swagger UI)

Drop `--reload` in production (it's a dev-only convenience flag that
restarts the server on every file change).

## 4. Vendor → WooCommerce → Chatbot product sync

On startup, the backend automatically:

1. Fetches every published product from WooCommerce.
2. Writes a clean copy to `app/data/products_cache.json`.
3. Rebuilds the FAISS vector index from it.
4. Hot-swaps the live search index the chatbot uses — **no restart needed.**

This then repeats automatically every 20 minutes for as long as the server
is running, so when a vendor adds or edits a product in WooCommerce, it
shows up in the chatbot within ~20 minutes with no manual steps.

Useful endpoints:

- `GET /admin/sync-status` — last sync time, product count, last error (if any)
- `POST /admin/sync-now` — trigger a sync immediately (e.g. right after adding a product, if you don't want to wait)

To change the sync interval, edit `SYNC_INTERVAL_MINUTES` in
`app/core/scheduler.py`.

## 5. Per-conversation memory

Each visitor's conversation (brand/category/budget/feature context) is kept
isolated from every other visitor's, and automatically forgotten after 45
minutes of inactivity. See `app/memory/conversation_memory.py`.

Sessions are currently identified server-side by IP + User-Agent, since the
WordPress plugin doesn't send an explicit session id. This is a best-effort
fallback — visitors sharing an IP (office wifi, some mobile carriers, VPN)
can be bucketed together. If more accurate isolation is needed later, the
plugin's `assets/js/api.js` can be updated to generate and send a real
`session_id` (e.g. a UUID stored in `localStorage`).

## 6. Deploying so WordPress can actually reach it

**This is the part that trips people up:** `127.0.0.1:8000` only works if
WordPress and the backend are running on the *same* machine (e.g. a local
dev setup like LocalWP/XAMPP on your own PC). If `aottar.com` is a real,
live hosted WordPress site, its visitors' browsers call this API directly
from their own browser — so the backend needs a **public URL**, not your
laptop's localhost.

Options, roughly easiest → most control:
- **Railway / Render / Fly.io** — push this repo, get a public HTTPS URL, set the env vars in their dashboard instead of `.env`.
- **A VPS** (DigitalOcean, Hetzner, etc.) — run `uvicorn` behind `nginx` + a process manager (systemd or `pm2`), with a Let's Encrypt SSL cert.

Whichever you choose, **you must use HTTPS** if `aottar.com` is served over
HTTPS (it almost certainly is) — browsers block a HTTPS page from calling
a plain `http://` API (mixed content), so the chatbot will silently fail
until the backend has a valid SSL certificate too.

Once deployed, update the CORS allow-list in `app/main.py` if your backend
domain or WordPress domain differs from what's currently set
(`https://aottar.com`, `https://www.aottar.com`).

## 7. Connecting the WordPress plugin (`aottar-ai-chatbot`)

1. **Install the plugin.** Either:
   - Zip the `aottar-ai-chatbot` folder and upload it via WP Admin → Plugins → Add New → Upload Plugin, or
   - Copy the `aottar-ai-chatbot` folder directly into `wp-content/plugins/` on the server (via FTP/SSH).
2. **Activate it**: WP Admin → Plugins → find "Aottar AI Chatbot" → Activate.
3. **Point it at your backend**: a new "Aottar AI" menu item appears in the WP Admin sidebar.
   - Enter your backend's chat endpoint URL, **with the trailing slash**, e.g.:
     ```
     https://your-backend-domain.com/chat/
     ```
   - Click **Save Settings**, then click **Test Connection** — it should show "✅ Backend Connected Successfully". If it says "❌ Unable to Connect" or "❌ Backend Responded with Error", see troubleshooting below.
4. **That's it** — the chatbot widget auto-injects into the footer of every page (`wp_footer` hook), no shortcode placement required. (A `[aottar_chatbot]` shortcode is also registered if you ever want to embed it inline on a specific page/template instead.)

### Troubleshooting the WordPress connection

| Symptom | Likely cause |
|---|---|
| "❌ Unable to Connect" | Backend isn't reachable from the internet yet (still `127.0.0.1`), backend is down, or a firewall is blocking the port |
| "❌ Backend Responded with Error" | Backend is reachable but errored — check the backend's terminal/logs, or hit `/admin/sync-status` and `/health` directly in a browser |
| Chat works in WP Admin's "Test Connection" but not on the live site for real visitors | Almost always CORS — the visitor's browser origin (`https://aottar.com`) isn't in the `allow_origins` list in `app/main.py`, or it's mixed-content (HTTPS page calling an HTTP backend) |
| Product cards never show up | Run `POST /admin/sync-now` and check `GET /admin/sync-status` for `last_error` — usually a stale/incorrect WooCommerce key in `.env` |

---

## Project structure

```
app/
├── main.py                  FastAPI app, CORS, routers, startup sync scheduler
├── api/                     Route handlers (chat, products, vendors, health)
├── core/                    Settings, logging, the sync scheduler
├── services/                ChatService, WooCommerceService, ProductSyncService, ...
├── pipelines/                ShoppingPipeline (intent → entities → search → rerank → reply)
├── models/                  Intent classifier, entity extractor (LLM-based)
├── retrieval/                BM25 search, hybrid search, product loader/cache
├── rag/                      Embeddings + FAISS vector store
├── memory/                  Per-conversation memory (SessionMemoryStore)
└── data/                    products_cache.json (generated, not committed)
```
