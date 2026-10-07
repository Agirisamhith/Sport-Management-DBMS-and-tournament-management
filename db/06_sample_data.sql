-- =============================================================================
-- 06_sample_data.sql
-- Representative sample data for all 15 entities
-- Execute AFTER 05_indexes.sql
-- =============================================================================

-- =============================================================================
-- 1. SPORTS
-- =============================================================================
INSERT INTO sport (name) VALUES
    ('Football'),
    ('Tennis'),
    ('Basketball'),
    ('Swimming'),
    ('Cricket');

-- =============================================================================
-- 2. MEMBERSHIP PLANS
-- =============================================================================
INSERT INTO membership_plan (name, duration_months, fee) VALUES
    ('Monthly Basic',    1, 1499.00),
    ('Quarterly Silver', 3, 3999.00),
    ('Annual Gold',     12, 14999.00),
    ('Annual Premium',  12, 24999.00);

-- =============================================================================
-- 3. MEMBERS (12 members)
-- =============================================================================
INSERT INTO member (first_name, last_name, email, phone, date_of_birth, join_date) VALUES
    ('Aarav',   'Sharma',  'aarav.sharma@email.com',  '0700-001-001', '1995-03-15', '2026-01-10'),
    ('Rohan',     'Gupta',    'rohan.gupta@email.com',      '0700-002-002', '1990-07-22', '2026-01-15'),
    ('Priya',  'Patel', 'priya.p@email.com',         '0700-003-003', '1998-11-05', '2026-02-01'),
    ('Rahul',   'Desai',    'rahul.d@email.com',        '0700-004-004', '1993-04-18', '2026-02-10'),
    ('Ananya',     'Singh',    'ananya.singh@email.com',      '0700-005-005', '2000-09-30', '2026-03-01'),
    ('Vikram',   'Mehta',   'vikram.m@email.com',        '0700-006-006', '1988-12-01', '2026-03-15'),
    ('Neha',   'Verma', 'neha.v@email.com',        '0700-007-007', '1996-06-20', '2026-04-01'),
    ('Siddharth',   'Reddy',    'siddharth.r@email.com',        '0700-008-008', '2002-01-25', '2026-04-10'),
    ('Sneha',    'Joshi',   'sneha.j@email.com',         '0700-009-009', '1997-08-14', '2026-05-01'),
    ('Aditya',    'Kumar',    'aditya.k@email.com',         '0700-010-010', '1994-02-11', '2026-05-15'),
    ('Kavya',    'Iyer',   'kavya.i@email.com',         '0700-011-011', '1999-10-03', '2026-06-01'),
    ('Karthik',    'Nair',  'karthik.n@email.com',          '0700-012-012', '1991-07-07', '2026-06-10');

-- =============================================================================
-- 4. MEMBERSHIPS
-- =============================================================================
INSERT INTO membership (member_id, plan_id, start_date, end_date, status) VALUES
    (1,  3, '2026-01-10', '2027-01-10', 'Active'),    -- Aarav: Annual Gold
    (2,  3, '2026-01-15', '2027-01-15', 'Active'),    -- Rohan: Annual Gold
    (3,  1, '2026-02-01', '2026-03-01', 'Expired'),   -- Priya: Monthly (expired)
    (4,  2, '2026-02-10', '2026-05-10', 'Expired'),   -- Rahul: Quarterly (expired)
    (5,  4, '2026-03-01', '2027-03-01', 'Active'),    -- Ananya: Annual Premium
    (6,  3, '2026-03-15', '2027-03-15', 'Active'),    -- Vikram: Annual Gold
    (7,  2, '2026-04-01', '2026-07-01', 'Active'),    -- Neha: Quarterly
    (8,  1, '2026-04-10', '2026-05-10', 'Expired'),   -- Siddharth: Monthly (expired)
    (9,  3, '2026-05-01', '2027-05-01', 'Active'),    -- Sneha: Annual Gold
    (10, 4, '2026-05-15', '2027-05-15', 'Active'),    -- Aditya: Annual Premium
    (11, 2, '2026-06-01', '2026-09-01', 'Active'),    -- Kavya: Quarterly
    (12, 3, '2026-06-10', '2027-06-10', 'Active');    -- Karthik: Annual Gold

