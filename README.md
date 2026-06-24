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

## Current Features

### Authentication

Implemented and tested:

* User registration (`POST /api/v1/auth/register`)
* User login (`POST /api/v1/auth/login`)
* Password hashing with Argon2
* JWT access token generation
* Email uniqueness validation
* Username uniqueness validation

### Verified Behaviors

Registration:

* Returns `201 Created` on success
* Returns `409 Conflict` for duplicate email
* Returns `409 Conflict` for duplicate username

Login:

* Returns JWT access token for valid credentials
* Returns `401 Unauthorized` for invalid credentials

### Current API Endpoints

| Method | Endpoint                | Description                      |
| ------ | ----------------------- | -------------------------------- |
| POST   | `/api/v1/auth/register` | Register a new user              |
| POST   | `/api/v1/auth/login`    | Authenticate user and return JWT |

### Next Steps

* JWT validation
* Current user dependency (`get_current_user`)
* `GET /api/v1/users/me`
* Tweet model and endpoints
* Follow system
* Likes
* Timeline
