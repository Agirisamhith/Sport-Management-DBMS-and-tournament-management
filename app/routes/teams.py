"""
routes/teams.py — CRUD + team member management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()

_TEAM_UPDATE_COLUMNS: dict[str, str] = {
    "name": "name",
    "coach_id": "coach_id",
    "max_capacity": "max_capacity",
}


class TeamCreate(BaseModel):
    name: str = Field(..., max_length=100)
    sport_id: int
    coach_id: Optional[int] = None
    max_capacity: int = Field(20, ge=1)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    coach_id: Optional[int] = None
    max_capacity: Optional[int] = Field(None, ge=1)


class TeamMemberAdd(BaseModel):
    member_id: int
    joined_date: Optional[date] = None


@router.get("/")
async def list_teams(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT t.*, s.name AS sport_name,
                   c.first_name || ' ' || c.last_name AS coach_name,
                   COUNT(tm.member_id) AS current_size
            FROM team t
            JOIN sport s ON s.sport_id = t.sport_id
            LEFT JOIN coach c ON c.coach_id = t.coach_id
            LEFT JOIN team_member tm ON tm.team_id = t.team_id
            GROUP BY t.team_id, s.name, c.first_name, c.last_name
            ORDER BY t.name
            """
        )
        return await cur.fetchall()


@router.get("/{team_id}")
async def get_team(team_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT t.*, s.name AS sport_name,
                   c.first_name || ' ' || c.last_name AS coach_name
            FROM team t
            JOIN sport s ON s.sport_id = t.sport_id
            LEFT JOIN coach c ON c.coach_id = t.coach_id
            WHERE t.team_id = %s
            """, (team_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Team not found")
        return row


@router.get("/{team_id}/members")
async def get_team_members(team_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT m.member_id, m.first_name, m.last_name, m.email, tm.joined_date
            FROM team_member tm
            JOIN member m ON m.member_id = tm.member_id
            WHERE tm.team_id = %s
            ORDER BY m.last_name
            """, (team_id,)
        )
        return await cur.fetchall()


@router.post("/", status_code=201)
async def create_team(data: TeamCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO team (name, sport_id, coach_id, max_capacity) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.name, data.sport_id, data.coach_id, data.max_capacity)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{team_id}")
async def update_team(team_id: int, data: TeamUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    raw = data.model_dump(exclude_none=True)
    if not raw:
        raise HTTPException(status_code=400, detail="No fields to update.")
    clauses, values = [], []
    for field, val in raw.items():
        col = _TEAM_UPDATE_COLUMNS.get(field)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Field '{field}' is not updatable.")
        clauses.append(f"{col} = %s")
        values.append(val)
    values.append(team_id)
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(f"UPDATE team SET {', '.join(clauses)} WHERE team_id = %s RETURNING *", values)
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Team not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.post("/{team_id}/members", status_code=201)
async def add_team_member(team_id: int, data: TeamMemberAdd, conn: psycopg.AsyncConnection = Depends(get_db)):
    """Add a member to a team (triggers enforce capacity)."""
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO team_member (team_id, member_id, joined_date) VALUES (%s,%s,%s) RETURNING *",
                (team_id, data.member_id, data.joined_date or date.today())
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{team_id}/members/{member_id}", status_code=204)
async def remove_team_member(team_id: int, member_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM team_member WHERE team_id=%s AND member_id=%s RETURNING team_id", (team_id, member_id)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Team member record not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM team WHERE team_id = %s RETURNING team_id", (team_id,))
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Team not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
