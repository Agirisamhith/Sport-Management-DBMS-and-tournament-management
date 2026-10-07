"""
db.py — Database connection management using psycopg3.

Provides:
  - An async connection pool (initialised once at application startup).
  - A FastAPI dependency (get_db) that yields a connection per request.
  - A get_connection() async context manager for non-route code.
  - A ping() helper used by the /health endpoint.
"""
import logging
import psycopg
from psycopg_pool import AsyncConnectionPool, PoolTimeout
from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global pool — initialised at application startup via lifespan
# ---------------------------------------------------------------------------
pool: AsyncConnectionPool | None = None


def _build_conninfo() -> str:
    return (
        f"host={settings.db_host} "
        f"port={settings.db_port} "
        f"dbname={settings.db_name} "
        f"user={settings.db_user} "
        f"password={settings.db_password} "
        f"connect_timeout={int(settings.db_connect_timeout)}"
    )


async def init_pool() -> None:
    """
    Create the async connection pool and verify connectivity.
    Raises RuntimeError if the database cannot be reached, which will
    prevent the application from starting up in a broken state.
    """
    global pool
    conninfo = _build_conninfo()
    logger.info(
        "Opening connection pool (min=%d, max=%d) → %s:%d/%s",
        settings.db_pool_min,
        settings.db_pool_max,
        settings.db_host,
        settings.db_port,
        settings.db_name,
    )
    pool = AsyncConnectionPool(
        conninfo=conninfo,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        timeout=settings.db_pool_timeout,
        open=False,
    )
    try:
        await pool.open(wait=True, timeout=settings.db_connect_timeout)
    except Exception as exc:
        logger.critical("Failed to open connection pool: %s", exc, exc_info=True)
        raise RuntimeError(
            f"Cannot connect to PostgreSQL at {settings.db_host}:{settings.db_port}. "
            f"Check DB_HOST / DB_PASSWORD environment variables."
        ) from exc

    # Smoke-test: execute a trivial query to confirm the pool works
    try:
        await ping()
        logger.info("Database connection pool is healthy.")
    except Exception as exc:
        logger.critical("Pool opened but smoke-test query failed: %s", exc, exc_info=True)
        await pool.close()
        raise RuntimeError("Database smoke-test failed after pool open.") from exc


async def close_pool() -> None:
    """Close the connection pool gracefully. Called once at shutdown."""
    global pool
    if pool:
        logger.info("Closing connection pool.")
        await pool.close()
        pool = None


async def ping() -> bool:
    """
    Execute a cheap query to verify DB reachability.
    Returns True on success, raises on failure.
    Used by the /health endpoint.
    """
    if pool is None:
        raise RuntimeError("Connection pool is not initialised.")
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return True


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_db():
    """
    FastAPI dependency that provides a database connection from the pool.

    Usage:
        conn: psycopg.AsyncConnection = Depends(get_db)

    Raises HTTP 503 if the pool is unavailable or exhausted.
    """
    if pool is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database pool is not available.")
    try:
        async with pool.connection() as conn:
            yield conn
    except PoolTimeout:
        from fastapi import HTTPException
        logger.error("Pool timeout: no connection available within %.1fs", settings.db_pool_timeout)
        raise HTTPException(
            status_code=503,
            detail="The server is under heavy load. Please try again shortly.",
        )


# ---------------------------------------------------------------------------
# Utility context manager (for non-route code such as setup scripts)
# ---------------------------------------------------------------------------

from contextlib import asynccontextmanager  # noqa: E402


@asynccontextmanager
async def get_connection():
    """Async context manager that yields a connection from the pool."""
    if pool is None:
        raise RuntimeError("Connection pool is not initialised. Call init_pool() first.")
    async with pool.connection() as conn:
        yield conn
