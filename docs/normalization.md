# Database Normalization and Functional Dependencies

This document details the functional dependencies identified during the design phase of WoxuDB and provides proof that the final schema satisfies the Third Normal Form (3NF).

## 1. Functional Dependencies

A functional dependency \( X \rightarrow Y \) means that the value of attribute(s) \( X \) uniquely determines the value of attribute(s) \( Y \).

### Primary Entities
* **Members**: `member_id` \( \rightarrow \) `{first_name, last_name, email, phone, dob, join_date}`
* **Sports**: `sport_id` \( \rightarrow \) `{name, description}`
* **Teams**: `team_id` \( \rightarrow \) `{sport_id, team_name, max_capacity}`
* **Coaches**: `coach_id` \( \rightarrow \) `{first_name, last_name, email, specialization}`
* **Facilities**: `facility_id` \( \rightarrow \) `{name, location, capacity}`
* **Membership Plans**: `plan_id` \( \rightarrow \) `{name, fee, duration_months, is_active}`

### Transactional & Event Entities
* **Memberships**: `membership_id` \( \rightarrow \) `{member_id, plan_id, start_date, end_date, status}`
* **Payments**: `payment_id` \( \rightarrow \) `{membership_id, amount, payment_date, payment_method}`
* **Tournaments**: `tournament_id` \( \rightarrow \) `{sport_id, name, start_date, end_date}`
* **Fixtures**: `fixture_id` \( \rightarrow \) `{tournament_id, facility_id, match_time, status}`
* **Results**: `result_id` \( \rightarrow \) `{fixture_id, winner_team_id, home_score, away_score}`
* **Equipment**: `equipment_id` \( \rightarrow \) `{sport_id, name, total_stock, available_stock}`
* **Equipment Issues**: `issue_id` \( \rightarrow \) `{equipment_id, member_id, issue_date, expected_return_date, actual_return_date, status}`

### Associative (Many-to-Many) Entities
* **Team Members**: `{team_id, member_id}` \( \rightarrow \) `{join_date}`
* **Team Coaches**: `{team_id, coach_id}` \( \rightarrow \) `{assigned_date}`
* **Fixture Participants**: `{fixture_id, team_id}` \( \rightarrow \) `{is_home}`

---

## 2. Normalization Process

### First Normal Form (1NF)
**Rule:** Each table must have a primary key, and all attributes must contain atomic values (no repeating groups).
* **Application in WoxuDB:**
  * Surrogate primary keys (`SERIAL`) were introduced for all primary entities to ensure uniqueness.
  * Multi-valued attributes (e.g., a member playing multiple sports, or a team having multiple coaches) were separated into associative tables (`team_members`, `team_coaches`).
  * Lists of items are not stored in single comma-separated strings (e.g., equipment tracking is handled individually via `equipment_issues`).

### Second Normal Form (2NF)
**Rule:** The database must be in 1NF, and all non-key attributes must be fully functionally dependent on the entire primary key (no partial dependencies).
* **Application in WoxuDB:**
  * This rule is verified against tables with composite primary keys (`team_members`, `team_coaches`, `fixture_participants`).
  * In `team_members` (PK: `team_id`, `member_id`), the attribute `join_date` depends on the *entire* combination of the team and the member. It does not depend solely on the member or the team.
  * Therefore, there are no partial dependencies.

### Third Normal Form (3NF)
**Rule:** The database must be in 2NF, and no transitive dependencies should exist (non-key attributes must not depend on other non-key attributes).
* **Application in WoxuDB:**
  * **Eliminating Coach Transitivity:** Instead of storing coach details (name, email) directly inside the `teams` table, we link them via `team_coaches` to a separate `coaches` table. This prevents the dependency `team_id` \(\rightarrow\) `coach_id` \(\rightarrow\) `coach_name`.
  * **Eliminating Membership Plan Transitivity:** In the `memberships` table, we store `plan_id` rather than duplicating the `fee` and `duration`. Thus, we remove the transitive dependency `membership_id` \(\rightarrow\) `plan_id` \(\rightarrow\) `fee`.
  * **Eliminating Score Transitivity:** `home_score` and `away_score` depend entirely on `result_id` (and the `fixture_id` it represents), not on the individual teams directly outside the context of the fixture.

## Conclusion
The WoxuDB schema successfully satisfies 3NF by ensuring all attributes depend *on the key, the whole key, and nothing but the key*. No deliberate denormalization was performed, ensuring high data integrity suited for an OLTP academic project.
