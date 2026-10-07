"""
routes/payments.py — Payment recording endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from app.db import get_db
from app.utils.errors import handle_db_error

router = APIRouter()


class PaymentCreate(BaseModel):
    membership_id: int
    amount: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=255)


@router.get("/")
async def list_payments(conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """
            SELECT p.*, m.first_name || ' ' || m.last_name AS member_name,
                   mp.name AS plan_name
            FROM payment p
            JOIN membership ms ON ms.membership_id = p.membership_id
            JOIN member m ON m.member_id = ms.member_id
            JOIN membership_plan mp ON mp.plan_id = ms.plan_id
            ORDER BY p.payment_date DESC
            """
        )
        return await cur.fetchall()


@router.get("/{payment_id}")
async def get_payment(payment_id: int, conn: psycopg.AsyncConnection = Depends(get_db)):
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT * FROM payment WHERE payment_id = %s", (payment_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")
        return row


@router.post("/", status_code=201)
async def record_payment(data: PaymentCreate, conn: psycopg.AsyncConnection = Depends(get_db)):
    """
    Record a payment. Wrapped in an explicit transaction for safety.
    """
    try:
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                # Verify membership exists
                await cur.execute("SELECT membership_id FROM membership WHERE membership_id=%s", (data.membership_id,))
                if not await cur.fetchone():
                    raise HTTPException(status_code=404, detail="Membership not found")
                await cur.execute(
                    "INSERT INTO payment (membership_id, amount, notes) VALUES (%s,%s,%s) RETURNING *",
                    (data.membership_id, data.amount, data.notes)
                )
                return await cur.fetchone()
    except HTTPException:
        raise
    except Exception as e:
        handle_db_error(e)
