"""
tests/conftest.py — Shared pytest fixtures for integration tests.

NOTE: These tests require a live PostgreSQL database with the schema loaded.
Set DB credentials in environment variables or a .env file before running.
Run with: pytest tests/ -v
"""
import pytest
import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONNINFO = (
    f"host={os.getenv('DB_HOST', 'localhost')} "
    f"port={os.getenv('DB_PORT', '5432')} "
    f"dbname={os.getenv('DB_NAME', 'sports_club_db')} "
    f"user={os.getenv('DB_USER', 'postgres')} "
    f"password={os.getenv('DB_PASSWORD', 'password')}"
)


@pytest.fixture(scope="module")
def db():
    """Provides a synchronous psycopg connection to the test database."""
    with psycopg.connect(DB_CONNINFO, row_factory=dict_row) as conn:
        yield conn


@pytest.fixture
def db_tx(db):
    """
    Provides a database connection wrapped in a SAVEPOINT for each test.
    Rolls back all changes after each test to keep the database clean.
    """
    with db.transaction(force_rollback=True):
        yield db
