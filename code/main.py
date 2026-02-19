from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
from asyncpg.exceptions import UniqueViolationError
import redis.asyncio as redis
import json
import os
import asyncio

COMPANY_NAME = os.getenv("COMPANY_NAME", "My Company")

app = FastAPI(
    title=f"{COMPANY_NAME} API",
    description=f"API for {COMPANY_NAME}",
    version="1.0.0",
)

# Database connections
db_pool = None
redis_client = None

CACHE_TTL = 60  # seconds

# Cache keys
def _user_cache_key(user_id: int) -> str:
    return f"user:{user_id}"

USERS_LIST_CACHE_KEY = "users:all"


# Models
class UserCreate(BaseModel):
    name: str
    email: str


# Startup/Shutdown
async def _wait_for_postgres(max_attempts=30, delay=1):
    for attempt in range(max_attempts):
        try:
            return await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "mydb"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            )
        except (ConnectionRefusedError, asyncpg.PostgresConnectionError, OSError):
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(delay)


@app.on_event("startup")
async def startup():
    global db_pool, redis_client
    db_pool = await _wait_for_postgres()
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )


@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()


# User endpoints
@app.post("/users")
async def create_user(user: UserCreate):
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, name, email",
                user.name,
                user.email,
            )
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="Email already exists")

    created = dict(row)

    # Cache the individual user and invalidate the users list cache
    try:
        await redis_client.setex(
            _user_cache_key(created["id"]),
            CACHE_TTL,
            json.dumps(created),
        )
        await redis_client.delete(USERS_LIST_CACHE_KEY)
    except Exception:
        # Cache issues should not break API functionality
        pass

    return created


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    cache_key = _user_cache_key(user_id)

    # 1) Cache-first
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # 2) DB fallback
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, email FROM users WHERE id = $1",
            user_id,
        )

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = dict(row)

    # 3) Populate cache
    try:
        await redis_client.setex(cache_key, CACHE_TTL, json.dumps(user_data))
    except Exception:
        pass

    return user_data


@app.get("/users")
async def list_users():
    # 1) Cache-first
    try:
        cached = await redis_client.get(USERS_LIST_CACHE_KEY)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # 2) DB fallback
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, email FROM users ORDER BY id ASC")

    users = [dict(r) for r in rows]

    # 3) Populate cache
    try:
        await redis_client.setex(USERS_LIST_CACHE_KEY, CACHE_TTL, json.dumps(users))
    except Exception:
        pass

    return users

# Run with: uvicorn main:app --reload
