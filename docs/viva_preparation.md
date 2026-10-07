# Viva Preparation Guide for WoxuDB

This document provides a comprehensive Q&A guide for the university defense/viva of the WoxuDB (WoxuDB) DBMS project.

## 1. Database Design & Architecture

**Q1: Why did you choose PostgreSQL for this project?**
**A:** PostgreSQL is a powerful, open-source object-relational database system known for its strict adherence to SQL standards, ACID compliance, and robust data integrity features. For a sports club handling memberships and payments, data integrity is critical. We also utilized advanced features like `pg_trgm` (for fuzzy search) and `btree_gist` (for exclusion constraints to prevent facility double-booking).

**Q2: How did you ensure the database is normalized?**
**A:** The database is normalized up to the Third Normal Form (3NF). 
- **1NF**: All tables have a primary key (`SERIAL`), and all fields contain atomic values. 
- **2NF**: All non-key attributes are fully dependent on the entire primary key (e.g., in `team_members`, the `join_date` depends on both `team_id` and `member_id`). 
- **3NF**: There are no transitive dependencies. For example, instead of storing a coach's name inside the `teams` table, we store `coach_id` which references the `coaches` table.

**Q3: Explain how you resolved Many-to-Many (M:N) relationships.**
**A:** M:N relationships cannot be directly implemented in a relational database. I resolved them by introducing **associative (junction) tables**. For instance, a member can be in multiple teams, and a team has multiple members. I created the `team_members` table with a composite primary key (`team_id`, `member_id`) to resolve this. Similarly, I used `team_coaches` and `fixture_participants`.

## 2. Constraints and Triggers

**Q4: How do you prevent two training sessions from happening at the same facility at the same time?**
**A:** I used an **EXCLUDE constraint** utilizing the `btree_gist` extension in PostgreSQL. The constraint ensures that for the same `facility_id`, the time ranges (`start_time`, `end_time`) cannot overlap. 

**Q5: What triggers did you implement and why?**
**A:** Triggers were used to enforce complex business logic that cannot be handled by simple `CHECK` constraints:
1. **Equipment Stock Trigger**: Automatically updates `available_stock` when an item is issued or returned.
2. **Team Capacity Trigger**: Prevents adding a member to a team if it exceeds `max_capacity`.
3. **Membership Auto-Expire**: Ensures a member's status changes to 'Expired' once the `end_date` passes.

## 3. SQL Queries & Reporting

**Q6: What kind of advanced SQL features did you use?**
**A:** I used a variety of advanced SQL features in the `db/07_reports.sql` file:
- **Window Functions**: `RANK() OVER(PARTITION BY...)` was used to rank teams within a tournament based on their scores.
- **Aggregations**: `SUM`, `COUNT`, `AVG` were used in financial reports grouped by membership plans.
- **Subqueries**: Used in the `v_unpaid_memberships` view (`WHERE membership_id NOT IN (SELECT membership_id FROM payment)`) to find members who haven't paid.
- **Views**: Complex joins were abstracted into views (e.g., `v_active_members`, `v_equipment_status`) so the application backend can query them simply.

## 4. Application Integration

**Q7: How does your backend connect to PostgreSQL?**
**A:** I built the backend using **Python** and **FastAPI**, and I used the **psycopg3** library with `AsyncConnectionPool`. This provides asynchronous, non-blocking database connections which scale well for web applications.

**Q8: What happens if a payment fails halfway through?**
**A:** All critical operations are wrapped in **database transactions** (`with db.transaction():`). If an error occurs (e.g., the payment amount is negative, violating a check constraint), the entire block rolls back, ensuring the database is never left in an inconsistent state.

## 5. Security & Validation

**Q9: How do you validate user inputs?**
**A:** Validation happens at three levels:
1. **Frontend**: HTML5 constraints (`required`, `type="number"`, `min="1"`).
2. **Backend**: FastAPI enforces data types automatically, rejecting invalid payloads.
3. **Database**: The ultimate source of truth. The DB enforces `NOT NULL`, `UNIQUE` (for emails), `CHECK` constraints (e.g., `amount > 0`), and Foreign Keys to prevent orphaned records.
