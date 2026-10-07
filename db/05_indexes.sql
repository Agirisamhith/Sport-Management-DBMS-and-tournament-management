-- =============================================================================
-- 05_indexes.sql
-- Indexes for performance on frequently searched/joined columns
-- Execute AFTER 04_triggers.sql
-- =============================================================================

-- member
CREATE INDEX IF NOT EXISTS idx_member_email     ON member (email);
CREATE INDEX IF NOT EXISTS idx_member_last_name ON member (last_name);

-- membership
CREATE INDEX IF NOT EXISTS idx_membership_member_id ON membership (member_id);
CREATE INDEX IF NOT EXISTS idx_membership_plan_id   ON membership (plan_id);
CREATE INDEX IF NOT EXISTS idx_membership_status    ON membership (status);

-- payment
CREATE INDEX IF NOT EXISTS idx_payment_membership_id ON payment (membership_id);
CREATE INDEX IF NOT EXISTS idx_payment_date          ON payment (payment_date DESC);

-- team
CREATE INDEX IF NOT EXISTS idx_team_sport_id ON team (sport_id);
CREATE INDEX IF NOT EXISTS idx_team_coach_id ON team (coach_id);

-- team_member (composite already PK, add individual for reverse lookups)
CREATE INDEX IF NOT EXISTS idx_team_member_member_id ON team_member (member_id);

-- training_session
CREATE INDEX IF NOT EXISTS idx_session_team_id     ON training_session (team_id);
CREATE INDEX IF NOT EXISTS idx_session_facility_id ON training_session (facility_id);
CREATE INDEX IF NOT EXISTS idx_session_start_time  ON training_session (start_time);

-- tournament
CREATE INDEX IF NOT EXISTS idx_tournament_sport_id   ON tournament (sport_id);
CREATE INDEX IF NOT EXISTS idx_tournament_start_date ON tournament (start_date);

-- fixture
CREATE INDEX IF NOT EXISTS idx_fixture_tournament_id ON fixture (tournament_id);
CREATE INDEX IF NOT EXISTS idx_fixture_facility_id   ON fixture (facility_id);
CREATE INDEX IF NOT EXISTS idx_fixture_start_time    ON fixture (start_time);

-- fixture_participant
CREATE INDEX IF NOT EXISTS idx_fp_team_id ON fixture_participant (team_id);

-- equipment
CREATE INDEX IF NOT EXISTS idx_equipment_sport_id ON equipment (sport_id);
-- Trigram index for fuzzy name search
CREATE INDEX IF NOT EXISTS idx_equipment_name_trgm ON equipment USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_member_name_trgm    ON member    USING GIN ((first_name || ' ' || last_name) gin_trgm_ops);

-- equipment_issue
CREATE INDEX IF NOT EXISTS idx_issue_equipment_id ON equipment_issue (equipment_id);
CREATE INDEX IF NOT EXISTS idx_issue_member_id    ON equipment_issue (member_id);
CREATE INDEX IF NOT EXISTS idx_issue_date         ON equipment_issue (issue_date DESC);
-- Index for finding unreturned items quickly
CREATE INDEX IF NOT EXISTS idx_issue_unreturned   ON equipment_issue (actual_return_date)
    WHERE actual_return_date IS NULL;
