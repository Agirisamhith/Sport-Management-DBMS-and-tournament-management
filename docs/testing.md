# Testing Documentation

## Test Strategy
This project uses **pytest** with **psycopg3** for direct integration tests against the PostgreSQL database. Tests are grouped by domain and use **savepoints** for automatic rollback, keeping the database clean after each test.

## Running Tests
```bash
# Install dependencies first
pip install -r requirements.txt

# Copy and configure .env with your database credentials
cp .env.example .env

# Make sure the database schema is fully loaded (scripts 01-07)

# Run all tests with verbose output
pytest tests/ -v

# Run a specific module
pytest tests/test_equipment.py -v
```

## Test Modules

### `test_members.py` — Member Constraints
| Test | Description |
|---|---|
| `test_member_insert_and_select` | Valid member can be inserted and retrieved |
| `test_member_email_unique_constraint` | Duplicate emails are rejected (UNIQUE) |
| `test_member_dob_check_constraint` | Future date of birth is rejected (CHECK) |
| `test_member_not_null_constraint` | Missing required fields fail (NOT NULL) |
| `test_member_update` | Member fields can be updated |

### `test_equipment.py` — Stock Management Triggers
| Test | Description |
|---|---|
| `test_equipment_issue_reduces_stock` | Issuing equipment reduces `current_stock` |
| `test_equipment_issue_insufficient_stock` | Issuing more than available raises trigger error |
| `test_equipment_return_restores_stock` | Returning equipment restores `current_stock` |
| `test_equipment_issue_quantity_positive` | Zero/negative quantity rejected (CHECK) |
| `test_equipment_return_date_before_issue_date` | Invalid return date rejected (CHECK) |

### `test_scheduling.py` — Scheduling & Capacity
| Test | Description |
|---|---|
| `test_no_facility_overlap_for_training_sessions` | Overlapping facility bookings rejected (EXCLUSION) |
| `test_non_overlapping_sessions_allowed` | Back-to-back sessions at same facility allowed |
| `test_team_capacity_trigger` | Adding member over capacity raises trigger error |
| `test_session_time_check` | Session where end ≤ start rejected (CHECK) |

### `test_memberships.py` — Membership & Payment Rules
| Test | Description |
|---|---|
| `test_membership_creation` | Valid membership can be created |
| `test_membership_invalid_dates` | Membership where end ≤ start rejected (CHECK) |
| `test_membership_auto_expire_trigger` | Past-dated memberships auto-set to 'Expired' |
| `test_payment_requires_positive_amount` | Negative/zero payment amount rejected (CHECK) |
| `test_membership_invalid_status` | Invalid status value rejected (CHECK) |
| `test_plan_negative_fee_rejected` | Negative fee rejected (CHECK) |
