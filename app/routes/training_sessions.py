"""
routes/training_sessions.py — CRUD endpoints for Training Sessions.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class SessionCreate(BaseModel):
    team_id: int
    facility_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


@router.get("/")
async def list_sessions(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT ts.*, t.name AS team_name, f.name AS facility_name, s.name AS sport_name
            FROM training_session ts
            JOIN team t ON t.team_id = ts.team_id
            JOIN facility f ON f.facility_id = ts.facility_id
            JOIN sport s ON s.sport_id = t.sport_id
            ORDER BY ts.start_time DESC
            """
        )
        return await cur.fetchall()


@router.get("/{session_id}")
async def get_session(session_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT ts.*, t.name AS team_name, f.name AS facility_name
            FROM training_session ts
            JOIN team t ON t.team_id = ts.team_id
            JOIN facility f ON f.facility_id = ts.facility_id
            WHERE ts.session_id = %s
            """, (session_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Training session not found")
        return row


@router.post("/", status_code=201)
async def create_session(data: SessionCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.team_id, data.facility_id, data.start_time, data.end_time)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM training_session WHERE session_id=%s RETURNING session_id", (session_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Training session not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
