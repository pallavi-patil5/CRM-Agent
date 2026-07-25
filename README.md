# Agentic CRM Intelligence Platform

AI-powered Customer Relationship Management system that autonomously monitors a high-volume inbox, triages emails with multi-dimensional intelligence, executes agentic workflows, and surfaces real-time business insights.

---

## Resume Metrics

- 📧 **60 customer emails** across 30 conversation threads
- 🧵 **30 conversation threads** with full history retrieval
- 📚 **6 knowledge base documents** chunked and embedded into ChromaDB
- 🏷️ **12 email categories** — Complaint, Billing, Refund, Bug Report, Feature Request, Security, Legal, Compliance, Sales, Spam, Internal, General Inquiry
- 🤖 **Multi-step ReAct reasoning** with up to 6 tool invocations per email
- ⚡ **Sub-10ms heuristic pre-filter** before any LLM call
- 🔐 **5 hard-rule guardrails** — no auto-reply for Security, Legal, Spam, Internal, Critical
- 📬 **Gmail API integration** — OAuth2, real inbox sync, deduplication
- 🧠 **RAG pipeline** — PostgreSQL + ChromaDB dual storage, sentence-transformers embeddings
- 📊 **React dashboard** — 5 pages, real-time charts, agent reasoning trace viewer

---

## Architecture Overview

```
Email Ingestion
      │
      ▼
Heuristic Pre-filter (sub-10ms)
  │         │         │
Spam      Security   Legal/Compliance
  │         │         │
  ▼         ▼         ▼
Ignored   Escalate  Flag + Escalate
              │
              ▼
    Thread History Retrieval (PostgreSQL)
              │
              ▼
    RAG Knowledge Base Search (ChromaDB vector similarity)
              │
              ▼
    LLM Classification (Ollama llama3)
    - Category, Sentiment, Urgency
    - Detected Entities
    - Suggested Reply / Escalation Reason
              │
              ▼
    ReAct Agent Loop (max 6 tool calls)
    Thought → Action → Observation → Repeat
              │
         ┌────┴────┐
         ▼         ▼
    Auto-Reply   Escalate / Ticket / Flag
         │
         ▼
    PostgreSQL DB + React Dashboard
```

---

## Tech Stack

| Layer | Technology | Justification |
|---|---|---|
| Backend | FastAPI | Async-ready, automatic OpenAPI docs, Pydantic validation |
| Database | PostgreSQL | Relational integrity, JSON columns, full-text search |
| Vector Search | ChromaDB (persistent) | Dedicated vector store; fast similarity search, no numpy required |
| KB Storage | PostgreSQL + ChromaDB | PostgreSQL stores chunk text/metadata; ChromaDB stores embeddings |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Lightweight, fast, runs locally, no API cost |
| LLM | Ollama (llama3) | Fully local, no API keys, privacy-preserving |
| Email Integration | Gmail API (OAuth2) | Fetch unread emails, dedup, auto-ingest into CRM |
| Frontend | React + Vite | Fast SPA, component-based, Recharts for data viz |
| ORM | SQLAlchemy | Mature, type-safe, supports all PostgreSQL features |

---

## Project Structure

