# Sports Club Membership & Tournament Management System
Authors - Sai Samhith (25WU0101008) ,  Likhith Ram (25WU0101038) , Vidhathreya (25WU0101040)

A PostgreSQL-based Database Management System designed to manage sports club memberships, payments, teams, coaches, facilities, tournaments, fixtures, and equipment.

## Project Overview

Sports clubs handle a large amount of interconnected information such as member records, memberships, payments, teams, training sessions, tournaments, fixtures, and equipment.

Managing these records manually can result in duplicate data, inconsistent information, scheduling conflicts, and difficulty tracking equipment.

This project provides a centralized relational database system that organizes these operations using a normalized 3NF database design with strong referential integrity and automated business rules.

## Objectives

- Centralize sports club information in a single database.
- Manage members and membership plans.
- Track membership payments and status.
- Manage sports, teams, coaches, and team members.
- Schedule training sessions and facilities.
- Manage tournaments and fixtures.
- Track equipment inventory and equipment issues.
- Maintain data consistency using constraints and foreign keys.
- Automate business rules using PostgreSQL triggers and functions.
- Provide analytical views for reporting and management.

## Key Features

### Membership Management
- Member registration and profile management
- Membership plan management
- Membership status and lifecycle tracking
- Payment tracking

### Team & Coaching Management
- Sports and team management
- Coach assignment
- Team membership management
- Team capacity validation

### Facility & Training Management
- Facility management
- Training session scheduling
- Prevention of conflicting facility bookings

### Tournament Management
- Tournament creation and management
- Fixture scheduling
- Team participation in fixtures
- Match score tracking

### Equipment Management
- Equipment inventory tracking
- Equipment issue and return management
- Automatic stock deduction and restoration
- Overdue equipment tracking

## Database Design

The database consists of **15 relational tables**:

1. `sport`
2. `member`
3. `membership_plan`
4. `membership`
5. `payment`
6. `coach`
7. `facility`
8. `team`
9. `team_member`
10. `training_session`
11. `tournament`
12. `fixture`
13. `fixture_participant`
14. `equipment`
15. `equipment_issue`

The database follows **Third Normal Form (3NF)**.

### Normalization

**1NF**
- Attributes are atomic.
- No repeating groups are present.
- Each record is uniquely identifiable.

**2NF**
- No partial dependencies exist.
- Junction tables use composite primary keys where required.

**3NF**
- No transitive dependencies exist.
- Independent entities such as sports, teams, tournaments, and membership plans are stored separately to reduce redundancy.

## Relationships

Some of the major relationships include:

- Member → Membership: **1:M**
- Membership Plan → Membership: **1:M**
- Membership → Payment: **1:M**
- Team ↔ Member: **M:N** through `team_member`
- Facility → Training Session: **1:M**
- Tournament → Fixture: **1:M**
- Fixture ↔ Team: **M:N** through `fixture_participant`
- Sport → Team: **1:M**
- Sport → Tournament: **1:M**
- Equipment → Equipment Issue: **1:M**
- Member → Equipment Issue: **1:M**

## PostgreSQL Features Used

The project makes use of several PostgreSQL features:

- `SERIAL` primary keys
- Primary key and foreign key constraints
- `UNIQUE` constraints
- `NOT NULL` constraints
- `CHECK` constraints
- `ON DELETE RESTRICT`
- `ON DELETE CASCADE`
- PostgreSQL extensions:
  - `pg_trgm`
  - `btree_gist`
- PL/pgSQL functions and triggers
- B-tree indexes
- GIN/trigram indexes
- GiST and range-based constraints
- Partial indexes
- Analytical SQL views

## Automated Business Logic

The database includes automated logic for important operations.

### Team Capacity
Triggers validate team capacity before adding new team members.

### Equipment Stock
When equipment is issued, available stock is automatically reduced. When equipment is returned, stock is restored.

### Membership Lifecycle
Membership status can be automatically updated based on its expiry date.

### Facility Scheduling
PostgreSQL exclusion constraints are used to prevent overlapping bookings for the same facility.

## Reporting & Analytics

The database includes analytical views and queries for:

- Revenue by membership plan
- Team rosters
- Tournament leaderboards
- Equipment stock status
- Overdue equipment
- Membership information
- Payment analysis

Aggregate functions such as `COUNT()`, `SUM()`, and `AVG()` are used along with joins, grouping, filtering, and ordering.

## Sample Data

The database includes sample records across all major modules for testing and validation.

Example populated entities include:

- 11 members
- 3 membership plans
- 11 payments
- 4 sports
- 4 teams
- 6 training sessions
- 4 fixtures
- 9 equipment records
- 5 equipment issue records

## Project Structure

```text
Sports-Club-DBMS/
│
├── sql/
│   ├── 01_extensions.sql
│   ├── 02_schema.sql
│   ├── 03_constraints.sql
│   ├── 04_triggers.sql
│   ├── 05_indexes.sql
│   ├── 06_sample_data.sql
│   └── 07_reports.sql
│
├── diagrams/
│   └── er-diagram.png
│
├── presentation/
│   └── DBMS-Presentation.pptx
│
└── README.md
