import os
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "rise_faq.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        verified_status TEXT NOT NULL DEFAULT 'sample',
        FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        response TEXT NOT NULL,
        matched_faq_id INTEGER,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(matched_faq_id) REFERENCES faqs(id)
    );
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)
    categories = [
        "Admissions", "Counselling Admissions", "Management Admissions",
        "Fees & Payments", "Attendance", "Examinations", "Academics & Syllabus",
        "Departments", "Assignments & Labs", "Placements", "Scholarships",
        "Facilities", "Transport", "General Information"
    ]
    for name in categories:
        db.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))

    count = db.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
    if count == 0:
        category_ids = {r["name"]: r["id"] for r in db.execute("SELECT id,name FROM categories")}
        samples = [
            ("Admissions", "How can I apply for admission?", "Admissions are handled according to the institution's current eligibility criteria and admission procedure. Please contact the college admissions office for the latest application steps.", "sample"),
            ("Counselling Admissions", "What is the counselling quota fee?", "Counselling-quota fees depend on the current approved fee structure and course. Please confirm the exact amount with the college admissions office. This demo database does not contain verified fee figures.", "sample"),
            ("Management Admissions", "What is the management quota fee?", "Management-quota fees may vary by course and admission year. Contact the college admissions office for the current approved amount. This demo database does not contain verified fee figures.", "sample"),
            ("Fees & Payments", "How can I pay my college fee?", "Please use the payment method officially communicated by the college accounts office. Confirm the current payment link, due date and receipt procedure with the accounts office.", "sample"),
            ("Attendance", "What is the minimum attendance requirement?", "Attendance requirements depend on the applicable university and institution regulations. Please check the current academic regulations or contact your department office.", "sample"),
            ("Examinations", "Where can I find the examination timetable?", "Please check the latest official examination-cell notice or academic portal. Timetables can change, so use the latest notice issued by the college.", "sample"),
            ("Academics & Syllabus", "Where can I get the syllabus?", "Please contact your department office or check the official academic resources shared by your college for the latest syllabus.", "sample"),
            ("Departments", "Which departments are available in the college?", "This chatbot is configured for all departments. Please refer to the institution's current official website or administration for the confirmed list of departments.", "sample"),
            ("Assignments & Labs", "When should I submit my assignment?", "Assignment deadlines are set by the subject faculty. Please check the instructions shared by your faculty or department.", "sample"),
            ("Placements", "How can I get placement information?", "For placement eligibility, training schedules and company updates, contact the placement and training cell.", "sample"),
            ("Scholarships", "How can I apply for a scholarship?", "Scholarship eligibility and application dates depend on the applicable government or institutional scheme. Contact the scholarship section for current details.", "sample"),
            ("Facilities", "How can I access the library?", "Please contact the library staff for membership, borrowing rules and current operating hours.", "sample"),
            ("Transport", "How can I get college bus information?", "For bus routes, availability and transport fees, contact the college transport office.", "sample"),
            ("General Information", "What are the college working hours?", "Please confirm the current working hours with the college administration, as schedules may vary by department and academic calendar.", "sample"),
        ]
        for category, question, answer, status in samples:
            db.execute(
                "INSERT INTO faqs(category_id,question,answer,verified_status) VALUES(?,?,?,?)",
                (category_ids[category], question, answer, status)
            )

    # Local demo administrator. Change credentials before any public deployment.
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@rise.local")
    admin_password = os.environ.get("ADMIN_PASSWORD", "ChangeThisAdmin123!")
    existing = db.execute("SELECT id FROM admins WHERE email=?", (admin_email,)).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO admins(email,password_hash) VALUES(?,?)",
            (admin_email, generate_password_hash(admin_password))
        )
    db.commit()
    db.close()
