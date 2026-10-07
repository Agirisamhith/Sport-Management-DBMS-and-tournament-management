# Conceptual ER Design: Sports Club Management System

## Entity Identification & Attributes

### 1. Member
- **Primary Key**: `member_id`
- **Important Attributes**: `first_name`, `last_name`, `email`, `phone`, `join_date`
- **Candidate Keys**: `email`

### 2. Membership Plan
- **Primary Key**: `plan_id`
- **Important Attributes**: `name`, `description`, `price`, `duration_days`
- **Candidate Keys**: `name`

### 3. Membership
- **Primary Key**: `membership_id`
- **Important Attributes**: `start_date`, `end_date`, `status`
- **Foreign Keys**: `member_id`, `plan_id`

### 4. Payment
- **Primary Key**: `payment_id`
- **Important Attributes**: `amount`, `payment_date`, `payment_method`
- **Foreign Keys**: `member_id`

### 5. Sport
- **Primary Key**: `sport_id`
- **Important Attributes**: `name`, `description`
- **Candidate Keys**: `name`

### 6. Team
- **Primary Key**: `team_id`
- **Important Attributes**: `name`, `max_capacity`
- **Foreign Keys**: `sport_id`

### 7. Coach
- **Primary Key**: `coach_id`
- **Important Attributes**: `first_name`, `last_name`, `email`, `specialization`
- **Candidate Keys**: `email`

### 8. Facility
- **Primary Key**: `facility_id`
- **Important Attributes**: `name`, `facility_type`, `capacity`
- **Candidate Keys**: `name`

### 9. Training Session
- **Primary Key**: `session_id`
- **Important Attributes**: `start_time`, `end_time`
- **Foreign Keys**: `facility_id`, `team_id`, `coach_id`

### 10. Tournament
- **Primary Key**: `tournament_id`
- **Important Attributes**: `name`, `start_date`, `end_date`
- **Foreign Keys**: `sport_id`

### 11. Fixture
- **Primary Key**: `fixture_id`
- **Important Attributes**: `start_time`, `status`
- **Foreign Keys**: `tournament_id`, `facility_id`

### 12. Fixture Participant
- **Primary Key**: `participant_id`
- **Important Attributes**: None (Associative linking entity)
- **Foreign Keys**: `fixture_id`, `team_id`, `member_id`

### 13. Result
- **Primary Key**: `result_id`
- **Important Attributes**: `score`, `is_winner`
- **Foreign Keys**: `fixture_id`, `participant_id`

### 14. Equipment
- **Primary Key**: `equipment_id`
- **Important Attributes**: `name`, `category`, `total_stock`, `available_stock`

### 15. Equipment Issue
- **Primary Key**: `issue_id`
- **Important Attributes**: `issue_date`, `return_date`, `status`
- **Foreign Keys**: `equipment_id`, `member_id`

## Associative Entities (Many-to-Many Resolutions)
- **Team Member**: Resolves M:N between `Team` and `Member`. PK is composite (`team_id`, `member_id`).
- **Team Coach**: Resolves M:N between `Team` and `Coach`. PK is composite (`team_id`, `coach_id`).

## Relationships & Cardinalities
- **Member -> Membership (1:N)**: A member can have multiple historical memberships, but a membership belongs to one member. Mandatory for Membership, Optional for Member.
- **Membership Plan -> Membership (1:N)**: A plan can be applied to many memberships. Mandatory for Membership.
- **Member -> Payment (1:N)**: A member makes many payments over time. Mandatory for Payment.
- **Sport -> Team (1:N)**: A sport categorizes many teams. Mandatory for Team.
- **Team -> Team Member <- Member (M:N)**: A team has many members, a member joins many teams.
- **Team -> Team Coach <- Coach (M:N)**: A team has many coaches, a coach trains many teams.
- **Facility -> Training Session (1:N)**: A facility hosts many sessions. Mandatory for Session.
- **Team -> Training Session (1:N)**: A team attends many sessions. Mandatory for Session.
- **Coach -> Training Session (1:N)**: A coach leads many sessions. Optional for Coach.
- **Sport -> Tournament (1:N)**: A tournament is for one sport. Mandatory for Tournament.
- **Tournament -> Fixture (1:N)**: A tournament contains many fixtures. Mandatory for Fixture.
- **Facility -> Fixture (1:N)**: A facility hosts many fixtures. Mandatory for Fixture.
- **Fixture -> Fixture Participant (1:N)**: A fixture involves multiple participants (teams or individuals). Mandatory for Participant.
- **Team/Member -> Fixture Participant (1:N)**: A team or member acts as a participant in many fixtures.
- **Fixture -> Result (1:N)**: A fixture produces results for its participants. Mandatory for Result.
- **Fixture Participant -> Result (1:1/1:N)**: A participant in a fixture achieves a result. Mandatory for Result.
- **Member -> Equipment Issue <- Equipment (M:N)**: A member borrows multiple equipment items, equipment is borrowed by multiple members over time.
