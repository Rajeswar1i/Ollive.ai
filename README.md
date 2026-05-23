# Ollive.ai — LLM Observability Platform

A full-stack platform for monitoring and observing LLM inference calls. Captures latency, token usage, error rates, and conversation logs across multiple LLM providers with a real-time analytics dashboard.

---

## Demo

| Chat | Dashboard |
|---|---|
| ![Chat](screenshots/1.IndivudualChat.png) | ![Dashboard](screenshots/2.Dashboard.png) |
| ![Conversations](screenshots/3.MultipleChat.png) | ![Dashboard Metrics](screenshots/4.DashboardM.png) |

**Kubernetes pods running:**
![K8s Pods](screenshots/5.K8%20Pods.png)

---

## Features

- **Multi-provider LLM support** — Anthropic Claude, OpenAI, Groq (OpenAI-compatible), Google Gemini
- **Real-time observability dashboard** — total requests, avg/p95 latency, token usage, error rate
- **Conversation history** — browse past conversations and replay messages
- **Event-based logging pipeline** — Redis queue decouples LLM calls from DB writes
- **PII redaction** — emails, phone numbers, SSNs, and credit card numbers stripped from logs
- **REST ingest API** — log inference calls from any external application via HTTP
- **Kubernetes-ready** — full k8s manifests included for self-hosted deployment

---

## Architecture

```
Browser (React)
    │
     ▼
FastAPI Backend (port 8000)
     │
     ├── LLM Wrapper → Anthropic / OpenAI / Gemini
     │        │
     │        └── Redis Queue (RPUSH)
     │                  │
     │              Log Consumer (BLPOP)
     │                  │
     │              PostgreSQL (inference_logs)
     │
     └── REST API → conversations, metrics, ingest


**Stack:**
| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL 16 |
| Queue | Redis 7 |
| Container | Docker, Docker Compose |
| Orchestration | Kubernetes (k8s manifests) |


## Quick Start — Docker Compose

**Prerequisites:** Docker Desktop

    bash
# Clone the repo
git clone <repo-url>
cd ollive-ai

# Set your LLM API key (Groq is pre-configured and free)
# Edit docker-compose.yml → OPENAI_API_KEY with your Groq key
# Get a free key at: https://console.groq.com

# Start everything
docker compose up --build

# App is running at:
#   Frontend:  http://localhost:3000
#   Backend:   http://localhost:8000
#   API Docs:  http://localhost:8000/docs
```

**To stop:**
```bash
docker compose down
```

---

## Quick Start — Kubernetes (Docker Desktop)

**Prerequisites:** Docker Desktop with Kubernetes enabled (Settings → Kubernetes → Enable)

```bash
# Build images
docker compose build

# Deploy all manifests
kubectl apply -f k8s/
kubectl apply -f k8s/   # run twice — namespace needs a moment to propagate

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all -n ollive --timeout=120s

# Port-forward to access locally (run in two separate terminals)
kubectl port-forward svc/frontend 3000:80 -n ollive
kubectl port-forward svc/backend 8000:8000 -n ollive

# App is running at:
#   Frontend:  http://localhost:3000
#   Backend:   http://localhost:8000
```

**Check deployment status:**
```bash
kubectl get pods -n ollive
kubectl get services -n ollive
```

**To tear down:**
```bash
kubectl delete namespace ollive
```

---

## Configuration

Copy `.env.example` to `.env` and set your API keys:

```env
# LLM Provider (openai | anthropic | gemini)
LLM_PROVIDER=openai

# For Groq (OpenAI-compatible, free tier available)
OPENAI_API_KEY=your-groq-api-key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile

# For Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Database (auto-configured in Docker/k8s)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ollive
REDIS_URL=redis://localhost:6379
```

---

## API Reference

### Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/conversations` | Create a new conversation |
| `GET` | `/conversations` | List all conversations |
| `GET` | `/conversations/{id}/messages` | Get messages in a conversation |
| `POST` | `/chat/{conversation_id}` | Send a message (streaming SSE response) |

### Observability

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/metrics` | Dashboard stats (requests, latency, tokens, errors) |
| `POST` | `/ingest` | Log an inference call from an external app |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |

Full interactive docs at **http://localhost:8000/docs**

---

## External Ingest API

Log inference calls from any application without using the built-in LLM wrapper:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "provider": "openai",
    "latency_ms": 842,
    "prompt_tokens": 120,
    "completion_tokens": 85,
    "total_tokens": 205,
    "status": "success",
    "input_preview": "Summarize this document...",
    "output_preview": "The document covers..."
  }'
```

---

## Project Structure

```
ollive-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, lifespan, CORS
│   │   ├── config.py          # Settings (env vars)
│   │   ├── database.py        # Async SQLAlchemy engine
│   │   ├── models/            # ORM models
│   │   ├── routers/           # API route handlers
│   │   │   ├── chat.py        # Streaming chat endpoint
│   │   │   ├── conversations.py
│   │   │   ├── ingest.py      # External log ingestion
│   │   │   └── metrics.py     # Dashboard analytics
│   │   ├── sdk/
│   │   │   ├── llm_wrapper.py # Multi-provider LLM abstraction
│   │   │   ├── queue.py       # Redis RPUSH publisher
│   │   │   └── redact.py      # PII redaction
│   │   └── workers/
│   │       └── log_consumer.py # Redis BLPOP → PostgreSQL
│   ├── alembic/               # DB migrations
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/             # Dashboard, Chat, Logs pages
│   │   └── components/        # UI components
│   ├── Dockerfile
│   └── nginx.conf
├── k8s/
│   ├── namespace.yaml
│   ├── postgres.yaml          # PVC + Deployment + Service
│   ├── redis.yaml
│   ├── backend.yaml           # ConfigMap + Secret + Deployment + Service
│   └── frontend.yaml          # Deployment + NodePort Service
└── docker-compose.yml
```

