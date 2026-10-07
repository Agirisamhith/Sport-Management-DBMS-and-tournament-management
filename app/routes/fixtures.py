"""
routes/fixtures.py — CRUD endpoints for Fixtures and Participants.
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


class FixtureCreate(BaseModel):
    tournament_id: int
    facility_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ParticipantAdd(BaseModel):
    team_id: int
    score: int = Field(0, ge=0)


class ScoreUpdate(BaseModel):
    score: int = Field(..., ge=0)


@router.get("/")
async def list_fixtures(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT f.*, t.name AS tournament_name, fac.name AS facility_name,
                   s.name AS sport_name
            FROM fixture f
            JOIN tournament t ON t.tournament_id = f.tournament_id
            JOIN facility fac ON fac.facility_id = f.facility_id
            JOIN sport s ON s.sport_id = t.sport_id
            ORDER BY f.start_time DESC
            """
        )
        return await cur.fetchall()


@router.get("/{fixture_id}")
async def get_fixture(fixture_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT f.*, t.name AS tournament_name, fac.name AS facility_name
            FROM fixture f
            JOIN tournament t ON t.tournament_id = f.tournament_id
            JOIN facility fac ON fac.facility_id = f.facility_id
            WHERE f.fixture_id = %s
            """, (fixture_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Fixture not found")
        return row


@router.post("/", status_code=201)
async def create_fixture(data: FixtureCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO fixture (tournament_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.tournament_id, data.facility_id, data.start_time, data.end_time)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.post("/{fixture_id}/participants", status_code=201)
async def add_fixture_participant(fixture_id: int, data: ParticipantAdd, conn: psycopg.AsyncConnection = Depends(get_db)):
    """Add a team to a fixture. Trigger enforces sport matching."""
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO fixture_participant (fixture_id, team_id, score) VALUES (%s,%s,%s) RETURNING *",
                (fixture_id, data.team_id, data.score)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{fixture_id}/participants/{team_id}/score")
async def update_score(fixture_id: int, team_id: int, data: ScoreUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "UPDATE fixture_participant SET score=%s WHERE fixture_id=%s AND team_id=%s RETURNING *",
                (data.score, fixture_id, team_id)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Fixture participant not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{fixture_id}", status_code=204)
async def delete_fixture(fixture_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM fixture WHERE fixture_id = %s RETURNING fixture_id", (fixture_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Fixture not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
