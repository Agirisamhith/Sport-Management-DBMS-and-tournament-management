# Initial Relational Schema: Sports Club Management System

## 1. `members`
- **Purpose**: Stores information about club members.
- **Columns**:
  - `member_id` (SERIAL): **Primary Key**
  - `first_name` (VARCHAR)
  - `last_name` (VARCHAR)
  - `email` (VARCHAR): **UNIQUE**
  - `phone` (VARCHAR)
  - `join_date` (DATE)
- **Important Relationships**: Has many `memberships`, `payments`, `team_members`, `equipment_issues`.

## 2. `membership_plans`
- **Purpose**: Defines available membership tiers/plans.
- **Columns**:
  - `plan_id` (SERIAL): **Primary Key**
  - `name` (VARCHAR): **UNIQUE**
  - `description` (TEXT)
  - `price` (NUMERIC)
  - `duration_days` (INTEGER)
- **Important Relationships**: Defines many `memberships`.

## 3. `memberships`
- **Purpose**: Links members to specific plans for a time period.
- **Columns**:
  - `membership_id` (SERIAL): **Primary Key**
  - `member_id` (INTEGER): **Foreign Key** -> `members.member_id`
  - `plan_id` (INTEGER): **Foreign Key** -> `membership_plans.plan_id`
  - `start_date` (DATE)
  - `end_date` (DATE)
  - `status` (VARCHAR)
- **Important Relationships**: Maps `members` to `membership_plans`.

## 4. `payments`
- **Purpose**: Records financial transactions made by members.
- **Columns**:
  - `payment_id` (SERIAL): **Primary Key**
  - `member_id` (INTEGER): **Foreign Key** -> `members.member_id`
  - `amount` (NUMERIC)
  - `payment_date` (DATE)
  - `payment_method` (VARCHAR)
- **Important Relationships**: Belongs to `members`.

## 5. `sports`
- **Purpose**: Catalog of sports offered by the club.
- **Columns**:
  - `sport_id` (SERIAL): **Primary Key**
  - `name` (VARCHAR): **UNIQUE**
  - `description` (TEXT)
- **Important Relationships**: Has many `teams`, `tournaments`.

## 6. `teams`
- **Purpose**: Groups of members participating in a specific sport.
- **Columns**:
  - `team_id` (SERIAL): **Primary Key**
  - `sport_id` (INTEGER): **Foreign Key** -> `sports.sport_id`
  - `name` (VARCHAR)
  - `max_capacity` (INTEGER)
- **Important Relationships**: Belongs to `sports`. Has many `team_members`, `team_coaches`, `training_sessions`, `fixture_participants`.

## 7. `team_members`
- **Purpose**: Associative table linking members to teams.
- **Columns**:
  - `team_id` (INTEGER): **Primary Key**, **Foreign Key** -> `teams.team_id`
  - `member_id` (INTEGER): **Primary Key**, **Foreign Key** -> `members.member_id`
  - `join_date` (DATE)
- **Important Relationships**: Resolves M:N between `teams` and `members`.

## 8. `coaches`
- **Purpose**: Stores information about club coaches.
- **Columns**:
  - `coach_id` (SERIAL): **Primary Key**
  - `first_name` (VARCHAR)
  - `last_name` (VARCHAR)
  - `email` (VARCHAR): **UNIQUE**
  - `specialization` (VARCHAR)
- **Important Relationships**: Has many `team_coaches`, `training_sessions`.

## 9. `team_coaches`
- **Purpose**: Associative table linking coaches to teams.
- **Columns**:
  - `team_id` (INTEGER): **Primary Key**, **Foreign Key** -> `teams.team_id`
  - `coach_id` (INTEGER): **Primary Key**, **Foreign Key** -> `coaches.coach_id`
  - `role` (VARCHAR)
- **Important Relationships**: Resolves M:N between `teams` and `coaches`.

## 10. `facilities`
- **Purpose**: Physical locations (courts, fields, rooms) available for use.
- **Columns**:
  - `facility_id` (SERIAL): **Primary Key**
  - `name` (VARCHAR): **UNIQUE**
  - `facility_type` (VARCHAR)
  - `capacity` (INTEGER)