---

## How the Logging Pipeline Works

1. **LLM call** — `llm_wrapper.py` wraps every provider call and captures latency, token counts, timestamps, and input/output previews
2. **Redaction** — PII is stripped from previews before leaving the wrapper
3. **Publish** — log is serialized to JSON and pushed to Redis with `RPUSH inference_logs`
4. **Consume** — background worker started at app startup uses `BLPOP` to dequeue logs as they arrive
5. **Persist** — worker writes to `inference_logs` table in PostgreSQL
6. **Dashboard** — `/metrics` endpoint aggregates the table with SQL (avg, p95, count, error rate)

This decouples the hot path (LLM response streaming) from the DB write, so logging never blocks the user.

---

## Schema Design Decisions

### `inference_logs` table
Stores one row per LLM inference call.

| Column | Type | Reason |
|---|---|---|
| `id` | UUID | Globally unique, safe to expose in APIs |
| `conversation_id` | UUID (FK) | Groups logs by session for per-conversation analytics |
| `model` / `provider` | varchar | Kept separate — same model can be served by different providers |
| `latency_ms` | integer | Millisecond precision is sufficient; avoids float precision issues |
| `prompt_tokens` / `completion_tokens` / `total_tokens` | integer | Split so cost can be calculated per-direction (input vs output pricing differs) |
| `request_timestamp` / `response_timestamp` | timestamptz | Both stored so latency can be recomputed independently |
| `status` | varchar | `success` or `error` — avoids a boolean that can't express future states |
| `input_preview` / `output_preview` | text | Truncated, PII-redacted snapshots for debugging without storing full prompts |

### `conversations` + `messages` tables
- Conversations track status (`active` / `cancelled`) so the UI can gate further messages
- Messages store `role` (`user` / `assistant`) and `content` — minimal schema that matches the OpenAI message format directly

### Why PostgreSQL
- Native `percentile_cont` for p95 latency without application-level sorting
- JSONB available if schema needs to flex later
- Simple operational model for a self-hosted deployment

---

## Tradeoffs

| Decision | What was chosen | What was traded off |
|---|---|---|
| Redis queue for logging | Decoupled async writes, no blocking on hot path | Added operational complexity (one more service); logs lost if Redis crashes before consume |
| Single consumer worker | Simple, no concurrency bugs | Won't scale past ~1k logs/sec without multiple consumers |
| Store previews, not full prompts | Privacy-safe by default, smaller storage | Loses ability to replay or audit exact prompts |
| Groq as default provider | Free tier, fast inference, no credit card | Dependent on third-party availability; swap `OPENAI_BASE_URL` to self-host |
| Docker Desktop k8s | Zero additional infrastructure | Single-node only; not production-grade (no HA, no persistent volume replication) |
| Alembic for migrations | Versioned, reproducible schema changes | Adds a migration step on first boot (handled by `entrypoint.sh` retry loop) |

---

## What I Would Improve With More Time

- **Authentication** — no auth currently; add JWT or API key gating on the ingest endpoint at minimum
- **Full prompt storage** — store complete messages in an encrypted column for audit use cases, with access controls
- **Multiple consumer workers** — scale log throughput by running N consumers with a shared Redis connection
- **Alerting** — webhook or email when error rate exceeds a threshold
- **Cost tracking** — map token counts to per-provider pricing and show estimated cost per conversation
- **Retention policy** — auto-delete inference logs older than N days to control storage growth
- **Tests** — add pytest integration tests for the ingestion pipeline and unit tests for the redaction logic
- **Helm chart** — replace raw k8s YAML with a Helm chart for easier config management across environments

---

## Architecture Notes

### Ingestion Flow
```
LLM call finishes
    → llm_wrapper.py captures metadata + PII-redacts previews
    → publish_log() serializes to JSON, RPUSH to Redis "inference_logs" key
    → log_consumer (background asyncio task) BLPOP with 5s timeout
    → process_log() writes one row to inference_logs table
    → /metrics endpoint reads aggregated stats on demand
```

External apps skip the wrapper and POST directly to `/ingest`, which writes to the same table via the same path.

### Logging Strategy
- Logs are **fire-and-forget** from the LLM wrapper — a failure to publish never surfaces to the user
- PII redaction runs **before** the log enters the queue — data is clean at rest
- Previews are capped in length to bound storage per request

### Scaling Considerations
- **Queue fan-out**: replace Redis list with Redis Streams or Kafka to support multiple independent consumers (e.g., one for DB, one for S3 archival)
- **Read scaling**: the `/metrics` endpoint runs a full table scan — add a materialized view or time-series rollup table once row counts exceed ~1M
- **Worker scaling**: run multiple `log_consumer` processes (separate pods in k8s) — each `BLPOP` is atomic so no double-processing
- **Backend scaling**: FastAPI is stateless; add replicas behind a load balancer with no changes needed

### Failure Handling Assumptions
- **Redis down at publish time**: `publish_log` catches all exceptions silently — the LLM call still succeeds, log is dropped. Acceptable for observability (losing a log is better than failing a user request)
- **DB down at consume time**: consumer catches exceptions, sleeps 1s, and retries — message stays in the Redis queue until DB recovers
- **Backend crash**: unprocessed Redis messages survive restart since Redis persists the list in memory (and can be configured with AOF/RDB for durability)
- **Migration failure on boot**: `entrypoint.sh` retries `alembic upgrade head` up to 10 times with 3s delay — handles slow DB startup in Docker/k8s
