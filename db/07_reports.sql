-- =============================================================================
-- 07_reports.sql
-- Analytical queries for reporting dashboard
-- Execute AFTER 06_sample_data.sql
-- =============================================================================

-- =============================================================================
-- REPORT 1: Active Members Summary
-- Shows all currently active members with their plan details.
-- =============================================================================
-- VIEW: v_active_members
CREATE OR REPLACE VIEW v_active_members AS
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name  AS full_name,
    m.email,
    mp.name                              AS plan_name,
    ms.start_date,
    ms.end_date,
    (ms.end_date - CURRENT_DATE)        AS days_remaining
FROM member m
JOIN membership ms ON ms.member_id = m.member_id AND ms.status = 'Active'
JOIN membership_plan mp ON mp.plan_id = ms.plan_id
ORDER BY ms.end_date;


-- =============================================================================
-- REPORT 2: Revenue Summary by Plan
-- Total revenue grouped by membership plan type.
-- =============================================================================
CREATE OR REPLACE VIEW v_revenue_by_plan AS
SELECT
    mp.name                  AS plan_name,
    COUNT(p.payment_id)      AS total_payments,
    SUM(p.amount)            AS total_revenue,
    AVG(p.amount)            AS avg_payment
FROM payment p
JOIN membership ms ON ms.membership_id = p.membership_id
JOIN membership_plan mp ON mp.plan_id = ms.plan_id
GROUP BY mp.plan_id, mp.name
ORDER BY total_revenue DESC;


-- =============================================================================
-- REPORT 3: Tournament Results Leaderboard
-- Ranks teams by score within each tournament.
-- =============================================================================
CREATE OR REPLACE VIEW v_tournament_results AS
SELECT
    t.name          AS tournament_name,
    s.name          AS sport,
    tm.name         AS team_name,
    fp.score,
    f.start_time    AS match_time,
    RANK() OVER (
        PARTITION BY t.tournament_id
        ORDER BY fp.score DESC
    )               AS team_rank
FROM fixture_participant fp
JOIN fixture f          ON f.fixture_id    = fp.fixture_id
JOIN tournament t       ON t.tournament_id = f.tournament_id
JOIN team tm            ON tm.team_id      = fp.team_id
JOIN sport s            ON s.sport_id      = t.sport_id
ORDER BY t.tournament_id, team_rank;


-- =============================================================================
-- REPORT 4: Equipment Status Report
-- Current stock vs. total stock, highlighting low-stock items.
-- =============================================================================
CREATE OR REPLACE VIEW v_equipment_status AS
SELECT
    e.equipment_id,
    e.name                                      AS equipment_name,
    s.name                                      AS sport,
    e.total_stock,
    e.current_stock,
    (e.total_stock - e.current_stock)           AS items_on_loan,
    CASE
        WHEN e.current_stock = 0 THEN 'Out of Stock'
        WHEN e.current_stock <= (e.total_stock * 0.2) THEN 'Low Stock'
        ELSE 'Available'
    END                                         AS stock_status
FROM equipment e
JOIN sport s ON s.sport_id = e.sport_id
ORDER BY items_on_loan DESC;


-- =============================================================================
-- REPORT 5: Overdue Equipment Returns
-- Members who have not returned equipment past the expected return date.
-- =============================================================================
CREATE OR REPLACE VIEW v_overdue_equipment AS
SELECT
    ei.issue_id,
    m.first_name || ' ' || m.last_name          AS member_name,
    m.email,
    e.name                                       AS equipment_name,
    ei.quantity,
    ei.issue_date,
    ei.expected_return_date,
    (CURRENT_DATE - ei.expected_return_date)     AS days_overdue
FROM equipment_issue ei
JOIN member m    ON m.member_id    = ei.member_id
JOIN equipment e ON e.equipment_id = ei.equipment_id
WHERE ei.actual_return_date IS NULL
  AND ei.expected_return_date < CURRENT_DATE
ORDER BY days_overdue DESC;


-- =============================================================================
-- REPORT 6: Team Roster Report
-- Shows each team with its members and occupancy.
-- =============================================================================
CREATE OR REPLACE VIEW v_team_roster AS
SELECT
    t.name                AS team_name,
    sp.name               AS sport,
    c.first_name || ' ' || c.last_name  AS coach,
    m.first_name || ' ' || m.last_name  AS member_name,
    tm.joined_date,
    t.max_capacity,
    COUNT(tm2.member_id) OVER (PARTITION BY t.team_id) AS current_size
FROM team t
JOIN sport s    ON s.sport_id   = t.sport_id
JOIN sport sp   ON sp.sport_id  = t.sport_id
LEFT JOIN coach c    ON c.coach_id  = t.coach_id
JOIN team_member tm  ON tm.team_id  = t.team_id
JOIN member m        ON m.member_id = tm.member_id
JOIN team_member tm2 ON tm2.team_id = t.team_id
ORDER BY t.name, m.last_name;


-- =============================================================================
-- REPORT 7: Upcoming Training Sessions
-- Next 30 days of scheduled sessions.
-- =============================================================================
CREATE OR REPLACE VIEW v_upcoming_sessions AS
SELECT
    ts.session_id,
    t.name            AS team_name,
    sp.name           AS sport,
    f.name            AS facility,
    ts.start_time,
    ts.end_time,
    EXTRACT(EPOCH FROM (ts.end_time - ts.start_time)) / 3600 AS duration_hours
FROM training_session ts
JOIN team     t  ON t.team_id     = ts.team_id
JOIN sport    sp ON sp.sport_id   = t.sport_id
JOIN facility f  ON f.facility_id = ts.facility_id
WHERE ts.start_time BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '30 days'
ORDER BY ts.start_time;


-- =============================================================================
-- REPORT 8: Membership Expiry Alerts
-- Members whose memberships expire within the next 30 days.
-- =============================================================================
CREATE OR REPLACE VIEW v_expiring_memberships AS
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.email,
    mp.name                             AS plan_name,
    ms.end_date,
    (ms.end_date - CURRENT_DATE)        AS days_until_expiry
FROM member m
JOIN membership ms       ON ms.member_id = m.member_id AND ms.status = 'Active'
JOIN membership_plan mp  ON mp.plan_id   = ms.plan_id
WHERE ms.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY ms.end_date;


-- =============================================================================
-- REPORT 9: Unpaid Memberships (Demonstrates Subquery)
-- Identifies memberships that have no associated payments yet.
-- =============================================================================
CREATE OR REPLACE VIEW v_unpaid_memberships AS
SELECT
    m.member_id,
    m.first_name || ' ' || m.last_name AS member_name,
    m.email,
    ms.membership_id,
    ms.start_date
FROM member m
JOIN membership ms ON ms.member_id = m.member_id
WHERE ms.membership_id NOT IN (
    SELECT DISTINCT membership_id 
    FROM payment
);
