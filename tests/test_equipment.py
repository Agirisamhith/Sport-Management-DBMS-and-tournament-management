"""
tests/test_equipment.py — Integration tests for equipment stock management triggers.
"""
import pytest
import psycopg
from datetime import date, timedelta


@pytest.fixture
def sample_sport(db_tx):
    with db_tx.cursor() as cur:
        cur.execute("INSERT INTO sport (name) VALUES ('TestSport_Equip') RETURNING sport_id")
        return cur.fetchone()["sport_id"]


@pytest.fixture
def sample_member(db_tx):
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s) RETURNING member_id",
            ("Equip", "Tester", "equip.tester@test.com", "1990-01-01")
        )
        return cur.fetchone()["member_id"]


@pytest.fixture
def sample_equipment(db_tx, sample_sport):
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO equipment (name, sport_id, total_stock, current_stock) VALUES (%s,%s,%s,%s) RETURNING equipment_id",
            ("TestBall", sample_sport, 5, 5)
        )
        return cur.fetchone()["equipment_id"]


def test_equipment_issue_reduces_stock(db_tx, sample_equipment, sample_member):
    """Issuing equipment should reduce current_stock via trigger."""
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO equipment_issue (equipment_id, member_id, expected_return_date, quantity) VALUES (%s,%s,%s,%s)",
            (sample_equipment, sample_member, date.today() + timedelta(days=7), 2)
        )
        cur.execute("SELECT current_stock FROM equipment WHERE equipment_id = %s", (sample_equipment,))
        assert cur.fetchone()["current_stock"] == 3


def test_equipment_issue_insufficient_stock(db_tx, sample_equipment, sample_member):
    """Issuing more equipment than available should raise a trigger exception."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.RaiseException):
            cur.execute(
                "INSERT INTO equipment_issue (equipment_id, member_id, expected_return_date, quantity) VALUES (%s,%s,%s,%s)",
                (sample_equipment, sample_member, date.today() + timedelta(days=7), 999)
            )


def test_equipment_return_restores_stock(db_tx, sample_equipment, sample_member):
    """Returning equipment should restore current_stock via trigger."""
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO equipment_issue (equipment_id, member_id, expected_return_date, quantity) VALUES (%s,%s,%s,%s) RETURNING issue_id",
            (sample_equipment, sample_member, date.today() + timedelta(days=7), 3)
        )
        issue_id = cur.fetchone()["issue_id"]
        cur.execute("SELECT current_stock FROM equipment WHERE equipment_id = %s", (sample_equipment,))
        assert cur.fetchone()["current_stock"] == 2

        cur.execute(
            "UPDATE equipment_issue SET actual_return_date = %s WHERE issue_id = %s",
            (date.today(), issue_id)
        )
        cur.execute("SELECT current_stock FROM equipment WHERE equipment_id = %s", (sample_equipment,))
        assert cur.fetchone()["current_stock"] == 5


def test_equipment_issue_quantity_positive(db_tx, sample_equipment, sample_member):
    """Issuing zero or negative quantity should fail the CHECK constraint."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO equipment_issue (equipment_id, member_id, expected_return_date, quantity) VALUES (%s,%s,%s,%s)",
                (sample_equipment, sample_member, date.today() + timedelta(days=7), 0)
            )


def test_equipment_return_date_before_issue_date(db_tx, sample_equipment, sample_member):
    """Return date before issue date should fail the CHECK constraint."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO equipment_issue (equipment_id, member_id, issue_date, expected_return_date, actual_return_date, quantity) VALUES (%s,%s,%s,%s,%s,%s)",
                (sample_equipment, sample_member, date.today(), date.today() + timedelta(days=7),
                 date.today() - timedelta(days=1), 1)
            )