```
crm-agent-platform/
├── backend/
│   ├── agent/
│   │   └── triage_agent.py        # ReAct autonomous agent
│   ├── api/
│   │   ├── main.py                # FastAPI app + core endpoints
│   │   ├── dashboard.py           # Dashboard summary endpoints
│   │   ├── analytics.py           # Sentiment trend, contacts, threads
│   │   ├── ingest_email.py        # Email ingestion endpoint
│   │   ├── gmail_api.py           # Gmail sync + status endpoints
│   │   └── rag_api.py             # RAG debug search endpoint
│   ├── database/
│   │   ├── db.py                  # SQLAlchemy engine + session
│   │   └── models.py              # All ORM models
│   ├── rag/
│   │   ├── create_kb.py           # KB seeding script (PostgreSQL + ChromaDB)
│   │   └── retriever.py           # Vector search (ChromaDB)
│   ├── services/
│   │   ├── email_classifier.py    # LLM classification with full schema
│   │   ├── heuristic_engine.py    # Fast pre-filter (spam/security/legal)
│   │   ├── thread_service.py      # Thread history retrieval
│   │   ├── ticket_service.py      # Ticket CRUD
│   │   ├── action_service.py      # Action logging
│   │   ├── gmail_service.py       # Gmail OAuth2 + email fetch/parse
│   │   └── load_dataset.py        # Seed emails from JSON
│   ├── schemas/
│   │   └── email_schema.py        # Pydantic request schemas
│   ├── create_tables.py           # DB table creation
│   └── .env                       # Environment variables (not committed)
├── frontend/
│   └── app.py                     # Streamlit dashboard (legacy)
├── frontend-react/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── MissionControl.jsx  # Inbox, metrics, tickets
│   │   │   ├── ThreadWorkspace.jsx # Thread timeline + contact profile
│   │   │   ├── Analytics.jsx       # Charts: category, sentiment, trend
│   │   │   ├── RagDebug.jsx        # ChromaDB chunk search
│   │   │   └── BulkOperations.jsx  # Process all / single email
│   │   ├── App.jsx                 # Router + sidebar layout
│   │   ├── App.css                 # Dark theme design system
│   │   ├── api.js                  # Axios API client
│   │   └── constants.js            # Badge colors, icons
│   └── package.json
├── kb/
│   ├── pricing_policy.md
│   ├── sla_policy.md
│   ├── refund_policy.md
│   ├── api_docs.md
│   ├── compliance_faq.md
│   └── escalation_matrix.md
├── data/
│   └── email-data-advanced.json   # 60 emails, 30 threads
├── requirements.txt
├── .gitignore
├── chroma_db/                     # ChromaDB persistent vector store (auto-created)
└── README.md
```

---

