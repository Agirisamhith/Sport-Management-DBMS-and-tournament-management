-- =============================================================================
-- 03_constraints.sql
-- All UNIQUE, CHECK, DEFAULT, and FOREIGN KEY constraints
-- Execute AFTER 02_schema.sql
-- =============================================================================

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================

ALTER TABLE sport             ADD CONSTRAINT uq_sport_name            UNIQUE (name);
ALTER TABLE member            ADD CONSTRAINT uq_member_email           UNIQUE (email);
ALTER TABLE member            ADD CONSTRAINT uq_member_phone           UNIQUE (phone);
ALTER TABLE membership_plan   ADD CONSTRAINT uq_plan_name              UNIQUE (name);
ALTER TABLE coach             ADD CONSTRAINT uq_coach_email            UNIQUE (email);
ALTER TABLE team              ADD CONSTRAINT uq_team_name              UNIQUE (name);
ALTER TABLE facility          ADD CONSTRAINT uq_facility_name          UNIQUE (name);
ALTER TABLE tournament        ADD CONSTRAINT uq_tournament_name        UNIQUE (name);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================

-- member
ALTER TABLE member
    ADD CONSTRAINT chk_member_dob CHECK (date_of_birth < CURRENT_DATE);

-- membership_plan
ALTER TABLE membership_plan
    ADD CONSTRAINT chk_plan_duration CHECK (duration_months > 0),
    ADD CONSTRAINT chk_plan_fee      CHECK (fee >= 0);

-- membership
ALTER TABLE membership
    ADD CONSTRAINT chk_membership_dates CHECK (end_date > start_date),
    ADD CONSTRAINT chk_membership_status CHECK (status IN ('Active', 'Expired', 'Cancelled'));

-- payment
ALTER TABLE payment
    ADD CONSTRAINT chk_payment_amount CHECK (amount > 0);

-- facility
ALTER TABLE facility
    ADD CONSTRAINT chk_facility_capacity CHECK (max_capacity > 0);

-- team
ALTER TABLE team
    ADD CONSTRAINT chk_team_capacity CHECK (max_capacity > 0);

-- training_session
ALTER TABLE training_session
    ADD CONSTRAINT chk_session_times CHECK (end_time > start_time);

-- tournament
ALTER TABLE tournament
    ADD CONSTRAINT chk_tournament_dates CHECK (end_date >= start_date);

-- fixture
ALTER TABLE fixture
    ADD CONSTRAINT chk_fixture_times CHECK (end_time > start_time);

-- fixture_participant
ALTER TABLE fixture_participant
    ADD CONSTRAINT chk_fixture_score CHECK (score >= 0);

-- equipment
ALTER TABLE equipment
    ADD CONSTRAINT chk_equip_total_stock   CHECK (total_stock >= 0),
    ADD CONSTRAINT chk_equip_current_stock CHECK (current_stock >= 0),
    ADD CONSTRAINT chk_equip_stock_balance CHECK (current_stock <= total_stock);

-- equipment_issue
ALTER TABLE equipment_issue
    ADD CONSTRAINT chk_issue_quantity     CHECK (quantity > 0),
    ADD CONSTRAINT chk_issue_dates        CHECK (expected_return_date >= issue_date),
    ADD CONSTRAINT chk_issue_return_dates CHECK (actual_return_date IS NULL OR actual_return_date >= issue_date);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================

-- membership
ALTER TABLE membership
    ADD CONSTRAINT fk_membership_member FOREIGN KEY (member_id)
        REFERENCES member (member_id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_membership_plan FOREIGN KEY (plan_id)
        REFERENCES membership_plan (plan_id) ON DELETE RESTRICT;

-- payment
ALTER TABLE payment
    ADD CONSTRAINT fk_payment_membership FOREIGN KEY (membership_id)
        REFERENCES membership (membership_id) ON DELETE RESTRICT;

-- coach
ALTER TABLE coach
    ADD CONSTRAINT fk_coach_sport FOREIGN KEY (sport_id)
        REFERENCES sport (sport_id) ON DELETE RESTRICT;

-- team
ALTER TABLE team
    ADD CONSTRAINT fk_team_sport FOREIGN KEY (sport_id)
        REFERENCES sport (sport_id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_team_coach FOREIGN KEY (coach_id)
        REFERENCES coach (coach_id) ON DELETE SET NULL;

-- team_member
ALTER TABLE team_member
    ADD CONSTRAINT fk_tm_team   FOREIGN KEY (team_id)   REFERENCES team (team_id)     ON DELETE CASCADE,
    ADD CONSTRAINT fk_tm_member FOREIGN KEY (member_id) REFERENCES member (member_id) ON DELETE CASCADE;

-- training_session
ALTER TABLE training_session
    ADD CONSTRAINT fk_session_team     FOREIGN KEY (team_id)     REFERENCES team (team_id)         ON DELETE RESTRICT,
    ADD CONSTRAINT fk_session_facility FOREIGN KEY (facility_id) REFERENCES facility (facility_id) ON DELETE RESTRICT;

-- tournament
ALTER TABLE tournament
    ADD CONSTRAINT fk_tournament_sport FOREIGN KEY (sport_id)
        REFERENCES sport (sport_id) ON DELETE RESTRICT;

-- fixture
ALTER TABLE fixture
    ADD CONSTRAINT fk_fixture_tournament FOREIGN KEY (tournament_id)
        REFERENCES tournament (tournament_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_fixture_facility FOREIGN KEY (facility_id)
        REFERENCES facility (facility_id) ON DELETE RESTRICT;

-- fixture_participant
ALTER TABLE fixture_participant
    ADD CONSTRAINT fk_fp_fixture FOREIGN KEY (fixture_id) REFERENCES fixture (fixture_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_fp_team    FOREIGN KEY (team_id)    REFERENCES team (team_id)    ON DELETE RESTRICT;

-- equipment
ALTER TABLE equipment
    ADD CONSTRAINT fk_equipment_sport FOREIGN KEY (sport_id)
        REFERENCES sport (sport_id) ON DELETE RESTRICT;

-- equipment_issue
ALTER TABLE equipment_issue
    ADD CONSTRAINT fk_issue_equipment FOREIGN KEY (equipment_id)
        REFERENCES equipment (equipment_id) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_issue_member FOREIGN KEY (member_id)
        REFERENCES member (member_id) ON DELETE RESTRICT;

-- =============================================================================
-- EXCLUSION CONSTRAINTS (require btree_gist extension)
-- Prevents overlapping bookings for the same facility.
-- =============================================================================

ALTER TABLE training_session
    ADD CONSTRAINT excl_session_no_overlap
        EXCLUDE USING GIST (
            facility_id WITH =,
            tsrange(start_time, end_time) WITH &&
        );

ALTER TABLE fixture
    ADD CONSTRAINT excl_fixture_no_overlap
        EXCLUDE USING GIST (
            facility_id WITH =,
            tsrange(start_time, end_time) WITH &&
        );

-- Prevent a team from having two training sessions at the same time
ALTER TABLE training_session
    ADD CONSTRAINT excl_team_session_no_overlap
        EXCLUDE USING GIST (
            team_id WITH =,
            tsrange(start_time, end_time) WITH &&
        );
