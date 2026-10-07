import os

replacements = {
    # Members
    "'Alice'": "'Aarav'", "'Johnson'": "'Sharma'", "'alice.johnson@email.com'": "'aarav.sharma@email.com'",
    "'Bob'": "'Rohan'", "'Smith'": "'Gupta'", "'bob.smith@email.com'": "'rohan.gupta@email.com'",
    "'Carol'": "'Priya'", "'Williams'": "'Patel'", "'carol.w@email.com'": "'priya.p@email.com'",
    "'David'": "'Rahul'", "'Brown'": "'Desai'", "'david.b@email.com'": "'rahul.d@email.com'",
    "'Eve'": "'Ananya'", "'Jones'": "'Singh'", "'eve.jones@email.com'": "'ananya.singh@email.com'",
    "'Frank'": "'Vikram'", "'Garcia'": "'Mehta'", "'frank.g@email.com'": "'vikram.m@email.com'",
    "'Grace'": "'Neha'", "'Martinez'": "'Verma'", "'grace.m@email.com'": "'neha.v@email.com'",
    "'Henry'": "'Siddharth'", "'Davis'": "'Reddy'", "'henry.d@email.com'": "'siddharth.r@email.com'",
    "'Iris'": "'Sneha'", "'Wilson'": "'Joshi'", "'iris.w@email.com'": "'sneha.j@email.com'",
    "'Jack'": "'Aditya'", "'Moore'": "'Kumar'", "'jack.m@email.com'": "'aditya.k@email.com'",
    "'Kate'": "'Kavya'", "'Taylor'": "'Iyer'", "'kate.t@email.com'": "'kavya.i@email.com'",
    "'Liam'": "'Karthik'", "'Anderson'": "'Nair'", "'liam.a@email.com'": "'karthik.n@email.com'",
    
    # Coaches
    "'Marco'": "'Arjun'", "'Rossi'": "'Kapoor'", "'marco.rossi@club.com'": "'arjun.kapoor@club.com'",
    "'Sarah'": "'Sunita'", "'Connor'": "'Rao'", "'sarah.c@club.com'": "'sunita.r@club.com'",
    "'James'": "'Rajesh'", "'Hooper'": "'Khanna'", "'james.h@club.com'": "'rajesh.k@club.com'",
    "'Priya'": "'Maya'", "'Nair'": "'Menon'", "'priya.n@club.com'": "'maya.m@club.com'",
    "'Thomas'": "'Sanjay'", "'Hughes'": "'Verma'", "'thomas.h@club.com'": "'sanjay.v@club.com'",
    
    # Comments & Text
    "-- Alice": "-- Aarav",
    "-- Bob": "-- Rohan",
    "-- Carol": "-- Priya",
    "-- David": "-- Rahul",
    "-- Eve": "-- Ananya",
    "-- Frank": "-- Vikram",
    "-- Grace": "-- Neha",
    "-- Henry": "-- Siddharth",
    "-- Iris": "-- Sneha",
    "-- Jack": "-- Aditya",
    "-- Kate": "-- Kavya",
    "-- Liam": "-- Karthik",
    
    "Coach Marco": "Coach Arjun",
    "Coach Sarah": "Coach Sunita",
    "Coach James": "Coach Rajesh",
    "Coach Priya": "Coach Maya",
    "Coach Thomas": "Coach Sanjay"
}

filepath = 'db/06_sample_data.sql'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

for k, v in replacements.items():
    content = content.replace(k, v)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
