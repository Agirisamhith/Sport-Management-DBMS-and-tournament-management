"""
tests/test_scheduling.py — Integration tests for scheduling conflict constraints.
"""
import pytest
import psycopg
from datetime import datetime, timedelta


@pytest.fixture
def base_data(db_tx):
    """Creates a sport, coach, team, and facility for scheduling tests."""
    with db_tx.cursor() as cur:
        cur.execute("INSERT INTO sport (name) VALUES ('TestSport_Sched') RETURNING sport_id")
        sport_id = cur.fetchone()["sport_id"]

        cur.execute(
            "INSERT INTO coach (first_name, last_name, email, sport_id) VALUES (%s,%s,%s,%s) RETURNING coach_id",
            ("Sched", "Coach", "sched.coach@test.com", sport_id)
        )
        coach_id = cur.fetchone()["coach_id"]

        cur.execute(
            "INSERT INTO team (name, sport_id, coach_id, max_capacity) VALUES (%s,%s,%s,%s) RETURNING team_id",
            ("TestTeam_Sched", sport_id, coach_id, 20)
        )
        team_id = cur.fetchone()["team_id"]

        cur.execute(
            "INSERT INTO facility (name, max_capacity) VALUES (%s,%s) RETURNING facility_id",
            ("TestFacility_Sched", 100)
        )
        facility_id = cur.fetchone()["facility_id"]

    return {"sport_id": sport_id, "team_id": team_id, "facility_id": facility_id}


def test_no_facility_overlap_for_training_sessions(db_tx, base_data):
    """Two training sessions at the same facility cannot overlap in time."""
    t = datetime(2030, 1, 10, 9, 0)
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s)",
            (base_data["team_id"], base_data["facility_id"], t, t + timedelta(hours=2))
        )
        # Need a second team for the second session (same facility, overlapping time)
        cur.execute(
            "INSERT INTO sport (name) VALUES ('TestSport_Sched2') RETURNING sport_id"
        )
        sport_id2 = cur.fetchone()["sport_id"]
        cur.execute(
            "INSERT INTO team (name, sport_id, max_capacity) VALUES (%s,%s,%s) RETURNING team_id",
            ("TestTeam_Sched2", sport_id2, 5)
        )
        team2_id = cur.fetchone()["team_id"]
        with pytest.raises(psycopg.errors.ExclusionViolation):
            cur.execute(
                "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s)",
                (team2_id, base_data["facility_id"], t + timedelta(hours=1), t + timedelta(hours=3))
            )


def test_non_overlapping_sessions_allowed(db_tx, base_data):
    """Two sessions at the same facility without overlap should succeed."""
    t = datetime(2030, 1, 11, 9, 0)
    with db_tx.cursor() as cur:
        cur.execute(
            "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s)",
            (base_data["team_id"], base_data["facility_id"], t, t + timedelta(hours=2))
        )
        cur.execute(
            "INSERT INTO sport (name) VALUES ('TestSport_Sched3') RETURNING sport_id"
        )
        sport_id3 = cur.fetchone()["sport_id"]
        cur.execute(
            "INSERT INTO team (name, sport_id, max_capacity) VALUES (%s,%s,%s) RETURNING team_id",
            ("TestTeam_Sched3", sport_id3, 5)
        )
        team3_id = cur.fetchone()["team_id"]
        # Book at non-overlapping time (starts after first session ends)
        cur.execute(
            "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s)",
            (team3_id, base_data["facility_id"], t + timedelta(hours=2), t + timedelta(hours=4))
        )


def test_team_capacity_trigger(db_tx, base_data):
    """Adding a member beyond team capacity should raise an exception."""
    with db_tx.cursor() as cur:
        cur.execute(
            "UPDATE team SET max_capacity = 1 WHERE team_id = %s",
            (base_data["team_id"],)
        )
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s) RETURNING member_id",
            ("Cap", "Test1", "cap.test1@test.com", "1990-01-01")
        )
        m1 = cur.fetchone()["member_id"]
        cur.execute(
            "INSERT INTO member (first_name, last_name, email, date_of_birth) VALUES (%s,%s,%s,%s) RETURNING member_id",
            ("Cap", "Test2", "cap.test2@test.com", "1990-01-01")
        )
        m2 = cur.fetchone()["member_id"]

        cur.execute(
            "INSERT INTO team_member (team_id, member_id) VALUES (%s,%s)",
            (base_data["team_id"], m1)
        )
        with pytest.raises(psycopg.errors.RaiseException):
            cur.execute(
                "INSERT INTO team_member (team_id, member_id) VALUES (%s,%s)",
                (base_data["team_id"], m2)
            )


def test_session_time_check(db_tx, base_data):
    """A training session where end_time <= start_time should be rejected."""
    t = datetime(2030, 2, 1, 10, 0)
    with db_tx.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES (%s,%s,%s,%s)",
                (base_data["team_id"], base_data["facility_id"], t, t - timedelta(hours=1))
            )