## Setup Guide

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- [Ollama](https://ollama.ai) installed and running
- llama3 model pulled: `ollama pull llama3`

### 1. Clone & create virtual environment

```bash
git clone https://github.com/YOUR_USERNAME/crm-agent-platform.git
cd crm-agent-platform
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/crm_agent
```

### 4. Create the database

In pgAdmin or psql:

```sql
CREATE DATABASE crm_agent;
```

### 5. Create tables

```bash
cd backend
python create_tables.py
```

### 6. Load email dataset

```bash
python services/load_dataset.py
```

### 7. Seed the knowledge base

```bash
python rag/create_kb.py
```

### 8. Start the backend

```bash
uvicorn api.main:app --reload --port 8000
```

### 9. Start the React frontend (new terminal)

```bash
cd frontend-react
npm install
npm run dev
```

Opens at `uvicorn api.main:app --reload --port 8000`

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:pass@localhost:5432/crm_agent` |
| `GMAIL_CREDENTIALS_FILE` | Path to OAuth credentials file | `credentials.json` |
| `GMAIL_TOKEN_FILE` | Path to saved OAuth token | `token.json` |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest/` | Ingest a new email with deduplication |
| POST | `/process-email/{id}` | Run agent on email, save classification + ticket |
| POST | `/process-all-emails` | Bulk process all emails |
| POST | `/agent/dry-run/{id}` | Agent planning mode — no execution |
| GET | `/dashboard/summary` | Email + ticket counts |
| GET | `/dashboard/emails` | All emails for inbox view |
| GET | `/dashboard/categories` | Category distribution |
| GET | `/dashboard/sentiment` | Sentiment distribution |
| GET | `/dashboard/tickets` | Ticket priority distribution |
| GET | `/tickets` | All tickets |
| GET | `/analytics/sentiment-trend` | Time-series sentiment per sender |
| GET | `/analytics/category-breakdown` | Category breakdown by date range |
| GET | `/contacts/{email}` | Contact profile with churn signals |
| PATCH | `/contacts/{email}/status` | Update contact status |
| GET | `/threads/contact/{email}` | All threads for a contact |
| GET | `/rag/search?q=...` | RAG debug — chunks + similarity scores |
| GET | `/thread/{thread_id}` | Full thread history |
| GET | `/gmail/status` | Check Gmail OAuth authentication status |
| POST | `/gmail/sync` | Fetch unread Gmail emails and ingest into CRM |

Full interactive docs available at: `http://localhost:8000/docs`

---

## Agent Architecture

The triage agent uses a **ReAct (Reasoning + Acting)** loop:

```
Thought → Action → Observation → Thought → ...
```

### Tools available
- `tool_get_thread_history` — fetch full conversation context from DB
- `tool_search_knowledge_base` — RAG search across 6 KB documents
- `tool_create_ticket` — create support ticket
- `tool_escalate_to_human` — route to human with pre-filled brief
- `tool_flag_legal` — route to legal team
- `tool_flag_security` — route to security team
- `tool_flag_compliance` — route to compliance team
- `tool_draft_reply` — generate contextual reply using RAG context

### Hard rules enforced
- Maximum **6 tool calls** per email — if unresolved, escalate to human
- **No auto-reply** for: Security, Legal, Spam, Internal, Critical urgency
- **Confidence < 0.70** → automatically flags for human review
- Every agent run produces a structured **reasoning trace** stored in DB

---

## RAG Pipeline

1. KB documents (`kb/*.md`) are chunked into 300–500 token segments
2. Each chunk is embedded using `sentence-transformers/all-MiniLM-L6-v2`
3. Embeddings stored in both PostgreSQL `knowledge_chunks` table (text/metadata) and ChromaDB (vectors)
4. On each email, top-k chunks retrieved via **ChromaDB similarity search** — returns IDs matched back to PostgreSQL for full chunk data
5. Retrieved chunks injected into LLM prompt as grounding context

### Re-seed KB after changes

```bash
cd backend
python rag/create_kb.py
```

---

## LLM Classification Schema

```json
{
  "category": "Complaint|Billing|Refund|Bug Report|Feature Request|Security|Legal|Compliance|Sales|Spam|Internal|General Inquiry",
  "sentiment": "Positive|Neutral|Negative|Mixed",
  "sentiment_score": 0.0,
  "urgency": "Critical|High|Medium|Low",
  "requires_human": false,
  "escalation_reason": null,
  "suggested_reply": null,
  "confidence": 0.91,
  "reasoning": "...",
  "detected_entities": {
    "order_ids": [],
    "ticket_ids": [],
    "monetary_amounts": [],
    "deadlines": [],
    "products_mentioned": []
  }
}
```

---

## Special Scenario Handling

| Scenario | Handling |
|---|---|
| Ransomware threat (msg_038) | Heuristic detects BTC/ransomware → flag_security → escalate → NO auto-reply |
| GDPR Article 20 request (msg_052) | Compliance flag → legal team → acknowledgement citing 30-day window |
| Legal cease & desist (msg_020) | Legal flag → legal@platform.com → NO auto-reply, no liability admission |
| Karen churn threat (msg_033) | Sentiment deterioration alert → retention playbook → Senior CSM escalation |
| Bob SLA breach + legal (msg_060) | Full thread retrieved → SLA credit calculated → flag_legal → escalate with brief |
| Spam (msg_031 Nigerian prince) | Heuristic keyword match → marked Spam → no LLM call, no reply |

---

## Architectural Decisions & Trade-offs

### Why Ollama + llama3 instead of OpenAI?
- **Privacy**: all data stays local, no PII sent to third parties
- **Cost**: zero API cost during development and demo
- **Trade-off**: slower inference than GPT-4, slightly lower quality on complex reasoning

### Why ChromaDB instead of cosine similarity (numpy)?
- **Performance**: ChromaDB handles vector indexing and search natively — no need to load all embeddings into memory on every query
- **Persistence**: embeddings stored on disk in `chroma_db/`, survive restarts without re-seeding
- **Dual storage**: PostgreSQL remains the source of truth for chunk text and metadata; ChromaDB handles only the vector search layer
- **Trade-off**: adds a dependency and a second storage layer; for very large corpora a hosted vector DB (Pinecone, Weaviate) would scale further

### Why sentence-transformers instead of OpenAI embeddings?
- **Local**: no API key, no latency, free
- **Trade-off**: `all-MiniLM-L6-v2` (384 dimensions) is less semantically rich than `text-embedding-3-large` (3072 dimensions)

### Why React + Vite instead of Streamlit?
- **Interactivity**: full SPA with client-side routing, no page reloads
- **Design**: custom dark theme design system with badge chips, urgency-colored cards, animated buttons
- **Charts**: Recharts for pie, bar, and line charts with custom tooltips
- **Trade-off**: requires Node.js and a separate dev server; more setup than Streamlit

---

## Gmail API Integration

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app) → Download as `credentials.json`
4. Place `credentials.json` in `backend/`
5. On first `/gmail/sync` call, a browser window opens for OAuth consent — `token.json` is saved automatically for future runs

