"""
init_db.py  –  MongoDB setup for the Department Portal
Run once (or anytime) to:
  1. Create indexes on all collections
  2. Seed sample data so every page shows real content
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

# ── Connect ────────────────────────────────────────────────────────────────────
client = MongoClient('mongodb://localhost:27017/')
db = client['department_db']
print("[OK] Connected to MongoDB → department_db")

# ── 1. Indexes ─────────────────────────────────────────────────────────────────
print("\n[•] Creating indexes …")

# Users
db.users.create_index([('email', ASCENDING)], unique=True, name='idx_users_email')
db.users.create_index([('role',  ASCENDING)], name='idx_users_role')
db.users.create_index([('status', ASCENDING)], name='idx_users_status')

# News
db.news.create_index([('date', DESCENDING)], name='idx_news_date')
db.news.create_index([('title', TEXT), ('content', TEXT)], name='idx_news_text')

# Notes
db.notes.create_index([('date', DESCENDING)], name='idx_notes_date')
db.notes.create_index([('title', TEXT), ('subject', TEXT)], name='idx_notes_text')
db.notes.create_index([('uploaded_by', ASCENDING)], name='idx_notes_uploader')

# Achievements
db.achievements.create_index([('date', DESCENDING)], name='idx_achievements_date')

# Settings
db.settings.create_index([('site_id', ASCENDING)], unique=True, name='idx_settings_siteid')

print("    indexes created.")

# ── 2. Seed helpers ─────────────────────────────────────────────────────────────
def seed_if_empty(collection_name, docs):
    col = db[collection_name]
    if col.count_documents({}) == 0:
        col.insert_many(docs)
        print(f"    seeded {len(docs)} doc(s) into '{collection_name}'")
    else:
        print(f"    '{collection_name}' already has data – skipped")

# ── 3. Seed Users ──────────────────────────────────────────────────────────────
print("\n[•] Seeding users …")

students = [
    {
        'name': 'Arun Kumar',       'email': 'arun@student.com',
        'password': generate_password_hash('Student@1234'),
        'role': 'student', 'roll_no': 'CS21001', 'department': 'Computer Science',
        'year': 'Third Year',  'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Priya Sharma',     'email': 'priya@student.com',
        'password': generate_password_hash('Student@1234'),
        'role': 'student', 'roll_no': 'CS21002', 'department': 'Computer Science',
        'year': 'Second Year', 'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Rahul Verma',      'email': 'rahul@student.com',
        'password': generate_password_hash('Student@1234'),
        'role': 'student', 'roll_no': 'CS22001', 'department': 'Computer Science',
        'year': 'First Year',  'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Sneha Nair',       'email': 'sneha@student.com',
        'password': generate_password_hash('Student@1234'),
        'role': 'student', 'roll_no': 'CS20001', 'department': 'Computer Science',
        'year': 'Fourth Year', 'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Karthik Raj',      'email': 'karthik@student.com',
        'password': generate_password_hash('Student@1234'),
        'role': 'student', 'roll_no': 'CS21003', 'department': 'Computer Science',
        'year': 'Third Year',  'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
]

faculty_members = [
    {
        'name': 'Dr. Meena Krishnan', 'email': 'meena@faculty.com',
        'password': generate_password_hash('Faculty@1234'),
        'role': 'faculty', 'roll_no': '', 'faculty_id': 'FAC001',
        'faculty_role': 'Associate Professor', 'department': 'Computer Science',
        'age': '45', 'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Prof. Suresh Babu',  'email': 'suresh@faculty.com',
        'password': generate_password_hash('Faculty@1234'),
        'role': 'faculty', 'roll_no': '', 'faculty_id': 'FAC002',
        'faculty_role': 'Professor',          'department': 'Computer Science',
        'age': '52', 'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
    {
        'name': 'Dr. Lakshmi Priya',  'email': 'lakshmi@faculty.com',
        'password': generate_password_hash('Faculty@1234'),
        'role': 'faculty', 'roll_no': '', 'faculty_id': 'FAC003',
        'faculty_role': 'Assistant Professor', 'department': 'Computer Science',
        'age': '38', 'photo': 'default_avatar.png',
        'approved': True, 'status': 'approved', 'created_at': datetime.utcnow()
    },
]

# Insert users carefully to avoid duplicate key errors
def insert_users_safe(users):
    inserted = 0
    for u in users:
        if not db.users.find_one({'email': u['email']}):
            db.users.insert_one(u)
            inserted += 1
    print(f"    inserted {inserted} user(s) (skipped existing)")

if db.users.count_documents({}) == 0:
    insert_users_safe(students + faculty_members)
else:
    print(f"    'users' already has {db.users.count_documents({})} doc(s) – checking for missing sample accounts …")
    insert_users_safe(students + faculty_members)

# ── 4. Seed News ───────────────────────────────────────────────────────────────
print("\n[•] Seeding news …")
seed_if_empty('news', [
    {
        'title':    'Semester Registration 2026 Now Open',
        'content':  'Registration for the upcoming semester is now open. Students are requested to log in and complete course selection before the deadline. Ensure all dues are cleared before registering.',
        'category': 'Admission',
        'image':    None,
        'date':     datetime.now().strftime('%b %d, %Y')
    },
    {
        'title':    'National Symposium on AI & Machine Learning',
        'content':  'The department is hosting a two-day national symposium on Artificial Intelligence and Machine Learning. Students and faculty are invited to submit research papers. Selected papers will be published in the department journal.',
        'category': 'Seminar',
        'image':    None,
        'date':     (datetime.now() - timedelta(days=3)).strftime('%b %d, %Y')
    },
    {
        'title':    'Placement Drive 2026 – Top Companies Visiting',
        'content':  'Over 25 top companies including TCS, Infosys, Wipro, Zoho, and several startups will be visiting the campus for the annual placement drive. Eligible students should register through the placement cell portal.',
        'category': 'Placement',
        'image':    None,
        'date':     (datetime.now() - timedelta(days=7)).strftime('%b %d, %Y')
    },
    {
        'title':    'CSE Department Wins Best Department Award',
        'content':  'The Department of Computer Science & Engineering has been awarded the "Best Department" distinction at the State University Tech Fest 2026. This recognizes our excellence in research output, student performance, and infrastructure.',
        'category': 'Achievement',
        'image':    None,
        'date':     (datetime.now() - timedelta(days=10)).strftime('%b %d, %Y')
    },
    {
        'title':    'New Lab Facilities Inaugurated',
        'content':  'A state-of-the-art AI & Deep Learning Lab has been inaugurated with 40 high-performance GPU workstations. The lab is open for final year project students and research scholars.',
        'category': 'Infrastructure',
        'image':    None,
        'date':     (datetime.now() - timedelta(days=14)).strftime('%b %d, %Y')
    },
])

# ── 5. Seed Notes ──────────────────────────────────────────────────────────────
print("\n[•] Seeding notes …")
seed_if_empty('notes', [
    {
        'title':        'Data Structures – Unit 1: Arrays & Linked Lists',
        'subject':      'CS201',
        'filename':     'ds_unit1_arrays_linkedlists.pdf',
        'uploaded_by':  'Dr. Meena Krishnan',
        'date':         (datetime.now() - timedelta(days=2)).strftime('%b %d, %Y')
    },
    {
        'title':        'Operating Systems – Process Management',
        'subject':      'CS301',
        'filename':     'os_process_management.pdf',
        'uploaded_by':  'Prof. Suresh Babu',
        'date':         (datetime.now() - timedelta(days=5)).strftime('%b %d, %Y')
    },
    {
        'title':        'Database Management – ER Diagrams & Normalization',
        'subject':      'CS302',
        'filename':     'dbms_er_normalization.pdf',
        'uploaded_by':  'Dr. Meena Krishnan',
        'date':         (datetime.now() - timedelta(days=8)).strftime('%b %d, %Y')
    },
    {
        'title':        'Machine Learning – Introduction & Linear Regression',
        'subject':      'CS401',
        'filename':     'ml_intro_linear_regression.pdf',
        'uploaded_by':  'Dr. Lakshmi Priya',
        'date':         (datetime.now() - timedelta(days=12)).strftime('%b %d, %Y')
    },
    {
        'title':        'Computer Networks – OSI Model & TCP/IP',
        'subject':      'CS303',
        'filename':     'networks_osi_tcp.pdf',
        'uploaded_by':  'Prof. Suresh Babu',
        'date':         (datetime.now() - timedelta(days=15)).strftime('%b %d, %Y')
    },
    {
        'title':        'Software Engineering – SDLC & Agile',
        'subject':      'CS304',
        'filename':     'se_sdlc_agile.pdf',
        'uploaded_by':  'Dr. Lakshmi Priya',
        'date':         (datetime.now() - timedelta(days=20)).strftime('%b %d, %Y')
    },
])

# ── 6. Seed Achievements ───────────────────────────────────────────────────────
print("\n[•] Seeding achievements …")
seed_if_empty('achievements', [
    {
        'title':       'First Place – National Hackathon 2025',
        'description': 'Team CodeStorm from our department secured first place at the National Hackathon 2025 hosted by IIT Bombay among 500+ teams. They built an AI-powered disaster response system.',
        'image':       None,
        'uploaded_by': 'Arun Kumar',
        'date':        (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    },
    {
        'title':       'Best Research Paper – IEEE Conference 2025',
        'description': 'Dr. Meena Krishnan published a research paper on Federated Learning that won the Best Paper Award at IEEE ICACCI 2025. The paper introduces a privacy-preserving framework for medical data.',
        'image':       None,
        'uploaded_by': 'Dr. Meena Krishnan',
        'date':        (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
    },
    {
        'title':       'Smart India Hackathon Finalist',
        'description': 'Team InnovatIIT from CSE department reached the finals of Smart India Hackathon 2025 with their project on automated crop disease detection using computer vision.',
        'image':       None,
        'uploaded_by': 'Priya Sharma',
        'date':        (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    },
    {
        'title':       'Google Summer of Code 2025 Selection',
        'description': 'Rahul Verma (CS22001) has been selected for Google Summer of Code 2025 to contribute to the TensorFlow open-source project. He is one of only 3 students from Tamil Nadu selected this year.',
        'image':       None,
        'uploaded_by': 'Rahul Verma',
        'date':        (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    },
    {
        'title':       'ACM ICPC Asia Regionals Qualifier',
        'description': 'Three teams from our department qualified for the ACM ICPC Asia Regionals 2025. This is a record for the department with the most qualifiers in a single year.',
        'image':       None,
        'uploaded_by': 'Karthik Raj',
        'date':        (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
    },
])

# ── 7. Summary ─────────────────────────────────────────────────────────────────
print("\n" + "─"*50)
print("[✓] Database initialisation complete!")
print("─"*50)
for col in ['users', 'news', 'notes', 'achievements', 'settings']:
    count = db[col].count_documents({})
    print(f"  {col:15s} → {count} document(s)")
print("─"*50)
print("\nSample Login Credentials:")
print("  Admin   → admin@dept.com    / Admin@1234")
print("  Student → arun@student.com  / Student@1234")
print("  Faculty → meena@faculty.com / Faculty@1234")