-- =============================================================================
-- 5. PAYMENTS
-- =============================================================================
INSERT INTO payment (membership_id, amount, payment_date, notes) VALUES
    (1, 14999.00, '2026-01-10 09:00:00', 'Annual Gold - full payment'),
    (2, 14999.00, '2026-01-15 10:00:00', 'Annual Gold - full payment'),
    (3,  1499.00, '2026-02-01 11:00:00', 'Monthly Basic'),
    (4,  3999.00, '2026-02-10 12:00:00', 'Quarterly Silver'),
    (5, 24999.00, '2026-03-01 09:30:00', 'Annual Premium'),
    (6, 14999.00, '2026-03-15 14:00:00', 'Annual Gold'),
    (7,  3999.00, '2026-04-01 10:00:00', 'Quarterly Silver - first installment'),
    (8,  1499.00, '2026-04-10 08:00:00', 'Monthly Basic'),
    (9, 14999.00, '2026-05-01 09:00:00', 'Annual Gold'),
    (10, 24999.00, '2026-05-15 11:00:00', 'Annual Premium'),
    (11,  3999.00, '2026-06-01 10:00:00', 'Quarterly Silver'),
    (12, 14999.00, '2026-06-10 09:00:00', 'Annual Gold');

-- =============================================================================
-- 6. COACHES
-- =============================================================================
INSERT INTO coach (first_name, last_name, email, phone, sport_id) VALUES
    ('Arjun',   'Kapoor',    'arjun.kapoor@club.com',    '0800-001-001', 1),  -- Football
    ('Sunita',   'Rao',   'sunita.r@club.com',        '0800-002-002', 2),  -- Tennis
    ('Rajesh',   'Khanna',   'rajesh.k@club.com',        '0800-003-003', 3),  -- Basketball
    ('Maya',   'Menon',     'maya.m@club.com',        '0800-004-004', 4),  -- Swimming
    ('Sanjay',  'Verma',   'sanjay.v@club.com',       '0800-005-005', 5);  -- Cricket

-- =============================================================================
-- 7. FACILITIES
-- =============================================================================
INSERT INTO facility (name, location, max_capacity) VALUES
    ('Main Football Pitch',  'North Wing',   100),
    ('Tennis Court A',       'East Wing',     10),
    ('Tennis Court B',       'East Wing',     10),
    ('Basketball Arena',     'Central Block', 60),
    ('Olympic Swimming Pool','South Block',   40),
    ('Cricket Ground',       'West Wing',    150),
    ('Conference Room',      'Main Building', 30);

-- =============================================================================
-- 8. TEAMS
-- =============================================================================
INSERT INTO team (name, sport_id, coach_id, max_capacity) VALUES
    ('Thunder FC',        1, 1, 18),   -- Football, Coach Arjun
    ('Ace Smashers',      2, 2,  8),   -- Tennis, Coach Sunita
    ('Dunking Bears',     3, 3, 12),   -- Basketball, Coach Rajesh
    ('Wave Riders',       4, 4, 15),   -- Swimming, Coach Maya
    ('Royal Strikers',    5, 5, 11);   -- Cricket, Coach Sanjay

-- =============================================================================
-- 9. TEAM MEMBERS
-- =============================================================================
INSERT INTO team_member (team_id, member_id, joined_date) VALUES
    (1, 1, '2026-01-12'),   -- Aarav -> Thunder FC
    (1, 2, '2026-01-16'),   -- Rohan -> Thunder FC
    (1, 6, '2026-03-20'),   -- Vikram -> Thunder FC
    (2, 3, '2026-02-05'),   -- Priya -> Ace Smashers
    (2, 7, '2026-04-02'),   -- Neha -> Ace Smashers
    (3, 4, '2026-02-15'),   -- Rahul -> Dunking Bears
    (3, 8, '2026-04-12'),   -- Siddharth -> Dunking Bears
    (4, 5, '2026-03-05'),   -- Ananya -> Wave Riders
    (4, 9, '2026-05-03'),   -- Sneha -> Wave Riders
    (5, 10,'2026-05-20'),   -- Aditya -> Royal Strikers
    (5, 11,'2026-06-03'),   -- Kavya -> Royal Strikers
    (5, 12,'2026-06-12');   -- Karthik -> Royal Strikers