- **Important Relationships**: Hosts many `training_sessions`, `fixtures`.

## 11. `training_sessions`
- **Purpose**: Scheduled training events for teams.
- **Columns**:
  - `session_id` (SERIAL): **Primary Key**
  - `facility_id` (INTEGER): **Foreign Key** -> `facilities.facility_id`
  - `team_id` (INTEGER): **Foreign Key** -> `teams.team_id`
  - `coach_id` (INTEGER): **Foreign Key** -> `coaches.coach_id` (Nullable)
  - `start_time` (TIMESTAMP)
  - `end_time` (TIMESTAMP)
- **Important Relationships**: Belongs to `facilities`, `teams`, `coaches`.

## 12. `tournaments`
- **Purpose**: Organized competitions for specific sports.
- **Columns**:
  - `tournament_id` (SERIAL): **Primary Key**
  - `sport_id` (INTEGER): **Foreign Key** -> `sports.sport_id`
  - `name` (VARCHAR)
  - `start_date` (DATE)
  - `end_date` (DATE)
- **Important Relationships**: Belongs to `sports`. Has many `fixtures`.

## 13. `fixtures`
- **Purpose**: Individual matches or events within a tournament.
- **Columns**:
  - `fixture_id` (SERIAL): **Primary Key**
  - `tournament_id` (INTEGER): **Foreign Key** -> `tournaments.tournament_id`
  - `facility_id` (INTEGER): **Foreign Key** -> `facilities.facility_id`
  - `start_time` (TIMESTAMP)
  - `status` (VARCHAR)
- **Important Relationships**: Belongs to `tournaments`, `facilities`. Has many `fixture_participants`, `results`.

## 14. `fixture_participants`
- **Purpose**: Links teams or individual members as participants in a fixture.
- **Columns**:
  - `participant_id` (SERIAL): **Primary Key**
  - `fixture_id` (INTEGER): **Foreign Key** -> `fixtures.fixture_id`
  - `team_id` (INTEGER): **Foreign Key** -> `teams.team_id` (Nullable)
  - `member_id` (INTEGER): **Foreign Key** -> `members.member_id` (Nullable)
  - **Note**: A CHECK constraint will ensure exactly one of `team_id` or `member_id` is NOT NULL.
- **Important Relationships**: Belongs to `fixtures`, `teams`, `members`. Has many `results`.

## 15. `results`
- **Purpose**: Records the outcome and score for a participant in a fixture.
- **Columns**:
  - `result_id` (SERIAL): **Primary Key**
  - `fixture_id` (INTEGER): **Foreign Key** -> `fixtures.fixture_id`
  - `participant_id` (INTEGER): **Foreign Key** -> `fixture_participants.participant_id`
  - `score` (INTEGER)
  - `is_winner` (BOOLEAN)
- **Important Relationships**: Belongs to `fixtures`, `fixture_participants`.

## 16. `equipment`
- **Purpose**: Inventory catalog of club equipment.
- **Columns**:
  - `equipment_id` (SERIAL): **Primary Key**
  - `name` (VARCHAR)
  - `category` (VARCHAR)
  - `total_stock` (INTEGER)
  - `available_stock` (INTEGER)
- **Important Relationships**: Has many `equipment_issues`.

## 17. `equipment_issues`
- **Purpose**: Tracks equipment borrowed by members.
- **Columns**:
  - `issue_id` (SERIAL): **Primary Key**
  - `equipment_id` (INTEGER): **Foreign Key** -> `equipment.equipment_id`
  - `member_id` (INTEGER): **Foreign Key** -> `members.member_id`
  - `issue_date` (DATE)
  - `return_date` (DATE) (Nullable until returned)
  - `status` (VARCHAR)
- **Important Relationships**: Links `equipment` to `members`.

## Consistency Audit
- **Every FK must reference an existing PK/UNIQUE key**: Verified.
- **Every M:N relationship must have an associative table**: Verified (`team_members`, `team_coaches`, `fixture_participants`).
- **No obvious repeating groups**: Verified (data is normalized).
- **No unnecessary duplicate attributes**: Verified.
- **Naming must be consistent**: Plural table names, singular snake_case column names.
- **Review 1 documentation must match the proposed schema**: Verified.
