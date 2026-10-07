"""
routes/facilities.py — CRUD endpoints for Facilities.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()

_FACILITY_UPDATE_COLUMNS: dict[str, str] = {
    "name": "name",
    "location": "location",
    "max_capacity": "max_capacity",
}


class FacilityCreate(BaseModel):
    name: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=150)
    max_capacity: int = Field(..., ge=1)


class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=150)
    max_capacity: Optional[int] = Field(None, ge=1)


@router.get("/")
async def list_facilities(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM facility ORDER BY name")
        return await cur.fetchall()


@router.get("/{facility_id}")
async def get_facility(facility_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM facility WHERE facility_id = %s", (facility_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Facility not found")
        return row


@router.post("/", status_code=201)
async def create_facility(data: FacilityCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO facility (name, location, max_capacity) VALUES (%s,%s,%s) RETURNING *",
                (data.name, data.location, data.max_capacity)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{facility_id}")
async def update_facility(facility_id: int, data: FacilityUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    raw = data.model_dump(exclude_none=True)
    if not raw:
        raise HTTPException(status_code=400, detail="No fields to update.")
    clauses, values = [], []
    for field, val in raw.items():
        col = _FACILITY_UPDATE_COLUMNS.get(field)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Field '{field}' is not updatable.")
        clauses.append(f"{col} = %s")
        values.append(val)
    values.append(facility_id)
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                f"UPDATE facility SET {', '.join(clauses)} WHERE facility_id = %s RETURNING *", values
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Facility not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{facility_id}", status_code=204)
async def delete_facility(facility_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM facility WHERE facility_id = %s RETURNING facility_id", (facility_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Facility not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