### Auth Status Flow

| State | UI Message |
|---|---|
| `credentials.json` missing | ⚠️ Place credentials.json in backend/ and restart |
| `credentials.json` present, no `token.json` | ℹ️ Click Sync — browser OAuth popup will appear |
| `token.json` present | ✅ Gmail authenticated |

### How it works
- Fetches unread emails from `INBOX` label via Gmail API
- Deduplicates by `message-id` header — already-ingested emails are skipped
- Auto-creates Contact and Thread records if they don't exist
- Optionally marks fetched emails as read (`mark_read=true`)
- Synced emails appear instantly in Mission Control and can be processed by the agent

### UI
The **Bulk Operations** page has a Gmail Sync panel with auth status indicator, configurable fetch limit, mark-as-read toggle, and ingested/skipped/fetched counts.

---

## Known Limitations

- Bulk processing 60 emails takes ~5–10 minutes (LLM inference is synchronous)
- No WebSocket real-time updates — dashboard requires manual refresh
- ChromaDB vector index is local/file-based; for very large KB a hosted vector DB would be more scalable
- Gmail sync requires manual OAuth on first run (browser popup); subsequent runs use saved `token.json`
- No authentication on API endpoints (demo only)

---

## Screen Recording Walkthrough

1. Email stream ingestion via `load_dataset.py`
2. Agent reasoning trace for `thread_bob_outage` escalation (msg_060)
3. RAG retrieval debug view — search "SLA credit calculation"
4. Karen churn scenario — sentiment deterioration + escalation
5. Analytics dashboard — category distribution, sentiment trend

---

## Docker Deployment

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Place Gmail credentials
```
backend/credentials.json   ← OAuth credentials from Google Cloud Console
backend/token.json         ← generated on first Gmail sync (optional at start)
```

### 2. Build and start all services
```bash
docker compose up --build
```

This starts 5 containers in order:
| Container | Role | Port |
|---|---|---|
| `crm_postgres` | PostgreSQL database | 5432 |
| `crm_ollama` | Local LLM server | 11434 |
| `crm_ollama_pull` | Pulls llama3 model (one-time) | — |
| `crm_backend` | FastAPI backend | 8000 |
| `crm_backend_init` | Creates tables + seeds data (one-time) | — |
| `crm_frontend` | React app via nginx | 80 |

### 3. Open the app
- Dashboard → `http://localhost`
- API docs → `http://localhost:8000/docs`

### Useful commands
```bash
# Run in background
docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all
docker compose down

# Stop and delete volumes (full reset)
docker compose down -v
```
