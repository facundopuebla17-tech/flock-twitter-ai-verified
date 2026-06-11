# Flock Twitter AI Verified Backend

Initial FastAPI backend scaffold for a Twitter clone.

## Stack

- FastAPI
- SQLAlchemy 2.0 async ORM
- PostgreSQL
- Alembic
- Pydantic settings for environment-based configuration

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Update `.env`, then run:

```powershell
fastapi dev app/main.py
```

## Migrations

```powershell
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

