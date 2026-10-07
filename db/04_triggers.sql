-- =============================================================================
-- 04_triggers.sql
-- Business rule enforcement via PL/pgSQL triggers and functions
-- Execute AFTER 03_constraints.sql
-- =============================================================================


-- =============================================================================
-- TRIGGER 1: Enforce team roster capacity
-- A member cannot be added to a team that is already full.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_check_team_capacity()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_current_count INT;
    v_max_capacity  INT;
BEGIN
    SELECT COUNT(*)    INTO v_current_count FROM team_member WHERE team_id = NEW.team_id;
    SELECT max_capacity INTO v_max_capacity  FROM team        WHERE team_id = NEW.team_id;

    IF v_current_count >= v_max_capacity THEN
        RAISE EXCEPTION
            'Team (id=%) is at maximum capacity (%). Cannot add member.',
            NEW.team_id, v_max_capacity;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_team_capacity
BEFORE INSERT ON team_member
FOR EACH ROW EXECUTE FUNCTION fn_check_team_capacity();


-- =============================================================================
-- TRIGGER 2: Enforce facility capacity for training sessions
-- The sum of team members in a session cannot exceed the facility's max_capacity.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_check_session_facility_capacity()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_team_size      INT;
    v_facility_cap   INT;
BEGIN
    SELECT COUNT(*)    INTO v_team_size    FROM team_member WHERE team_id = NEW.team_id;
    SELECT max_capacity INTO v_facility_cap FROM facility    WHERE facility_id = NEW.facility_id;

    IF v_team_size > v_facility_cap THEN
        RAISE EXCEPTION
            'Team size (%) exceeds facility (id=%) capacity (%). Cannot schedule session.',
            v_team_size, NEW.facility_id, v_facility_cap;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_session_facility_capacity
BEFORE INSERT OR UPDATE ON training_session
FOR EACH ROW EXECUTE FUNCTION fn_check_session_facility_capacity();


-- =============================================================================
-- TRIGGER 3: Equipment issue — check and decrement stock
-- Prevents issuing equipment if insufficient stock exists, and auto-decrements.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_equipment_issue_deduct_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_available INT;
BEGIN
    -- Lock the row to prevent race conditions in concurrent transactions
    SELECT current_stock INTO v_available
    FROM equipment
    WHERE equipment_id = NEW.equipment_id
    FOR UPDATE;

    IF v_available < NEW.quantity THEN
        RAISE EXCEPTION
            'Insufficient stock for equipment (id=%). Requested: %, Available: %.',
            NEW.equipment_id, NEW.quantity, v_available;
    END IF;

    UPDATE equipment
    SET current_stock = current_stock - NEW.quantity
    WHERE equipment_id = NEW.equipment_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_equipment_issue_deduct
BEFORE INSERT ON equipment_issue
FOR EACH ROW EXECUTE FUNCTION fn_equipment_issue_deduct_stock();


-- =============================================================================
-- TRIGGER 4: Equipment return — validate and restore stock
-- Ensures return quantity does not exceed issued quantity, and restores stock.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_equipment_return_restore_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Only act when actual_return_date is being set for the first time
    IF OLD.actual_return_date IS NULL AND NEW.actual_return_date IS NOT NULL THEN
        UPDATE equipment
        SET current_stock = current_stock + OLD.quantity
        WHERE equipment_id = NEW.equipment_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_equipment_return_restore
BEFORE UPDATE ON equipment_issue
FOR EACH ROW EXECUTE FUNCTION fn_equipment_return_restore_stock();


-- =============================================================================
-- TRIGGER 5: Auto-expire memberships
-- Updates membership status to 'Expired' if end_date has passed.
-- Called at insert/update time to keep status consistent.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_auto_expire_membership()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.end_date < CURRENT_DATE AND NEW.status = 'Active' THEN
        NEW.status := 'Expired';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auto_expire_membership
BEFORE INSERT OR UPDATE ON membership
FOR EACH ROW EXECUTE FUNCTION fn_auto_expire_membership();


-- =============================================================================
-- TRIGGER 6: Prevent cross-sport team/fixture assignment
-- A team in a tournament must play the same sport as the tournament.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_check_fixture_team_sport()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_fixture_sport INT;
    v_team_sport    INT;
BEGIN
    SELECT t.sport_id INTO v_fixture_sport
    FROM fixture f
    JOIN tournament t ON f.tournament_id = t.tournament_id
    WHERE f.fixture_id = NEW.fixture_id;

    SELECT sport_id INTO v_team_sport
    FROM team WHERE team_id = NEW.team_id;

    IF v_fixture_sport <> v_team_sport THEN
        RAISE EXCEPTION
            'Team (id=%) sport does not match the tournament sport. Cannot add to fixture.',
            NEW.team_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_fixture_team_sport
BEFORE INSERT ON fixture_participant
FOR EACH ROW EXECUTE FUNCTION fn_check_fixture_team_sport();
