
# Binance Screener — Setup & Run

A lightweight Flask app for real‑time crypto screening.

## Features
- Periodic data refresh (server-side).
- Admin panel to toggle symbols.
- Rate limiting & caching.

---

## 1) Quick start (Docker Compose) — **recommended**

### Prerequisites
- Docker & Docker Compose

### Steps
1. Unpack the project and create an `.env` in the root (same folder as `docker-compose.yml`). Start from this example:
   ```env
   # Flask
   SECRET_KEY=change-me
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=adminpass
   REFRESH_SECONDS=60
   BINANCE_BASE_URL=https://api.binance.com

   # Database (Postgres in docker-compose)
   DATABASE_URL=postgresql+psycopg2://sprintero:sprintero@db:5432/sprintero

   # Limiter storage (Redis in docker-compose)
   LIMITER_STORAGE_URL=redis://redis:6379/0
   ```

2. Build & run:
   ```bash
   docker compose up --build
   ```

3. Open the app:
   - Web UI: http://localhost:8000
   - Admin:  http://localhost:8000/admin  (login with `ADMIN_USERNAME` / `ADMIN_PASSWORD`)

> The container waits for Postgres, runs migrations automatically, and launches Gunicorn (`entrypoint.sh`).

---

## 2) Local development (Python venv)

### Prerequisites
- Python 3.11+
- PostgreSQL (or use SQLite for quick testing)

### Steps
1. Create and activate venv:
   ```bash
   cd web
   python -m venv .venv
   source .venv/bin/activate     # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a `.env` in **project root** (one level above `web/`) or export env vars. Example with **SQLite** for quick run:
   ```env
   SECRET_KEY=dev-secret
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=adminpass
   REFRESH_SECONDS=60
   DATABASE_URL=sqlite:///app.db
   LIMITER_STORAGE_URL=memory://
   ```

3. Initialize DB and run dev server:
   ```bash
   export FLASK_APP=sprintero
   flask db upgrade || (flask db init && flask db migrate && flask db upgrade)
   flask run --host 0.0.0.0 --port 8000
   ```

4. Open:
   - http://localhost:8000
   - http://localhost:8000/admin

> To switch to Postgres locally, set `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname` and ensure the DB exists.

---

## Configuration reference

All configuration keys come from environment variables (see `web/sprintero/config.py`):

| Variable              | Default / Example                                               | Notes                               |
|-----------------------|-----------------------------------------------------------------|-------------------------------------|
| `SECRET_KEY`          | `dev-secret`                                                    | Change in production                 |
| `DATABASE_URL`        | `sqlite:///app.db` or `postgresql+psycopg2://…`                 | Used by SQLAlchemy & migrations      |
| `ADMIN_USERNAME`      | `admin`                                                         | Admin login                          |
| `ADMIN_PASSWORD`      | `adminpass`                                                     | Admin password                       |
| `BINANCE_BASE_URL`    | `https://api.binance.com`                                       | API endpoint                         |
| `REFRESH_SECONDS`     | `60`                                                            | Data refresh frequency               |
| `LIMITER_STORAGE_URL` | `memory://` (dev) or `redis://redis:6379/0` (compose)           | Rate limiter backend                 |

---

## Notes
- Static assets live in `web/sprintero/blueprints/main/static/`.
- If you change the DB schema, run migrations inside the web container:
  ```bash
  docker compose exec web flask db migrate -m "Your message"
  docker compose exec web flask db upgrade
  ```

## Troubleshooting
- **Stuck on start (waiting for DB):** ensure Postgres container is healthy. The app retries DB connection for ~2 minutes.
- **Rate limit errors in dev:** switch `LIMITER_STORAGE_URL=memory://` or adjust limits in `extensions.py`.
- **Port already in use:** change host port in `docker-compose.yml` (`8000:8000`).

---

---
## Support the Project 💖
If you like this project and want to support its development, you can buy me a coffee:  
[☕ Donate via Ko-fi](https://ko-fi.com/cryptoscreeners)
