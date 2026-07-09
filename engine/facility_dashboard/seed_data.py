import sqlite3
import os
from datetime import datetime, timedelta
import random

DB = os.path.join(os.path.dirname(__file__), 'dashboard.db')

# Device codes only — never resident names on the dashboard (HIPAA posture).
patients = [
    'NURA-0419',
    'NURA-0307',
    'NURA-0288',
    'NURA-0512',
    'NURA-0455',
    'NURA-0376',
    'NURA-0201',
    'NURA-0193',
]

concerns = ['green', 'green', 'green', 'yellow', 'orange', 'red']

conn = sqlite3.connect(DB)
c = conn.cursor()

for patient in patients:
    concern = random.choice(concerns)
    
    if concern == 'red':
        sentiment = random.randint(3, 5)
        isolation = random.randint(1, 3)
        late_night = 1
    elif concern == 'orange':
        sentiment = random.randint(2, 3)
        isolation = random.randint(0, 1)
        late_night = random.randint(0, 1)
    elif concern == 'yellow':
        sentiment = random.randint(1, 2)
        isolation = random.randint(0, 1)
        late_night = random.randint(0, 1)
    else:
        sentiment = 0
        isolation = 0
        late_night = 0

    c.execute('''
        INSERT INTO observations
        (patient_id, date, concern_level, sentiment_score,
         isolation_score, late_night, message_length, received_at)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (
        patient,
        datetime.now().strftime('%Y-%m-%d'),
        concern,
        sentiment,
        isolation,
        late_night,
        random.randint(50, 400),
        datetime.now().isoformat()
    ))

conn.commit()
conn.close()
print('Seed data inserted for', len(patients), 'patients.')
