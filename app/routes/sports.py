"""
routes/sports.py — CRUD endpoints for Sports.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class SportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


@router.get("/")
async def list_sports(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM sport ORDER BY name")
        return await cur.fetchall()


@router.get("/{sport_id}")
async def get_sport(sport_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM sport WHERE sport_id = %s", (sport_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Sport not found")
        return row


@router.post("/", status_code=201)
async def create_sport(data: SportCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO sport (name) VALUES (%s) RETURNING *", (data.name,)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{sport_id}")
async def update_sport(sport_id: int, data: SportCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "UPDATE sport SET name = %s WHERE sport_id = %s RETURNING *",
                (data.name, sport_id)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Sport not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{sport_id}", status_code=204)
async def delete_sport(sport_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM sport WHERE sport_id = %s RETURNING sport_id", (sport_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Sport not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
