"""
app.py — FastAPI application entry point.
Registers all routers, middleware, exception handlers, and manages
the application lifespan (DB pool open/close).
"""
import logging
import sys
import asyncio
import uuid

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# ── Windows event-loop policy (must come before any async code) ────────────
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.config import settings
from app.utils.logging_config import configure_logging
from app.db import init_pool, close_pool, ping
from app.routes import (
    members, sports, coaches, teams, facilities,
    training_sessions, tournaments, fixtures,
    memberships, payments, equipment, reports,
)

# ── Logging ────────────────────────────────────────────────────────────────
configure_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage DB pool lifecycle.  Startup failure aborts the process cleanly."""
    logger.info("Starting WoxuDB (debug=%s)", settings.debug)
    await init_pool()
    yield
    logger.info("Shutting down WoxuDB.")
    await close_pool()


# ── Application factory ────────────────────────────────────────────────────

app = FastAPI(
    title="WoxuDB",
    description="A DBMS project for academic review — FastAPI + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    # Hide /docs and /redoc in production to reduce attack surface
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ── CORS ───────────────────────────────────────────────────────────────────
# Tighten origins list for production deployments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request-ID middleware ──────────────────────────────────────────────────

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach a unique X-Request-ID to every request/response for traceability."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Global exception handlers ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unexpected exceptions.
    Logs full details server-side; never leaks a stack trace to the client.
    """
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.url.path, exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


# ── Static files and templates ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ── API Routers ────────────────────────────────────────────────────────────
app.include_router(members.router,           prefix="/api/members",           tags=["Members"])
app.include_router(sports.router,            prefix="/api/sports",            tags=["Sports"])
app.include_router(coaches.router,           prefix="/api/coaches",           tags=["Coaches"])
app.include_router(teams.router,             prefix="/api/teams",             tags=["Teams"])
app.include_router(facilities.router,        prefix="/api/facilities",        tags=["Facilities"])
app.include_router(training_sessions.router, prefix="/api/sessions",          tags=["Training Sessions"])
app.include_router(tournaments.router,       prefix="/api/tournaments",       tags=["Tournaments"])
app.include_router(fixtures.router,          prefix="/api/fixtures",          tags=["Fixtures"])
app.include_router(memberships.router,       prefix="/api/memberships",       tags=["Memberships"])
app.include_router(payments.router,          prefix="/api/payments",          tags=["Payments"])
app.include_router(equipment.router,         prefix="/api/equipment",         tags=["Equipment"])
app.include_router(reports.router,           prefix="/api/reports",           tags=["Reports"])

# ── Frontend Page Router ───────────────────────────────────────────────────
from app.routes.pages import page_router  # noqa: E402
app.include_router(page_router)


# ── Health endpoint ────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """
    Liveness + readiness probe.
    Performs a cheap SELECT 1 against the pool to confirm DB connectivity.
    Returns HTTP 200 when healthy, HTTP 503 when the DB is unreachable.
    """
    try:
        await ping()
        db_status = "ok"
    except Exception as exc:
        logger.warning("Health check: DB unreachable — %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "unreachable", "service": "WoxuDB"},
        )
    return {"status": "ok", "db": db_status, "service": "WoxuDB"}
