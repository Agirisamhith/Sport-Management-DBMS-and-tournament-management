"""
routes/reports.py — Report endpoints that expose the SQL views.
Each endpoint wraps its query in error handling so view/DB failures
return a clean HTTP 500 rather than leaking raw error messages.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()
logger = logging.getLogger(__name__)


async def _run_report(view_name: str, conn: psycopg.AsyncConnection) -> list[dict]:
    """Execute a report view query with error handling."""
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(f"SELECT * FROM {view_name}")  # noqa: S608 – view name is a hard-coded constant
            return await cur.fetchall()
    except Exception as e:
        logger.error("Report query failed for view '%s': %s", view_name, e, exc_info=True)
        handle_db_error(e)


@router.get("/active-members")
async def report_active_members(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Active members with their membership plan and days remaining."""
    return await _run_report("v_active_members", conn)


@router.get("/revenue-by-plan")
async def report_revenue_by_plan(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Revenue breakdown by membership plan."""
    return await _run_report("v_revenue_by_plan", conn)


@router.get("/tournament-results")
async def report_tournament_results(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Tournament leaderboard with rankings."""
    return await _run_report("v_tournament_results", conn)


@router.get("/equipment-status")
async def report_equipment_status(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Equipment stock status with loan summary."""
    return await _run_report("v_equipment_status", conn)


@router.get("/overdue-equipment")
async def report_overdue_equipment(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Members with overdue equipment returns."""
    return await _run_report("v_overdue_equipment", conn)


@router.get("/team-roster")
async def report_team_roster(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Complete team roster with occupancy data."""
    return await _run_report("v_team_roster", conn)


@router.get("/upcoming-sessions")
async def report_upcoming_sessions(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Training sessions in the next 30 days."""
    return await _run_report("v_upcoming_sessions", conn)


@router.get("/expiring-memberships")
async def report_expiring_memberships(conn: psycopg.AsyncConnection = Depends(get_db)):
    """Memberships expiring within 30 days."""
    return await _run_report("v_expiring_memberships", conn)
