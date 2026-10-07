"""
routes/tournaments.py — CRUD endpoints for Tournaments and Fixtures.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date, datetime
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class TournamentCreate(BaseModel):
    name: str = Field(..., max_length=150)
    sport_id: int
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


@router.get("/")
async def list_tournaments(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT t.*, s.name AS sport_name,
                   COUNT(f.fixture_id) AS fixture_count
            FROM tournament t
            JOIN sport s ON s.sport_id = t.sport_id
            LEFT JOIN fixture f ON f.tournament_id = t.tournament_id
            GROUP BY t.tournament_id, s.name
            ORDER BY t.start_date DESC
            """
        )
        return await cur.fetchall()


@router.get("/{tournament_id}")
async def get_tournament(tournament_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT t.*, s.name AS sport_name FROM tournament t JOIN sport s ON s.sport_id = t.sport_id WHERE t.tournament_id = %s",
            (tournament_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return row


@router.get("/{tournament_id}/fixtures")
async def get_tournament_fixtures(tournament_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT f.*, fac.name AS facility_name,
                   json_agg(json_build_object('team_id', fp.team_id, 'team_name', t.name, 'score', fp.score)) AS participants
            FROM fixture f
            JOIN facility fac ON fac.facility_id = f.facility_id
            LEFT JOIN fixture_participant fp ON fp.fixture_id = f.fixture_id
            LEFT JOIN team t ON t.team_id = fp.team_id
            WHERE f.tournament_id = %s
            GROUP BY f.fixture_id, fac.name
            ORDER BY f.start_time
            """, (tournament_id,)
        )
        return await cur.fetchall()


@router.post("/", status_code=201)
async def create_tournament(data: TournamentCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO tournament (name, sport_id, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.name, data.sport_id, data.start_date, data.end_date)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{tournament_id}", status_code=204)
async def delete_tournament(tournament_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM tournament WHERE tournament_id = %s RETURNING tournament_id", (tournament_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Tournament not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
