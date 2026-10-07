-- =============================================================================
-- 02_schema.sql
-- Core table definitions for the WoxuDB
-- Execute AFTER 01_extensions.sql
-- =============================================================================

-- Drop schema and recreate cleanly (useful for development resets)
-- WARNING: This will destroy all existing data.
DROP TABLE IF EXISTS equipment_issue CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS fixture_participant CASCADE;
DROP TABLE IF EXISTS fixture CASCADE;
DROP TABLE IF EXISTS tournament CASCADE;
DROP TABLE IF EXISTS training_session CASCADE;
DROP TABLE IF EXISTS team_member CASCADE;
DROP TABLE IF EXISTS team CASCADE;
DROP TABLE IF EXISTS coach CASCADE;
DROP TABLE IF EXISTS facility CASCADE;
DROP TABLE IF EXISTS sport CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS membership CASCADE;
DROP TABLE IF EXISTS membership_plan CASCADE;
DROP TABLE IF EXISTS member CASCADE;

-- =============================================================================
-- LOOKUP / CORE ENTITIES
-- =============================================================================

-- 1. SPORT
--    Root entity. Categorizes teams, coaches, tournaments, equipment.
CREATE TABLE sport (
    sport_id    SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL
);

-- 2. MEMBER
--    Core stakeholder of the club.
CREATE TABLE member (
    member_id     SERIAL PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    phone         VARCHAR(20),
    date_of_birth DATE         NOT NULL,
    join_date     DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- 3. MEMBERSHIP_PLAN
--    Defines the type of membership (e.g., Monthly, Annual).
CREATE TABLE membership_plan (
    plan_id          SERIAL PRIMARY KEY,
    name             VARCHAR(50)    NOT NULL,
    duration_months  INT            NOT NULL,
    fee              NUMERIC(10, 2) NOT NULL
);

-- 4. MEMBERSHIP
--    Associates a member with a plan over a specific period.
CREATE TABLE membership (
    membership_id SERIAL PRIMARY KEY,
    member_id     INT         NOT NULL,
    plan_id       INT         NOT NULL,
    start_date    DATE        NOT NULL,
    end_date      DATE        NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'Active'
);

-- 5. PAYMENT
--    Tracks fee transactions against memberships.
CREATE TABLE payment (
    payment_id    SERIAL PRIMARY KEY,
    membership_id INT            NOT NULL,
    amount        NUMERIC(10, 2) NOT NULL,
    payment_date  TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes         VARCHAR(255)
);

-- =============================================================================
-- SPORTS / CLUB OPERATIONS
-- =============================================================================

-- 6. COACH
--    A qualified individual who manages/trains a team.
CREATE TABLE coach (
    coach_id   SERIAL PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NOT NULL,
    phone      VARCHAR(20),
    sport_id   INT          NOT NULL
);

-- 7. FACILITY
--    A bookable physical space within the club.
CREATE TABLE facility (
    facility_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    location     VARCHAR(150),
    max_capacity INT          NOT NULL
);

-- 8. TEAM
--    A group of members competing/training in a sport.
CREATE TABLE team (
    team_id      SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    sport_id     INT          NOT NULL,
    coach_id     INT,
    max_capacity INT          NOT NULL DEFAULT 20
);

-- 9. TEAM_MEMBER (Associative)
--    Resolves the M:N relationship between Team and Member.
CREATE TABLE team_member (
    team_id     INT  NOT NULL,
    member_id   INT  NOT NULL,
    joined_date DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (team_id, member_id)
);

-- =============================================================================
-- SCHEDULING
-- =============================================================================

-- 10. TRAINING_SESSION
--     A scheduled practice session for a team at a facility.
CREATE TABLE training_session (
    session_id  SERIAL    PRIMARY KEY,
    team_id     INT       NOT NULL,
    facility_id INT       NOT NULL,
    start_time  TIMESTAMP NOT NULL,
    end_time    TIMESTAMP NOT NULL
);

-- =============================================================================
-- TOURNAMENTS & FIXTURES
-- =============================================================================

-- 11. TOURNAMENT
--     A competitive event for a specific sport.
CREATE TABLE tournament (
    tournament_id SERIAL PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    sport_id      INT          NOT NULL,
    start_date    DATE         NOT NULL,
    end_date      DATE         NOT NULL
);

-- 12. FIXTURE
--     A specific match within a tournament.
CREATE TABLE fixture (
    fixture_id    SERIAL    PRIMARY KEY,
    tournament_id INT       NOT NULL,
    facility_id   INT       NOT NULL,
    start_time    TIMESTAMP NOT NULL,
    end_time      TIMESTAMP NOT NULL
);

-- 13. FIXTURE_PARTICIPANT (Associative)
--     Resolves the M:N relationship between Fixture and Team, also stores scores.
CREATE TABLE fixture_participant (
    fixture_id INT NOT NULL,
    team_id    INT NOT NULL,
    score      INT NOT NULL DEFAULT 0,
    PRIMARY KEY (fixture_id, team_id)
);

-- =============================================================================
-- EQUIPMENT
-- =============================================================================

-- 14. EQUIPMENT
--     Sporting assets owned by the club.
CREATE TABLE equipment (
    equipment_id  SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    sport_id      INT          NOT NULL,
    total_stock   INT          NOT NULL DEFAULT 0,
    current_stock INT          NOT NULL DEFAULT 0
);

-- 15. EQUIPMENT_ISSUE
--     Tracks the borrowing and return of equipment by members.
CREATE TABLE equipment_issue (
    issue_id             SERIAL PRIMARY KEY,
    equipment_id         INT  NOT NULL,
    member_id            INT  NOT NULL,
    issue_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_return_date DATE NOT NULL,
    actual_return_date   DATE,
    quantity             INT  NOT NULL
);
