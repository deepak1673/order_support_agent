# Order & Delivery Support Agent

A LangGraph ReAct agent (Gemini 2.5 Flash + LangChain tools) that answers
order, shipment and ticket questions for authenticated customers. Business
data lives in SQLite; the LLM only reaches it through customer-scoped tools.

For the full design, roadmap and known gaps, see
[ORDER_SUPPORT_AGENT_README.md](ORDER_SUPPORT_AGENT_README.md).

## What's implemented
- LangGraph `StateGraph`: agent node + tool node, looping until the model stops calling tools.
- Seven LangChain tools (orders, tracking, tickets, refund eligibility, cancellation), built per request and closed over the authenticated `customer_id`, so the model never supplies its own customer identity.
- JWT auth (`/auth/register`, `/auth/login`) with PBKDF2-hashed passwords.
- SQLite + SQLAlchemy persistence: customers, orders, shipments, tickets, conversations, messages.
- Persisted multi-turn conversation memory.
- FastAPI backend, Streamlit chat UI, and a CLI demo.

## Still mocked / missing
- Shipment tracking is seeded sample data (no AfterShip).
- Cancellation executes immediately; no human approval step.
- No RAG/policy retrieval, rate limiting, observability or eval suite.
- SQLite instead of Postgres.

## Setup
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # set GOOGLE_API_KEY and JWT_SECRET (JWT_SECRET is required)
python seed.py          # creates order_support.db with demo data
```

Demo logins (password `password123`):
- `aditi@example.com` (C1024): `ORD123` shipped/delayed, `ORD124` delivered
- `marcus@example.com` (C2001): `ORD200` processing, still cancellable

## Run
```bash
python demo.py                    # CLI: three sample queries, prints tool trace
uvicorn main:app --reload         # API on :8000
streamlit run streamlit_app.py    # chat UI (API must be running)
```

```bash
TOKEN=$(curl -s -X POST localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"email":"aditi@example.com","password":"password123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST localhost:8000/chat -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" -d '{"message":"Where is my order ORD123?"}'
```

## File map
```
agent.py          LangGraph ReAct graph + run_agent()
tools.py          LangChain tools scoped to one customer_id
crud.py           data-access functions used by tools and API
db.py             SQLAlchemy models + engine
security.py       password hashing + JWT
seed.py           creates and seeds the SQLite DB
main.py           FastAPI app (auth, conversations, /chat)
streamlit_app.py  chat UI
demo.py           CLI runner
mock_data.py      legacy in-memory store (unused)
```
