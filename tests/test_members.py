"""
tests/test_members.py — Integration tests for the member table.
"""
import pytest
import psycopg


def test_member_insert_and_select(db_tx):
    """Test that a valid member can be inserted and retrieved."""
    with db_tx.cursor() as cur:
        cur.execute(
            """
            INSERT INTO member (first_name, last_name, email, date_of_birth)
            VALUES (%s, %s, %s, %s) RETURNING member_id
            """,
            ("Test", "User", "test.user.unique@test.com", "1995-01-01")
        )
        row = cur.fetchone()
        assert row["member_id"] is not None


def test_member_email_unique_constraint(db_tx):
    """Two members with the same email should be rejected."""
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s)",
            ("A", "User", "duplicate@test.com", "1990-01-01")
        )
        with pytest.raises(psycopg.errors.UniqueViolation):
            cur.execute(
                "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s)",
                ("B", "User", "duplicate@test.com", "1990-01-01")
            )


def test_member_dob_check_constraint(db_tx):
    """A member with a future date of birth should be rejected."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s)",
                ("Future", "Person", "future@test.com", "2099-01-01")
            )


def test_member_not_null_constraint(db_tx):
    """Inserting without required fields should fail."""
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.NotNullViolation):
            cur.execute(
                "INSERT INTO member (last_name, email, date_of_birth) VALUES (%s,%s,%s)",
                ("NoFirstName", "nofirst@test.com", "1990-01-01")
            )


def test_member_update(db_tx):
    """A member's email can be updated."""
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s) RETURNING member_id",
            ("Update", "Me", "update.me@test.com", "1990-01-01")
        )
        mid = cur.fetchone()["member_id"]
        cur.execute("UPDATE member SET first_name = 'Updated' WHERE member_id = %s", (mid,))
        cur.execute("SELECT first_name FROM member WHERE member_id = %s", (mid,))
        assert cur.fetchone()["first_name"] == "Updated"
