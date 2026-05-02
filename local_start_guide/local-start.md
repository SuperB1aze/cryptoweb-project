# Local Start Guide

This folder contains the local-only helper files for starting the project:

- `local-start.md` - this guide.
- `seed_mock_data.py` - idempotent mock data loader.

The project still expects infrastructure files in the repository root:

- `.env` - local development secrets and database connection values.
- `docker-compose.yml` - PostgreSQL 16 container.
- `certs/private.pem` and `certs/public.pem` - local JWT keys.

Do not commit `.env` or `certs/`. They are local machine files and are already ignored by git.

## Environment

Create `.env` in the repository root. Keep the real values private and take them from your local setup or private notes.

The app and Docker Compose need database settings, JWT key paths, and JWT algorithm settings. Do not keep public env templates with real or reusable values.

PostgreSQL can be published on local port `5433` to avoid conflicts with a locally installed PostgreSQL on `5432`.

## Start Order

Run these commands from the repository root:

```powershell
docker compose up -d
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python local_start_guide\seed_mock_data.py
python main.py
```

Swagger UI will be available at:

```text
http://127.0.0.1:8000/api/v1/docs
```

## Mock Accounts

Seeded login accounts:

- `admin@example.com`
- `alice@example.com`
- `bob@example.com`

All seeded users use the password `password123`.
