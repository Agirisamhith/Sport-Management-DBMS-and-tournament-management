"""
routes/coaches.py — CRUD endpoints for Coaches.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()

_COACH_UPDATE_COLUMNS: dict[str, str] = {
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email",
    "phone": "phone",
    "sport_id": "sport_id",
}


class CoachCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    sport_id: int

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.strip().lower()


class CoachUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = None
    sport_id: Optional[int] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v


@router.get("/")
async def list_coaches(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT c.*, s.name AS sport_name
            FROM coach c JOIN sport s ON s.sport_id = c.sport_id
            ORDER BY c.last_name
            """
        )
        return await cur.fetchall()


@router.get("/{coach_id}")
async def get_coach(coach_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT c.*, s.name AS sport_name FROM coach c JOIN sport s ON s.sport_id = c.sport_id WHERE c.coach_id = %s",
            (coach_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Coach not found")
        return row


@router.post("/", status_code=201)
async def create_coach(data: CoachCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO coach (first_name, last_name, email, phone, sport_id) VALUES (%s,%s,%s,%s,%s) RETURNING *",
                (data.first_name, data.last_name, data.email, data.phone, data.sport_id)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{coach_id}")
async def update_coach(coach_id: int, data: CoachUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    raw = data.model_dump(exclude_none=True)
    if not raw:
        raise HTTPException(status_code=400, detail="No fields to update.")
    clauses, values = [], []
    for field, val in raw.items():
        col = _COACH_UPDATE_COLUMNS.get(field)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Field '{field}' is not updatable.")
        clauses.append(f"{col} = %s")
        values.append(val)
    values.append(coach_id)
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                f"UPDATE coach SET {', '.join(clauses)} WHERE coach_id = %s RETURNING *", values
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Coach not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{coach_id}", status_code=204)
async def delete_coach(coach_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM coach WHERE coach_id = %s RETURNING coach_id", (coach_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Coach not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
