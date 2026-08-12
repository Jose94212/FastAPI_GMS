# Gym Management System (GMS)

A FastAPI backend for running a gym: members, staff, lockers, membership plans and subscriptions, and inventory tracking for electronics, furniture, and equipment. Built with SQLModel on top of SQLAlchemy, JWT-based login, and a full pytest suite.

## Features

- **Members & Staff** - staff are also members under the hood: creating a staff record automatically creates its linked member row (shared login credentials), and deleting one cascades to the other.
- **Authentication** - JWT login via email/password (bcrypt-hashed), with anti-enumeration on failed logins (wrong password and unknown email return identical errors).
- **Role-based access** - two roles, `member` and `owner`. Electronics/furniture/equipment routes require any logged-in member to read/create/update, but only an `owner` can delete.
- **Lockers** - allocated to a member or staff (or both), never neither - enforced by a validator, both on create and on update.
- **Membership plans & subscriptions** - plans define pricing/duration; subscriptions link a member to a plan for a date range.
- **Cascading deletes** - deleting a member removes their staff row, subscriptions, and locker in one transaction, via SQLAlchemy `Relationship(cascade_delete=True)`.
- **Structured logging** - every resource logs creates/updates/deletes at INFO, and 404s/auth failures/validation rejections at WARNING.
- **Tested** - unit tests (pure logic, no DB) and integration tests (full app against an isolated in-memory database per test).

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) - web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - ORM (SQLAlchemy + Pydantic combined)
- [PostgreSQL](https://www.postgresql.org/), hosted on [Neon](https://neon.com/) - database (serverless, scales to zero when idle, no deletion on inactivity)
- [Alembic](https://alembic.sqlalchemy.org/) - schema migrations
- [PyJWT](https://pyjwt.readthedocs.io/) + [bcrypt](https://pypi.org/project/bcrypt/) - authentication
- [pytest](https://docs.pytest.org/) - testing
- [Render](https://render.com/) - hosting (free web service, deploys from `main` on push)

## Project structure

```
GMS/
  main.py              # app entry point, router wiring, logging config
  auth.py              # password hashing, JWT issuing/decoding, auth dependencies
  database.py           # DB engine, session dependency
  seed_data.py          # populates the DB with sample data
  .env                  # DATABASE_URL, SECRET_KEY - not committed, see Setup below
  alembic/               # migration scripts (alembic/versions/) and env.py
  alembic.ini             # Alembic config
  gms_assets/
    members/            # members + login
    staff/               # staff (linked to a member row)
    locker/              # lockers
    membership_plans/    # subscribable plans
    member_subscriptions/# member-to-plan subscriptions
    electronics/          # inventory
    furniture/             # inventory
    equipment/              # inventory
  tests/
    unit/                # pure logic - no DB, no HTTP client
    integration/          # full app + isolated in-memory DB via the client fixture
  conftest.py            # the `client` pytest fixture used by integration tests
```

Each resource folder follows the same pattern: `schemas.py` (request/response shapes + validation), `model.py`/`models.py` (the DB table), `router.py` (the endpoints).

## Getting started

### Prerequisites

- Python 3.11+
- A [Neon](https://neon.com/) account (free tier) with a project created, for the Postgres connection string

### Setup

```bash
git clone <this-repo>
cd GMS
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root (never committed - it's in `.gitignore`):

```
DATABASE_URL=<your Neon connection string>
SECRET_KEY=<a random secret - generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
```

Then apply the schema to your database:

```bash
alembic upgrade head
```

### Run it

```bash
uvicorn main:gms --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive Swagger docs - every endpoint, request/response schema, and a "Try it out" button live there.

### Sample data (optional)

```bash
python3 seed_data.py
```

Populates the database with sample members, staff, plans, subscriptions, and inventory. Every seeded member/staff account logs in with the password `password123`.

### Schema changes

Table structure is managed by Alembic, not by the app itself - nothing runs automatically on startup. After changing a model:

```bash
alembic revision --autogenerate -m "describe the change"
```

Review the generated file in `alembic/versions/` (autogenerate isn't perfect), then apply it:

```bash
alembic upgrade head
```

## Authentication

Log in via `POST /members/token`, form-encoded, using your email as `username`:

```bash
curl -X POST http://127.0.0.1:8000/members/token \
  -d "username=alex.morgan@ironpeak.gym&password=password123"
```

Returns a bearer token. Pass it as `Authorization: Bearer <token>` on routes that require login (electronics, furniture, equipment - membership plans/subscriptions/members/staff/locker are currently open, no auth dependency yet).

## Resources

| Resource | Prefix | Auth required | Notes |
|---|---|---|---|
| Members | `/members` | No (except where noted) | `/members/token` issues login tokens |
| Staff | `/staff` | No | Creating staff also creates a linked member row |
| Locker | `/locker` | No | Must be allocated to a member or staff |
| Membership Plans | `/plans` | No | |
| Subscriptions | `/subscriptions` | No | Links a member to a plan |
| Electronics | `/electronics` | Yes (owner for delete) | |
| Furniture | `/furniture` | Yes (owner for delete) | |
| Equipment | `/gym_equipment` | Yes (owner for delete) | Auto-computes total cost and next maintenance date if left blank |

## Running tests

```bash
pytest -v
```

- `tests/unit/` - no database, no HTTP client. Tests validators and pure functions directly (e.g. password hashing, the locker orphan-check) and router functions with a mocked DB session.
- `tests/integration/` - spins up the full FastAPI app against a throwaway in-memory SQLite database per test (via the `client` fixture in `conftest.py`), and drives it through real HTTP requests. Never touches Neon, regardless of what `DATABASE_URL` points to.

Run just one or the other with `pytest tests/unit` or `pytest tests/integration`.

## Deployment

Live on [Render](https://render.com/) (free web service tier), database on [Neon](https://neon.com/) (free Postgres). Deploys automatically on every push to `main`.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:gms --host 0.0.0.0 --port $PORT`
- **Environment variables (set in Render's dashboard, not committed):** `DATABASE_URL`, `SECRET_KEY`
- **Schema:** managed by Alembic, applied directly against Neon (`alembic upgrade head`) - not run automatically on deploy, since the app's startup no longer touches the schema at all.

Note: Render's free tier spins the service down after 15 minutes of inactivity - the first request after a period of idle takes about a minute to respond while it cold-starts.

## Possible future improvements

- **Async DB access** - routes are currently synchronous (`def`, not `async def`); FastAPI runs these in a thread pool so a slow Postgres round-trip doesn't block other requests, which is sufficient at this app's scale. Worth revisiting (`asyncpg` + SQLAlchemy's async engine) if this ever needs to handle real concurrent load.
- **CI** - running the test suite automatically on every push (e.g. GitHub Actions), rather than only locally before pushing.
- **Docker** - containerizing the app for portability across hosts, independent of Render's buildpack.
