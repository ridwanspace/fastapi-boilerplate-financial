# Getting Started

> **Navigation:** [README](../../README.md) · [Configuration](configuration.md) · [API Reference](api-reference.md) · [Troubleshooting](troubleshooting.md)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Create your repo from this template](#1-create-your-repo-from-this-template)
- [2. Configure environment](#2-configure-environment)
- [3. Start infrastructure](#3-start-infrastructure)
- [4. Create the test database](#4-create-the-test-database)
- [5. Run migrations](#5-run-migrations)
- [6. Start the server](#6-start-the-server)

---

## Prerequisites

| Tool | Minimum Version | How to check | Install guide |
|---|---|---|---|
| Python | 3.12 | `python --version` | [python.org](https://www.python.org/downloads/) |
| pip | 24+ | `pip --version` | Bundled with Python |
| Docker | 24+ | `docker --version` | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.20+ | `docker compose version` | Bundled with Docker Desktop |
| Git | any | `git --version` | [git-scm.com](https://git-scm.com/) |

> **Note for Windows users:** Use WSL2 (Windows Subsystem for Linux). Running natively on Windows is not supported.

---

## 1. Create your repo from this template

Click the **"Use this template"** button at the top of the [GitHub repository page](https://github.com/ridwanspace/fastapi-boilerplate-financial), then choose **"Create a new repository"**.

Once your new repo is created, clone it and install dependencies:

```bash
git clone git@github.com:<your-username>/<your-repo-name>.git && cd <your-repo-name>

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # On Windows: .venv\Scripts\activate

# Install all dependencies (including dev/test tools)
make dev
# or manually:
pip install -r requirements-dev.txt
```

---

## 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

```bash
# Generate a secure JWT secret (minimum 32 chars):
openssl rand -hex 32
```

**Required values to set in `.env`:**

| Variable | How to get it |
|---|---|
| `JWT_SECRET_KEY` | `openssl rand -hex 32` |
| `GCS_PROJECT_ID` | Your GCP project ID |
| `GCS_BUCKET_NAME` | See GCS setup below |
| `GCS_CREDENTIALS_PATH` | Path to your service account JSON file |

For the full list of environment variables and their defaults, see [Configuration](configuration.md).

### GCS setup — create a service account and bucket

```bash
# 1. Create a service account
gcloud iam service-accounts create fastapi-boilerplate-sa \
  --display-name="FastAPI Boilerplate Service Account" \
  --project=<your-project-id>

# 2. Grant GCS and Cloud SQL access
gcloud projects add-iam-policy-binding <your-project-id> \
  --member="serviceAccount:fastapi-boilerplate-sa@<your-project-id>.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding <your-project-id> \
  --member="serviceAccount:fastapi-boilerplate-sa@<your-project-id>.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# 3. Download the key to the project root (gitignored via *.json)
gcloud iam service-accounts keys create ./service-account.json \
  --iam-account=fastapi-boilerplate-sa@<your-project-id>.iam.gserviceaccount.com

# 4. Create a private GCS bucket
gsutil mb -p <your-project-id> -l asia-southeast1 gs://<your-bucket-name>
```

Then set in `.env`:

```env
GCS_PROJECT_ID=<your-project-id>
GCS_BUCKET_NAME=<your-bucket-name>
GCS_CREDENTIALS_PATH=./service-account.json
```

---

## 3. Start infrastructure

Start PostgreSQL and Redis locally via Docker:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

Verify they're running:

```bash
docker compose -f docker/docker-compose.yml ps
```

You should see both `postgres` and `redis` with status `healthy`.

---

## 4. Create the test database

The test suite requires a separate database. Create it once:

```bash
docker compose -f docker/docker-compose.yml exec postgres \
  psql -U postgres -c "CREATE DATABASE boilerplate_test_db;"
```

---

## 5. Run migrations

Apply the database schema. See [Database Migrations](database-migrations.md) for the full Alembic workflow.

```bash
make migrate
# or:
alembic upgrade head
```

---

## 6. Start the server

```bash
make run
# or (if make can't find uvicorn — e.g. conda env):
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

> **conda users:** All `make` targets use `python -m <tool>` so they resolve through the active conda environment automatically.

The API is now running. Open your browser:

| URL | Description |
|---|---|
| http://localhost:8000/docs | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/api/v1/health | Health check (DB + Redis + GCS) |

See the [API Reference](api-reference.md) for available endpoints and request/response formats.

---

## Related Guides

- [Configuration](configuration.md) — all environment variables
- [Database Migrations](database-migrations.md) — Alembic workflow
- [API Reference](api-reference.md) — endpoint documentation
- [Docker](docker.md) — running via Docker Compose
- [Troubleshooting](troubleshooting.md) — common errors and fixes
- [Back to README](../../README.md)
