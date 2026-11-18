# Young Malang — FastAPI Backend

Production-ready REST + WebSocket API for the Young Malang fast-food & POS platform.

---

## Prerequisites

- Python 3.11+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (optional)

---

## Local Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to point to your local Postgres instance

# 4. Run database migrations
alembic upgrade head

# 5. Seed the database
python -m app.scripts.seed

# 6. Start the development server
uvicorn app.main:app --reload --port 8000
```

---

## Docker Setup

```bash
docker-compose up --build
```

The API will be available at http://localhost:8000 after the database health check passes.

---

## API Documentation

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/ | Health check |

---

## WebSocket Channels

Connect with `?token=<JWT>` query parameter for authenticated channels.

| URL | Purpose |
|-----|---------|
| `ws://localhost:8000/ws/pos` | POS / admin live order feed |
| `ws://localhost:8000/ws/kitchen` | Kitchen display |
| `ws://localhost:8000/ws/rider` | Rider dispatch channel |

---

## Default Admin Credentials

| Field | Value |
|-------|-------|
| Email | admin@youngmalang.com |
| Password | Admin@1234 |

> Change these immediately in production.

---

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/register | Register customer |
| POST | /api/v1/auth/login | Login (returns JWT) |
| GET | /api/v1/menu/items | List food items |
| POST | /api/v1/orders | Place order |
| POST | /api/v1/delivery/check | Check delivery eligibility |
| GET | /api/v1/reports/daily | Daily sales summary |
| GET | /api/v1/pos/tables | List all 30 POS tables |

---

## Credit

**Software Developed by AM Enterprises / 03173712950**