-- =============================================================================
-- 10. TRAINING SESSIONS
-- =============================================================================
INSERT INTO training_session (team_id, facility_id, start_time, end_time) VALUES
    (1, 1, '2026-07-01 09:00:00', '2026-07-01 11:00:00'),  -- Thunder FC, Football Pitch
    (2, 2, '2026-07-01 10:00:00', '2026-07-01 12:00:00'),  -- Ace Smashers, Tennis A
    (3, 4, '2026-07-02 08:00:00', '2026-07-02 10:00:00'),  -- Dunking Bears, Basketball Arena
    (4, 5, '2026-07-02 07:00:00', '2026-07-02 08:30:00'),  -- Wave Riders, Pool
    (5, 6, '2026-07-03 09:00:00', '2026-07-03 12:00:00'),  -- Royal Strikers, Cricket Ground
    (1, 1, '2026-07-08 09:00:00', '2026-07-08 11:00:00'),  -- Thunder FC session 2
    (2, 3, '2026-07-01 14:00:00', '2026-07-01 16:00:00');  -- Ace Smashers on Court B

-- =============================================================================
-- 11. TOURNAMENTS
-- =============================================================================
INSERT INTO tournament (name, sport_id, start_date, end_date) VALUES
    ('Summer Football League 2026', 1, '2026-07-15', '2026-08-15'),
    ('Club Tennis Open 2026',       2, '2026-07-20', '2026-07-30'),
    ('Basketball Challenge Cup',    3, '2026-08-01', '2026-08-20'),
    ('Annual Swim Gala',            4, '2026-08-10', '2026-08-11'),
    ('Cricket Premier League',      5, '2026-09-01', '2026-10-01');

-- =============================================================================
-- 12. FIXTURES
-- =============================================================================
INSERT INTO fixture (tournament_id, facility_id, start_time, end_time) VALUES
    (1, 1, '2026-07-16 15:00:00', '2026-07-16 17:00:00'),  -- Football
    (1, 1, '2026-07-23 15:00:00', '2026-07-23 17:00:00'),  -- Football round 2
    (2, 2, '2026-07-21 11:00:00', '2026-07-21 13:00:00'),  -- Tennis
    (3, 4, '2026-08-05 10:00:00', '2026-08-05 12:00:00'),  -- Basketball
    (5, 6, '2026-09-10 10:00:00', '2026-09-10 18:00:00');  -- Cricket

-- Note: For the football tournament we only have one team (Thunder FC).
-- For a proper fixture with 2 teams, we only insert Thunder FC here.
-- In a real scenario another team would exist.

-- =============================================================================
-- 13. FIXTURE PARTICIPANTS
-- =============================================================================
INSERT INTO fixture_participant (fixture_id, team_id, score) VALUES
    (1, 1, 3),   -- Thunder FC played fixture 1
    (3, 2, 2),   -- Ace Smashers played fixture 3
    (4, 3, 65),  -- Dunking Bears played fixture 4
    (5, 5, 180); -- Royal Strikers played fixture 5

-- =============================================================================
-- 14. EQUIPMENT
-- =============================================================================
INSERT INTO equipment (name, sport_id, total_stock, current_stock) VALUES
    ('Football',           1, 20, 18),
    ('Football Gloves',    1, 10, 10),
    ('Tennis Racket',      2, 15, 12),
    ('Tennis Balls (box)', 2, 30, 25),
    ('Basketball',         3, 12, 12),
    ('Swimming Goggles',   4, 25, 22),
    ('Swim Cap',           4, 30, 28),
    ('Cricket Bat',        5, 10,  9),
    ('Cricket Pads',       5,  8,  7),
    ('Cricket Ball',       5, 20, 18);

-- =============================================================================
-- 15. EQUIPMENT ISSUES
-- =============================================================================
INSERT INTO equipment_issue (equipment_id, member_id, issue_date, expected_return_date, actual_return_date, quantity) VALUES
    (1,  1, '2026-07-01', '2026-07-08', '2026-07-07', 1),   -- Aarav borrowed Football, returned
    (3,  3, '2026-07-10', '2026-07-17', '2026-07-15', 2),   -- Priya borrowed Tennis Rackets, returned
    (1,  2, '2026-07-15', '2026-07-22', NULL,           1), -- Rohan borrowed Football, not returned
    (6,  5, '2026-07-20', '2026-07-27', NULL,           2), -- Ananya borrowed Goggles, not returned
    (8, 10, '2026-07-25', '2026-08-05', NULL,           1), -- Aditya borrowed Cricket Bat, not returned
    (4,  7, '2026-07-12', '2026-07-19', '2026-07-19', 5);  -- Neha borrowed Tennis Balls, returned
