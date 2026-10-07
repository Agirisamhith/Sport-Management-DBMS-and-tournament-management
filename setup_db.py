"""
setup_db.py — Automated database setup and migration script.
Creates the database if it doesn't exist and applies all schema/data scripts in order.
"""
import sys
import os
from pathlib import Path
import psycopg
from psycopg import sql

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent))
from app.config import settings

SQL_FILES = [
    "01_extensions.sql",
    "02_schema.sql",
    "03_constraints.sql",
    "04_triggers.sql",
    "05_indexes.sql",
    "06_sample_data.sql",
    "07_reports.sql",
]


def init_database():
    print(f"Connecting to PostgreSQL server at {settings.db_host}:{settings.db_port} as {settings.db_user}...")
    
    # 1. Connect to default postgres DB to ensure target database exists
    admin_conninfo = (
        f"host={settings.db_host} "
        f"port={settings.db_port} "
        f"user={settings.db_user} "
        f"password={settings.db_password} "
        f"dbname=postgres"
    )
    
    try:
        with psycopg.connect(admin_conninfo, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.db_name,))
                exists = cur.fetchone()
                if not exists:
                    print(f"Creating database '{settings.db_name}'...")
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.db_name)))
                    print(f"Database '{settings.db_name}' created successfully.")
                else:
                    print(f"Database '{settings.db_name}' already exists.")
    except Exception as e:
        print(f"Failed to connect to postgres server: {e}")
        return False

    # 2. Connect to the target database and execute all SQL scripts
    target_conninfo = (
        f"host={settings.db_host} "
        f"port={settings.db_port} "
        f"user={settings.db_user} "
        f"password={settings.db_password} "
        f"dbname={settings.db_name}"
    )

    db_dir = Path(__file__).parent / "db"
    try:
        with psycopg.connect(target_conninfo) as conn:
            with conn.cursor() as cur:
                for file_name in SQL_FILES:
                    file_path = db_dir / file_name
                    if not file_path.exists():
                        print(f"Warning: {file_name} not found, skipping.")
                        continue
                    print(f"Applying {file_name}...")
                    sql_content = file_path.read_text(encoding="utf-8")
                    cur.execute(sql_content)
                    conn.commit()
                    print(f"Applied {file_name} successfully.")
        print("\nAll database migrations and sample data applied successfully!")
        return True
    except Exception as e:
        print(f"Error applying migrations: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
