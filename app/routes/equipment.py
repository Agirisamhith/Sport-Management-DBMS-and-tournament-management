"""
routes/equipment.py — Equipment inventory and issue/return management.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class EquipmentCreate(BaseModel):
    name: str = Field(..., max_length=100)
    sport_id: int
    total_stock: int = Field(..., ge=0)
    current_stock: int = Field(..., ge=0)

    @model_validator(mode="after")
    def stock_balance(self):
        if self.current_stock > self.total_stock:
            raise ValueError("current_stock cannot exceed total_stock")
        return self


class IssueCreate(BaseModel):
    equipment_id: int
    member_id: int
    expected_return_date: date
    quantity: int = Field(..., ge=1)

    @model_validator(mode="after")
    def return_date_in_future(self):
        if self.expected_return_date < date.today():
            raise ValueError("expected_return_date cannot be in the past")
        return self


class ReturnEquipment(BaseModel):
    actual_return_date: date


# --- Equipment Inventory ---

@router.get("/")
async def list_equipment(
    search: Optional[str] = None,
    conn: psycopg.AsyncConnection = Depends(get_db)
):
    async with conn.cursor(row_factory=dict_row) as cur:
        if search:
            await cur.execute(
                """
                SELECT e.*, s.name AS sport_name FROM equipment e
                JOIN sport s ON s.sport_id = e.sport_id
                WHERE e.name ILIKE %s ORDER BY e.name
                """, (f"%{search}%",)
            )
        else:
            await cur.execute(
                "SELECT e.*, s.name AS sport_name FROM equipment e JOIN sport s ON s.sport_id = e.sport_id ORDER BY e.name"
            )
        return await cur.fetchall()


@router.get("/{equipment_id}")
async def get_equipment(equipment_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT e.*, s.name AS sport_name FROM equipment e JOIN sport s ON s.sport_id=e.sport_id WHERE e.equipment_id=%s",
            (equipment_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Equipment not found")
        return row


@router.post("/", status_code=201)
async def create_equipment(data: EquipmentCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    # Stock balance is already validated by the model validator
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO equipment (name, sport_id, total_stock, current_stock) VALUES (%s,%s,%s,%s) RETURNING *",
                (data.name, data.sport_id, data.total_stock, data.current_stock)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.delete("/{equipment_id}", status_code=204)
async def delete_equipment(equipment_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    try:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM equipment WHERE equipment_id=%s RETURNING equipment_id", (equipment_id,))
            row = await cur.fetchone()
            await conn.commit()
            if not row:
                raise HTTPException(status_code=404, detail="Equipment not found")
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


# --- Equipment Issues ---

@router.get("/issues/all")
async def list_issues(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT ei.*, e.name AS equipment_name,
                   m.first_name || ' ' || m.last_name AS member_name,
                   CASE WHEN ei.actual_return_date IS NULL THEN 'On Loan' ELSE 'Returned' END AS status
            FROM equipment_issue ei
            JOIN equipment e ON e.equipment_id = ei.equipment_id
            JOIN member m ON m.member_id = ei.member_id
            ORDER BY ei.issue_date DESC
            """
        )
        return await cur.fetchall()


@router.post("/issues", status_code=201)
async def issue_equipment(data: IssueCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    """
    Issue equipment to a member. Trigger auto-decrements stock
    and raises an error if stock is insufficient.
    """
    # Date validation is now handled by model_validator
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO equipment_issue (equipment_id, member_id, expected_return_date, quantity)
                VALUES (%s,%s,%s,%s) RETURNING *
                """,
                (data.equipment_id, data.member_id, data.expected_return_date, data.quantity)
            )
            await conn.commit()
            return await cur.fetchone()
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)


@router.patch("/issues/{issue_id}/return")
async def return_equipment(issue_id: int, data: ReturnEquipment, conn: psycopg.AsyncConnection = Depends(get_db)):
    """
    Mark equipment as returned. Trigger auto-restores stock.
    """
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM equipment_issue WHERE issue_id=%s", (issue_id,))
            issue = await cur.fetchone()
            if not issue:
                raise HTTPException(status_code=404, detail="Issue record not found")
            if issue["actual_return_date"] is not None:
                raise HTTPException(status_code=400, detail="Equipment already returned")
            if data.actual_return_date < issue["issue_date"]:
                raise HTTPException(status_code=400, detail="Return date cannot be before issue date")
            await cur.execute(
                "UPDATE equipment_issue SET actual_return_date=%s WHERE issue_id=%s RETURNING *",
                (data.actual_return_date, issue_id)
            )
            await conn.commit()
            return await cur.fetchone()
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        handle_db_error(e)
