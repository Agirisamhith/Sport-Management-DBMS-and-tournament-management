# Data Dictionary

## 1. member
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| member_id     | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| first_name    | VARCHAR(50)   | NOT NULL                                 | Member's first name                |
| last_name     | VARCHAR(50)   | NOT NULL                                 | Member's last name                 |
| email         | VARCHAR(100)  | NOT NULL, UNIQUE                         | Contact email                      |
| phone         | VARCHAR(20)   | UNIQUE                                   | Contact phone number               |
| date_of_birth | DATE          | NOT NULL, CHECK (date_of_birth < today)  | Member's DOB                       |
| join_date     | DATE          | NOT NULL, DEFAULT CURRENT_DATE           | Date the member joined the club    |

## 2. membership_plan
| Column Name     | Data Type     | Constraints                       | Description                        |
| --------------- | ------------- | --------------------------------- | ---------------------------------- |
| plan_id         | SERIAL        | PRIMARY KEY                       | Surrogate key                      |
| name            | VARCHAR(50)   | NOT NULL, UNIQUE                  | e.g., 'Annual Basic'               |
| duration_months | INT           | NOT NULL, CHECK (> 0)             | Validity in months                 |
| fee             | NUMERIC(10,2) | NOT NULL, CHECK (fee >= 0)        | Cost of the plan                   |

## 3. membership
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| membership_id | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| member_id     | INT           | NOT NULL, FK (member.member_id)          | Associated member                  |
| plan_id       | INT           | NOT NULL, FK (membership_plan.plan_id)   | Associated plan                    |
| start_date    | DATE          | NOT NULL                                 | Start of validity                  |
| end_date      | DATE          | NOT NULL, CHECK (end_date > start_date)  | End of validity                    |
| status        | VARCHAR(20)   | NOT NULL, DEFAULT 'Active'               | 'Active', 'Expired', 'Cancelled'   |

## 4. payment
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| payment_id    | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| membership_id | INT           | NOT NULL, FK (membership.membership_id)  | Associated membership              |
| amount        | NUMERIC(10,2) | NOT NULL, CHECK (amount > 0)             | Amount paid                        |
| payment_date  | TIMESTAMP     | NOT NULL, DEFAULT CURRENT_TIMESTAMP      | When the payment occurred          |

## 5. sport
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| sport_id      | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| name          | VARCHAR(50)   | NOT NULL, UNIQUE                         | Sport name (e.g., 'Tennis')        |

## 6. coach
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| coach_id      | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| first_name    | VARCHAR(50)   | NOT NULL                                 | Coach's first name                 |
| last_name     | VARCHAR(50)   | NOT NULL                                 | Coach's last name                  |
| email         | VARCHAR(100)  | NOT NULL, UNIQUE                         | Contact email                      |
| sport_id      | INT           | NOT NULL, FK (sport.sport_id)            | Primary specialization             |

## 7. team
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| team_id       | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| name          | VARCHAR(100)  | NOT NULL, UNIQUE                         | Team name                          |
| sport_id      | INT           | NOT NULL, FK (sport.sport_id)            | Sport played                       |
| coach_id      | INT           | FK (coach.coach_id)                      | Managing coach                     |
| max_capacity  | INT           | NOT NULL, CHECK (max_capacity > 0)       | Roster limit                       |

## 8. team_member
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| team_id       | INT           | PK, FK (team.team_id)                    | Team reference                     |
| member_id     | INT           | PK, FK (member.member_id)                | Member reference                   |
| joined_date   | DATE          | NOT NULL, DEFAULT CURRENT_DATE           | Date joined the team               |

## 9. facility
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| facility_id   | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| name          | VARCHAR(100)  | NOT NULL, UNIQUE                         | Facility name                      |
| max_capacity  | INT           | NOT NULL, CHECK (max_capacity > 0)       | Max allowable people               |

## 10. training_session
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| session_id    | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| team_id       | INT           | NOT NULL, FK (team.team_id)              | Team participating                 |
| facility_id   | INT           | NOT NULL, FK (facility.facility_id)      | Location                           |
| start_time    | TIMESTAMP     | NOT NULL                                 | Session start                      |
| end_time      | TIMESTAMP     | NOT NULL, CHECK (end_time > start_time)  | Session end                        |

## 11. tournament
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| tournament_id | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| name          | VARCHAR(150)  | NOT NULL, UNIQUE                         | Tournament name                    |
| sport_id      | INT           | NOT NULL, FK (sport.sport_id)            | Sport type                         |
| start_date    | DATE          | NOT NULL                                 | Start date                         |
| end_date      | DATE          | NOT NULL, CHECK (end_date >= start_date) | End date                           |

## 12. fixture
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| fixture_id    | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| tournament_id | INT           | NOT NULL, FK (tournament.tournament_id)  | Associated tournament              |
| facility_id   | INT           | NOT NULL, FK (facility.facility_id)      | Match location                     |
| start_time    | TIMESTAMP     | NOT NULL                                 | Match start                        |
| end_time      | TIMESTAMP     | NOT NULL, CHECK (end_time > start_time)  | Match end                          |

## 13. fixture_participant
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| fixture_id    | INT           | PK, FK (fixture.fixture_id)              | Match reference                    |
| team_id       | INT           | PK, FK (team.team_id)                    | Team reference                     |
| score         | INT           | DEFAULT 0, CHECK (score >= 0)            | Points scored                      |

## 14. equipment
| Column Name   | Data Type     | Constraints                              | Description                        |
| ------------- | ------------- | ---------------------------------------- | ---------------------------------- |
| equipment_id  | SERIAL        | PRIMARY KEY                              | Surrogate key                      |
| name          | VARCHAR(100)  | NOT NULL                                 | Equipment name                     |
| sport_id      | INT           | NOT NULL, FK (sport.sport_id)            | Associated sport                   |
| total_stock   | INT           | NOT NULL, CHECK (total_stock >= 0)       | Total owned                        |
| current_stock | INT           | NOT NULL, CHECK (current_stock >= 0)     | Currently available                |

## 15. equipment_issue
| Column Name          | Data Type     | Constraints                                         | Description                    |
| -------------------- | ------------- | --------------------------------------------------- | ------------------------------ |
| issue_id             | SERIAL        | PRIMARY KEY                                         | Surrogate key                  |
| equipment_id         | INT           | NOT NULL, FK (equipment.equipment_id)               | Item borrowed                  |
| member_id            | INT           | NOT NULL, FK (member.member_id)                     | Member borrowing               |
| issue_date           | DATE          | NOT NULL, DEFAULT CURRENT_DATE                      | Date issued                    |
| expected_return_date | DATE          | NOT NULL, CHECK (expected_return_date >= issue_date)| Due date                       |
| actual_return_date   | DATE          | CHECK (actual_return_date >= issue_date)            | Date returned (NULL if pending)|
| quantity             | INT           | NOT NULL, CHECK (quantity > 0)                      | Amount borrowed                |
