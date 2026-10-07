# Business Rules & Constraints

This document defines the strict business rules that govern the database design and application logic. These rules will be enforced via table constraints (CHECK, UNIQUE, FKs) or database triggers where constraints are insufficient.

## 1. Member and Identity Rules
- **BR1-01**: Members must have valid, unique contact information (Email must be strictly unique).
- **BR1-02**: A member cannot participate in club activities (teams, training, fixtures) unless they have an *active* membership.

## 2. Scheduling and Booking Rules
- **BR2-01**: A facility cannot have overlapping bookings. If a facility is booked for a training session or fixture, no other event can be scheduled there simultaneously.
- **BR2-02**: A team cannot have overlapping schedules (cannot participate in a training session and a fixture, or two fixtures, at the exact same time).
- **BR2-03**: A member cannot be assigned to conflicting team schedules (if a member is on multiple teams, those teams cannot have overlapping events).

## 3. Capacity and Roster Constraints
- **BR3-01**: A team cannot exceed its defined roster capacity constraint.
- **BR3-02**: The participant count for a training session cannot exceed the associated facility's maximum capacity.

## 4. Equipment Management Rules
- **BR4-01**: Equipment issued to a member cannot exceed the currently available stock for that item.
- **BR4-02**: Equipment return quantities cannot exceed the quantities originally issued.
- **BR4-03**: An equipment return date cannot be chronologically before its issue date.

## 5. Financial Rules
- **BR5-01**: Financial amounts (membership plan fees, payment amounts) must be strictly non-negative (>= 0).

## 6. Scoring and Results Rules
- **BR6-01**: Fixture scores must be valid non-negative integer values.

## 7. General Database Integrity Rules
- **BR7-01**: All required fields must use `NOT NULL` constraints.
- **BR7-02**: Surrogate primary keys (e.g., UUIDs or Identity columns) will be used for all main entities.
- **BR7-03**: Referential integrity must be strictly enforced using Foreign Keys with appropriate `ON DELETE` actions (usually `RESTRICT` or `CASCADE` where sensible).
- **BR7-04**: Critical multi-step operations (e.g., issuing equipment and decrementing stock) must be wrapped in ACID-compliant transactions.
