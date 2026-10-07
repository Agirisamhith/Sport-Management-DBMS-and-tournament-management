"""
tests/test_memberships.py — Integration tests for membership and payment rules.
"""
import pytest
import psycopg
from datetime import date, timedelta


@pytest.fixture
def sample_member(db_tx):
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s) RETURNING member_id",
            ("Membership", "Tester", "membership.tester@test.com", "1990-01-01")
        )
        return cur.fetchone()["member_id"]


@pytest.fixture
def sample_plan(db_tx):
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO membership_plan (name, duration_months, fee) VALUES (%s,%s,%s) RETURNING plan_id",
            ("Test Plan", 12, 100.00)
        )
        return cur.fetchone()["plan_id"]


def test_membership_creation(db_tx, sample_member, sample_plan):
    """A valid membership can be created."""
    start = date.today()
    end = start + timedelta(days=365)
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO membership (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING membership_id",
            (sample_member, sample_plan, start, end)
        )
        assert cur.fetchone()["membership_id"] is not None


def test_membership_invalid_dates(db_tx, sample_member, sample_plan):
    """Membership where end_date <= start_date should be rejected."""
    start = date.today()
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO membership (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s)",
                (sample_member, sample_plan, start, start)
            )


def test_membership_auto_expire_trigger(db_tx, sample_member, sample_plan):
    """Memberships with past end_date should auto-expire on insert/update."""
    past_start = date(2020, 1, 1)
    past_end = date(2020, 12, 31)
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO membership (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING status",
            (sample_member, sample_plan, past_start, past_end)
        )
        assert cur.fetchone()["status"] == "Expired"


def test_payment_requires_positive_amount(db_tx, sample_member, sample_plan):
    """A payment with amount <= 0 should fail the CHECK constraint."""
    start = date.today()
    end = start + timedelta(days=365)
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO membership (member_id, plan_id, start_date, end_date) VALUES (%s,%s,%s,%s) RETURNING membership_id",
            (sample_member, sample_plan, start, end)
        )
        ms_id = cur.fetchone()["membership_id"]
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO payment (membership_id, amount) VALUES (%s,%s)",
                (ms_id, -50.00)
            )


def test_membership_invalid_status(db_tx, sample_member, sample_plan):
    """An invalid status value should be rejected by CHECK constraint."""
    start = date.today()
    end = start + timedelta(days=365)
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO membership (member_id, plan_id, start_date, end_date, status) VALUES (%s,%s,%s,%s,%s)",
                (sample_member, sample_plan, start, end, "InvalidStatus")
            )


def test_plan_negative_fee_rejected(db_tx):
    """A membership plan with a negative fee should be rejected."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO membership_plan (name, duration_months, fee) VALUES (%s,%s,%s)",
                ("Negative Plan", 1, -10.00)
            )
