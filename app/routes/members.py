"""
routes/members.py — CRUD endpoints for Members.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()

# Explicit allowlist of updatable columns → prevents SQL injection even if
# Pydantic field names ever differ from DB column names.
_MEMBER_UPDATE_COLUMNS: dict[str, str] = {
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email",
    "phone": "phone",
}


class MemberCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: date
    join_date: Optional[date] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("date_of_birth")
    @classmethod
    def dob_in_past(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v


class MemberUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v


@router.get("/")
async def list_members(
    search: Optional[str] = Query(None, description="Search by name or email"),
    conn: psycopg.AsyncConnection = Depends(get_db)
):
    async with conn.cursor(row_factory=dict_row) as cur:
        if search:
            await cur.execute(
                """
                SELECT m.*, ms.status AS membership_status
                FROM member m
                LEFT JOIN membership ms ON ms.member_id = m.member_id AND ms.status = 'Active'
                WHERE (first_name || ' ' || last_name) ILIKE %s OR email ILIKE %s
                ORDER BY m.last_name, m.first_name
                """,
                (f"%{search}%", f"%{search}%")
            )
        else:
            await cur.execute(
                """
                SELECT m.*, ms.status AS membership_status
                FROM member m
                LEFT JOIN membership ms ON ms.member_id = m.member_id AND ms.status = 'Active'
                ORDER BY m.last_name, m.first_name
                """
            )
        return await cur.fetchall()


@router.get("/{member_id}")
async def get_member(member_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM member WHERE member_id = %s", (member_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Member not found")
        return row


@router.post("/", status_code=201)
async def create_member(data: MemberCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO member (first_name, last_name, email, phone, date_of_birth, join_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (data.first_name, data.last_name, data.email, data.phone,
                 data.date_of_birth, data.join_date or date.today())
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.put("/{member_id}")
async def update_member(member_id: int, data: MemberUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    raw = data.model_dump(exclude_none=True)
    if not raw:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    # Use only allowed column names to prevent SQL injection
    clauses, values = [], []
    for field, val in raw.items():
        col = _MEMBER_UPDATE_COLUMNS.get(field)
        if col is None:
            raise HTTPException(status_code=400, detail=f"Field '{field}' is not updatable.")
        clauses.append(f"{col} = %s")
        values.append(val)
    values.append(member_id)
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                f"UPDATE member SET {', '.join(clauses)} WHERE member_id = %s RETURNING *",
                values
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Member not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{member_id}", status_code=204)
async def delete_member(member_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM member WHERE member_id = %s RETURNING member_id", (member_id,)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Member not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
