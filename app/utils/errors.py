"""
utils/errors.py — Shared error handling utilities.

Converts psycopg-level exceptions into appropriate HTTP responses while
keeping internal details (stack traces, raw SQL messages) server-side.
"""
import logging
import psycopg
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Pydantic email-str trigger phrase we want to surface to clients
_EMAIL_HINT = "value is not a valid email"


def handle_db_error(e: Exception) -> None:
    """
    Convert psycopg errors to meaningful HTTP exceptions.

    Logs the full error server-side (for debugging) and raises a clean
    HTTPException with a client-safe message.  Always raises — never returns.
    """
    logger.error("Database error: %s", e, exc_info=True)

    if isinstance(e, psycopg.errors.UniqueViolation):
        # Extract the constraint name for a more helpful message
        detail = _extract_unique_detail(e)
        raise HTTPException(status_code=409, detail=detail)

    if isinstance(e, psycopg.errors.ForeignKeyViolation):
        raise HTTPException(
            status_code=400,
            detail="Foreign key violation: a referenced record does not exist.",
        )

    if isinstance(e, psycopg.errors.CheckViolation):
        constraint = _diag_constraint(e)
        raise HTTPException(
            status_code=400,
            detail=f"Constraint violation: value rejected by rule '{constraint}'."
            if constraint
            else "Constraint violation: the submitted value is not allowed.",
        )

    if isinstance(e, psycopg.errors.NotNullViolation):
        col = getattr(e.diag, "column_name", None)
        raise HTTPException(
            status_code=400,
            detail=f"Required field '{col}' is missing." if col else "A required field is missing.",
        )

    if isinstance(e, psycopg.errors.RaiseException):
        # Custom business-rule errors raised by PL/pgSQL triggers.
        # Only expose the first line (the human-readable message).
        msg = str(e).split("\n")[0].strip()
        raise HTTPException(status_code=400, detail=msg)

    if isinstance(e, psycopg.errors.ExclusionViolation):
        raise HTTPException(
            status_code=409,
            detail="Scheduling conflict: the requested time slot is already booked.",
        )

    if isinstance(e, psycopg.errors.StringDataRightTruncation):
        raise HTTPException(
            status_code=400,
            detail="A field value exceeds the maximum allowed length.",
        )

    # Generic DB error — do NOT leak raw SQL to the client
    raise HTTPException(status_code=500, detail="An internal database error occurred.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_unique_detail(e: psycopg.errors.UniqueViolation) -> str:
    constraint = _diag_constraint(e)
    if constraint:
        return f"Duplicate entry: a record violating the uniqueness rule '{constraint}' already exists."
    return "Duplicate entry: a record with this value already exists."


def _diag_constraint(e: Exception) -> str | None:
    """Safely pull the constraint name from psycopg diagnostics."""
    diag = getattr(e, "diag", None)
    if diag is None:
        return None
    return getattr(diag, "constraint_name", None)
