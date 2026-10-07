"""
routes/memberships.py — CRUD for Membership Plans and Member Memberships.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from datetime import date
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class PlanCreate(BaseModel):
    name: str = Field(..., max_length=50)
    duration_months: int = Field(..., ge=1)
    fee: float = Field(..., ge=0)


class MembershipCreate(BaseModel):
    member_id: int
    plan_id: int
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be strictly after start_date")
        return self


class MembershipStatusUpdate(BaseModel):
    status: Literal["Active", "Expired", "Cancelled"]


# --- Membership Plans ---

@router.get("/plans")
async def list_plans(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM membership_plan ORDER BY fee")
        return await cur.fetchall()


@router.post("/plans", status_code=201)
async def create_plan(data: PlanCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO membership_plan (name, duration_months, fee) VALUES (%s,%s,%s) RETURNING *",
                (data.name, data.duration_months, data.fee)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM membership_plan WHERE plan_id=%s RETURNING plan_id", (plan_id,))
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Plan not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)

# --- Memberships ---

@router.get("/")
async def list_memberships(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT ms.*, m.first_name || ' ' || m.last_name AS member_name,
                   mp.name AS plan_name, mp.fee
            FROM membership ms
            JOIN member m ON m.member_id = ms.member_id
            JOIN membership_plan mp ON mp.plan_id = ms.plan_id
            ORDER BY ms.start_date DESC
            """
        )
        return await cur.fetchall()


@router.get("/{membership_id}")
async def get_membership(membership_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT ms.*, m.first_name || ' ' || m.last_name AS member_name, mp.name AS plan_name FROM membership ms JOIN member m ON m.member_id=ms.member_id JOIN membership_plan mp ON mp.plan_id=ms.plan_id WHERE ms.membership_id=%s",
            (membership_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Membership not found")
        return row


@router.post("/", status_code=201)
async def create_membership(data: MembershipCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO membership (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.member_id, data.plan_id, data.start_date, data.end_date)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.patch("/{membership_id}/status")
async def update_membership_status(membership_id: int, data: MembershipStatusUpdate, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "UPDATE membership SET status=%s WHERE membership_id=%s RETURNING *",
                (data.status, membership_id)
            )
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Membership not found")
            return row
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
