# Local Start Guide

This folder contains the local-only helper files for starting the project:

- `local-start.md` - this guide.
- `seed_mock_data.py` - idempotent mock data loader.
- `create-test-db.sh` - creates test role and test DB in a running PostgreSQL container.

The project still expects infrastructure files in the repository root:

- `.env` - local development secrets and database connection values.
- `docker-compose.yml` - PostgreSQL 16 container.
- `certs/private.pem` and `certs/public.pem` - local JWT keys.

Do not commit `.env` or `certs/`. They are local machine files and are already ignored by git.

## Environment

Create `.env` in the repository root. Keep the real values private and take them from your local setup or private notes.

The app and Docker Compose need database settings and JWT settings. Do not keep public env templates with real or reusable values.

For local HTTP development, `REFRESH_COOKIE_SECURE` can be omitted or set to `false`. For HTTPS environments, set it to `true`.

MinIO settings are expected as:

- `MINIO_ENDPOINT_URL`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_NAME`
- `MINIO_PUBLIC_BASE_URL`

If your `.env` currently has only `S3_*` variables, add the `MINIO_*` ones too.

## Start Order

Run these commands from the repository root:

```powershell
docker compose up -d
.\venv\Scripts\activate
pip install -r requirements.txt
sh ./local_start_guide/create-test-db.sh
alembic upgrade head
python local_start_guide\seed_mock_data.py
python main.py
```

Linux/macOS variant:

```bash
docker compose up -d
source venv/bin/activate
pip install -r requirements.txt
sh ./local_start_guide/create-test-db.sh
alembic upgrade head
python local_start_guide/seed_mock_data.py
python main.py
```

Note: `sh ./local_start_guide/create-test-db.sh` is idempotent and can be run repeatedly.

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
