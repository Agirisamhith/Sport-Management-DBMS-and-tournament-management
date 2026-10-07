# WoxuDB

**Design and Implementation of a Database Management System for WoxuDB Membership and Tournament Management**

A university DBMS project built with **PostgreSQL**, **FastAPI (Python 3)**, and **HTML5/CSS3/JavaScript**.

---

## Quick Start

### 1. Prerequisites
- PostgreSQL 15+
- Python 3.11+
- `pip`

### 2. Database Setup
```bash
# Connect to PostgreSQL as superuser, then:
createdb sports_club_db
psql -d sports_club_db -f db/01_extensions.sql
psql -d sports_club_db -f db/02_schema.sql
psql -d sports_club_db -f db/03_constraints.sql
psql -d sports_club_db -f db/04_triggers.sql
psql -d sports_club_db -f db/05_indexes.sql
psql -d sports_club_db -f db/06_sample_data.sql
psql -d sports_club_db -f db/07_reports.sql
```

### 3. Environment Setup
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Install Dependencies & Run
```bash
pip install -r requirements.txt
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

### 5. Run Tests
```bash
pytest tests/ -v
```

---

## Database Schemas

### Entity-Relationship Diagram
`mermaid
erDiagram
    MEMBER {
        int member_id PK
        string first_name
        string last_name
        string email UK
        string phone
        date join_date
    }
    
    MEMBERSHIP_PLAN {
        int plan_id PK
        string name UK
        string description
        decimal price
        int duration_days
    }
    
    MEMBERSHIP {
        int membership_id PK
        int member_id FK
        int plan_id FK
        date start_date
        date end_date
        string status
    }
    
    PAYMENT {
        int payment_id PK
        int member_id FK
        decimal amount
        date payment_date
        string payment_method
    }
    
    SPORT {
        int sport_id PK
        string name UK
        string description
    }
    
    COACH {
        int coach_id PK
        string first_name
        string last_name
        string email UK
        string specialization
    }
    
    TEAM {
        int team_id PK
        int sport_id FK
        string name
        int max_capacity
    }
    
    TEAM_MEMBER {
        int team_id PK, FK
        int member_id PK, FK
        date join_date
    }
    
    TEAM_COACH {
        int team_id PK, FK
        int coach_id PK, FK
        string role
    }
    
    FACILITY {
        int facility_id PK
        string name UK
        string facility_type
        int capacity
    }
    
    TRAINING_SESSION {
        int session_id PK
        int facility_id FK
        int team_id FK
        int coach_id FK
        timestamp start_time
        timestamp end_time
    }
    
    TOURNAMENT {
        int tournament_id PK
        int sport_id FK
        string name
        date start_date
        date end_date
    }
    
    FIXTURE {
        int fixture_id PK
        int tournament_id FK
        int facility_id FK
        timestamp start_time
        string status
    }
    
    FIXTURE_PARTICIPANT {
        int participant_id PK
        int fixture_id FK
        int team_id FK "Optional"
        int member_id FK "Optional"
    }
    
    RESULT {
        int result_id PK
        int fixture_id FK
        int participant_id FK
        int score
        boolean is_winner
    }
    
    EQUIPMENT {
        int equipment_id PK
        string name
        string category
        int total_stock
        int available_stock
    }
    
    EQUIPMENT_ISSUE {
        int issue_id PK
        int equipment_id FK
        int member_id FK
        date issue_date
        date return_date
        string status
    }

    MEMBER ||--o{ MEMBERSHIP : "has"
    MEMBERSHIP_PLAN ||--o{ MEMBERSHIP : "defines"
    MEMBER ||--o{ PAYMENT : "makes"
    SPORT ||--o{ TEAM : "categorizes"
    TEAM ||--o{ TEAM_MEMBER : "includes"
    MEMBER ||--o{ TEAM_MEMBER : "joins"
    TEAM ||--o{ TEAM_COACH : "trained by"
    COACH ||--o{ TEAM_COACH : "trains"
    FACILITY ||--o{ TRAINING_SESSION : "hosts"
    TEAM ||--o{ TRAINING_SESSION : "attends"
    COACH ||--o{ TRAINING_SESSION : "leads"
    SPORT ||--o{ TOURNAMENT : "features"
    TOURNAMENT ||--o{ FIXTURE : "contains"
    FACILITY ||--o{ FIXTURE : "hosts"
    FIXTURE ||--|{ FIXTURE_PARTICIPANT : "involves"
    TEAM ||--o{ FIXTURE_PARTICIPANT : "competes as"
    MEMBER ||--o{ FIXTURE_PARTICIPANT : "competes as"
    FIXTURE ||--o{ RESULT : "produces"
    FIXTURE_PARTICIPANT ||--o{ RESULT : "achieves"
    MEMBER ||--o{ EQUIPMENT_ISSUE : "borrows"
    EQUIPMENT ||--o{ EQUIPMENT_ISSUE : "is issued"

`

### Relational Schema
`mermaid
erDiagram
    members {
        serial member_id PK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar phone
        date join_date
    }
    membership_plans {
        serial plan_id PK
        varchar name UK
        text description
        numeric price
        integer duration_days
    }
    memberships {
        serial membership_id PK
        integer member_id FK
        integer plan_id FK
        date start_date
        date end_date
        varchar status
    }
    payments {
        serial payment_id PK
        integer member_id FK
        numeric amount
        date payment_date
        varchar payment_method
    }
    sports {
        serial sport_id PK
        varchar name UK
        text description
    }
    teams {
        serial team_id PK
        integer sport_id FK
        varchar name
        integer max_capacity
    }
    team_members {
        integer team_id PK,FK
        integer member_id PK,FK
        date join_date
    }
    coaches {
        serial coach_id PK
        varchar first_name
        varchar last_name
        varchar email UK
        varchar specialization
    }
    team_coaches {
        integer team_id PK,FK
        integer coach_id PK,FK
        varchar role
    }
    facilities {
        serial facility_id PK
        varchar name UK
        varchar facility_type
        integer capacity
    }
    training_sessions {
        serial session_id PK
        integer facility_id FK
        integer team_id FK
        integer coach_id FK
        timestamp start_time
        timestamp end_time
    }
    tournaments {
        serial tournament_id PK
        integer sport_id FK
        varchar name
        date start_date
        date end_date
    }
    fixtures {
        serial fixture_id PK
        integer tournament_id FK
        integer facility_id FK
        timestamp start_time
        varchar status
    }
    fixture_participants {
        serial participant_id PK
        integer fixture_id FK
        integer team_id FK
        integer member_id FK
    }
    results {
        serial result_id PK
        integer fixture_id FK
        integer participant_id FK
        integer score
        boolean is_winner
    }
    equipment {
        serial equipment_id PK
        varchar name
        varchar category
        integer total_stock
        integer available_stock
    }
    equipment_issues {
        serial issue_id PK
        integer equipment_id FK
        integer member_id FK
        date issue_date
        date return_date
        varchar status
    }

    members ||--o{ memberships : "member_id"
    membership_plans ||--o{ memberships : "plan_id"
    members ||--o{ payments : "member_id"
    sports ||--o{ teams : "sport_id"
    teams ||--o{ team_members : "team_id"
    members ||--o{ team_members : "member_id"
    teams ||--o{ team_coaches : "team_id"
    coaches ||--o{ team_coaches : "coach_id"
    facilities ||--o{ training_sessions : "facility_id"
    teams ||--o{ training_sessions : "team_id"
    coaches ||--o{ training_sessions : "coach_id"
    sports ||--o{ tournaments : "sport_id"
    tournaments ||--o{ fixtures : "tournament_id"
    facilities ||--o{ fixtures : "facility_id"
    fixtures ||--o{ fixture_participants : "fixture_id"
    teams ||--o{ fixture_participants : "team_id"
    members ||--o{ fixture_participants : "member_id"
    fixtures ||--o{ results : "fixture_id"
    fixture_participants ||--o{ results : "participant_id"
    members ||--o{ equipment_issues : "member_id"
    equipment ||--o{ equipment_issues : "equipment_id"

`

## Project Structure

```
sports-club-dbms/
├── README.md
├── requirements.txt
├── .env.example
│
├── db/
│   ├── 01_extensions.sql      # pg_trgm, btree_gist
│   ├── 02_schema.sql          # All 15 table definitions
│   ├── 03_constraints.sql     # UNIQUE, CHECK, FK, EXCLUSION
│   ├── 04_triggers.sql        # 6 PL/pgSQL triggers
│   ├── 05_indexes.sql         # Performance indexes
│   ├── 06_sample_data.sql     # Sample data for all 15 entities
│   └── 07_reports.sql         # 8 analytical SQL views
│
├── docs/
│   ├── requirements.md
│   ├── er_diagram.md
│   ├── relational_schema.md
│   ├── normalization.md
│   ├── data_dictionary.md
│   ├── business_rules.md
│   ├── testing.md
│   └── final_report.md
│
├── diagrams/
│   ├── er_diagram.mmd         # Mermaid ER diagram
│   └── relational_schema.mmd  # Mermaid relational schema
│
├── app/
│   ├── app.py                 # FastAPI application factory
│   ├── db.py                  # psycopg3 async connection pool
│   ├── config.py              # Settings via pydantic-settings
│   ├── routes/                # API route handlers (12 modules)
│   ├── templates/             # Jinja2 HTML templates (7 pages)
│   ├── static/                # CSS + JS assets
│   └── utils/                 # Error handling utilities
│
└── tests/
    ├── conftest.py            # Shared fixtures with auto-rollback
    ├── test_members.py        # Member constraint tests
    ├── test_equipment.py      # Equipment trigger tests
    ├── test_scheduling.py     # Scheduling conflict tests
    └── test_memberships.py    # Membership & payment tests
```

---

## Core Entities (15 Tables)
`member`, `membership_plan`, `membership`, `payment`, `sport`, `coach`, `team`, `team_member`, `facility`, `training_session`, `tournament`, `fixture`, `fixture_participant`, `equipment`, `equipment_issue`

## API Endpoints
| Module | Prefix | Description |
|---|---|---|
| members | `/api/members` | Member CRUD + search |
| sports | `/api/sports` | Sports catalog |
| coaches | `/api/coaches` | Coach management |
| teams | `/api/teams` | Team + roster management |
| facilities | `/api/facilities` | Facility management |
| training_sessions | `/api/sessions` | Session scheduling |
| tournaments | `/api/tournaments` | Tournament + fixtures |
| fixtures | `/api/fixtures` | Fixture + score entry |
| memberships | `/api/memberships` | Plans + membership CRUD |
| payments | `/api/payments` | Payment recording |
| equipment | `/api/equipment` | Inventory + issue/return |
| reports | `/api/reports` | 8 analytical report views |

API documentation auto-generated at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Business Rules Enforced
- ✅ Unique emails for members and coaches
- ✅ Facility scheduling conflicts prevented (EXCLUSION constraint)
- ✅ Team capacity enforced by trigger
- ✅ Equipment stock managed by triggers (atomic deduct/restore)
- ✅ Memberships auto-expire past end_date (trigger)
- ✅ Fixture teams must match tournament sport (trigger)
- ✅ All financial amounts are non-negative (CHECK)
- ✅ Scores are non-negative (CHECK)
- ✅ Date/time ordering enforced (CHECK)
- ✅ Referential integrity enforced via FK constraints
