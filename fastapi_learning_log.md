# FastAPI Learning Log — GMS Project

**Date:** July 12, 2026
**Project:** GMS (Gym Management System) — routers for electronics, furniture, equipments, users

## Curriculum status

| Phase | Topic | Status |
|---|---|---|
| 0 | REST/HTTP fundamentals | Done |
| 1 | FastAPI basics (routing, Swagger/Redoc) | Done |
| 2 | Pydantic models + response_model | Done |
| 3 | In-memory data store | Done |
| 4 | Path params + error handling | Done |
| 5 | Full CRUD (POST/PUT/DELETE) | In progress |
| 6 | Query params + validation | Not started |
| 7 | Dependency injection | Not started |
| 8 | Real database | Not started |
| 9 | Auth | Not started |
| 10 | Testing | Not started |
| 11 | Deployment | Not started |

## What got built today

- Pydantic models added to all four routers: `GymElectronics`, `FurnitureDetails`, `GymEquipments`, `UserProfile`.
- Each router got a module-level in-memory list acting as a fake DB (`electronic_items`, `all_furniture`, `all_gym_equipments`, `all_users`).
- POST endpoints for all four that actually append to their store and return `status_code=201`.
- GET-all endpoints for all four with proper `response_model`/return-type annotations (`list[Model]`).
- GET-by-id with real 404 handling built for **all four routers**: `GET /electronics/{electro_id}`, `GET /furniture/{fur_id}`, `GET /gym_equipments/{gym_equip_id}`, `GET /users/{user_id}`. Same pattern everywhere: loop, match on the actual ID field (never list index), raise `HTTPException(404)` after the loop if nothing matched.
- Dropped some scratch/leftover endpoints from `users.py` (`fetch_trainer`, `list_trainers`, `/items/{item_id}`) that weren't part of the actual gym domain — cleaner file now, only user CRUD remains.

## Bugs found and fixed (in order)

1. **Copy-paste bug** — `furniture.py`/`equipments.py` both had a function named `list_free_weights` with an unrelated docstring. Fixed names/docstrings to match actual behavior.
2. **Missing response type** — `list_furniture` had no return type annotation at all; Swagger showed nothing useful. Fixed with `-> list[FurnitureDetails]`.
3. **Type vs. instance confusion** — wrote `list[all_furniture]` (a variable/instance) instead of `list[FurnitureDetails]` (the class). Would have crashed at startup.
4. **Variable shadowing** — `add_electronics(electronic_items: GymElectronics)` used the same name as the module-level store `electronic_items`, hiding it inside the function. Renamed the parameter.
5. **Store never populated** — even after fixing the shadowing, the function returned the posted item but never called `.append()`. Store stayed empty forever.
6. **List index vs. field value bug** — `get_electronics` did `electronic_items[electro_id]`, treating the business ID as a list position instead of searching for the matching `.electro_id` field. Fixed with a proper search loop.
7. **Broken loop logic** — the fix above initially had `if/else` inside the loop, returning 404 on the very first non-matching item instead of checking the whole list. Moved the not-found check to after the loop.
8. **Returning a status code as data** — `return status.HTTP_404_NOT_FOUND` sent back `200 OK` with the number `404` as the body, instead of an actual 404 response. Fixed with `raise HTTPException(status_code=404, ...)`.
9. **`fur_count` typed as `str`** instead of `int` — inconsistent with the other models' count fields. Fixed.
10. **`from starlette import status`** — reached past FastAPI into its underlying framework directly. Switched to `from fastapi import status`.

## Still outstanding (pick up next session)

- Minor: `get_user`'s docstring still says "List all users" (copy-pasted from `list_users`) — should describe fetching a single user by id.
- Phase 5: add PUT and DELETE to all four routers, with correct status codes (200/204) and 404 handling on missing IDs, mirroring the GET-by-id pattern already in place.
- `EmailStr` validation on `UserProfile.email_id` is currently reverted to plain `str` — the `email-validator` package install hit an environment mismatch (installed into the wrong Python/venv) and wasn't worth chasing today. Revisit later: confirm `which python3`/`which pip` inside the actual venv used to run the server, install `pydantic[email]` there, fully restart (not reload) the server.

## Key concepts learned

- **Statelessness ≠ no server-side data.** REST's "stateless" means the server doesn't track *who's calling* between requests — it says nothing about whether the server holds data in memory. An in-memory list persists across requests as long as the server process keeps running; it's wiped only on process restart (crash, manual stop, or `--reload` triggering).
- **Type hints on plain variables are not enforced by Python.** `x: list[SomeType] = []` is purely advisory — nothing stops you from appending the wrong type. FastAPI only performs real validation at the request/response boundary, via the function's parameter types and return-type annotation, using Pydantic underneath.
- **Custom Pydantic models vs. builtins in type hints** — mechanically the same enforcement applies to `str`/`int` and to a custom `BaseModel` subclass, but builtins check a single scalar value while a model checks a whole structure (every field, every type). A plain class *not* inheriting from `BaseModel` would not get this treatment automatically.
- **400 vs. 422** — 400 means the request itself is malformed (bad syntax/JSON). 422 means the request is well-formed but fails validation (wrong type, missing field) — this is what FastAPI raises automatically when a Pydantic model rejects incoming data.
- **`return` vs. `raise`** — `return` hands back normal data; `raise HTTPException(...)` interrupts the function and tells FastAPI to build an actual error response with the given status code.
- **List index ≠ record ID.** Never assume an object's ID field matches its position in a list — search by field value instead.
- **Pydantic does lax type coercion by default.** A numeric string like `"25"` sent for a `float` field is silently coerced to `25.0`, not rejected. Only genuinely non-convertible values (e.g. `"twenty-five"`) trigger a 422. Use `Field(strict=True)` or `ConfigDict(strict=True)` to disable coercion and require exact types.
- **Unknown/extra fields in a request body are silently ignored by default** (`extra="ignore"`), not stored and not an error.
- **`Optional[X]` ≠ "field can be omitted."** It only means the value can be `None` — the key must still be present unless you also give it a default (`Optional[X] = None`). Type and requiredness are two separate questions.
- **Mutable default values in Pydantic models are safe**, unlike plain Python function defaults. Each model instance gets its own deep copy of a mutable default (list/dict/set), so `cart1.items.append(...)` never leaks into `cart2.items`. Still idiomatic to write `Field(default_factory=list)` for clarity.

## Full phase roadmap (reference)

0. REST/HTTP fundamentals — verbs, status codes.
1. FastAPI basics — routing, `/docs`, `/redoc`.
2. Pydantic models — `BaseModel`, `response_model`/return-type validation.
3. In-memory data store — module-level list standing in for a DB.
4. Path params + error handling — get-by-id, `HTTPException(404)`.
5. Full CRUD — POST/PUT/DELETE with correct status codes.
6. Query params + validation — filtering, `Field`/`Query` constraints.
7. Dependency injection — `Depends()` for shared logic (e.g., lookup-or-404).
8. Real database — SQLModel/SQLAlchemy + SQLite, swap out the in-memory store.
9. Auth — OAuth2/JWT, lock down write routes.
10. Testing — pytest + `TestClient`, happy path + 404 path.
11. Deployment — Docker, gunicorn+uvicorn workers, env config.
