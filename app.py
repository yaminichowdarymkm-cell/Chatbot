import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import init_db, get_db
from chatbot import find_answer

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-local-development-secret")
app.config["JSON_SORT_KEYS"] = False

init_db()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/categories")
def categories():
    db = get_db()
    rows = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/faqs")
def faqs():
    db = get_db()
    rows = db.execute("""
        SELECT f.id, f.question, f.answer, f.verified_status, c.name AS category
        FROM faqs f JOIN categories c ON c.id=f.category_id
        ORDER BY c.name, f.id
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"answer": "Please type a question so I can help.", "matched": False}), 400
    db = get_db()
    result = find_answer(db, question)
    db.execute(
        "INSERT INTO chat_history (question, response, matched_faq_id) VALUES (?, ?, ?)",
        (question, result["answer"], result.get("faq_id"))
    )
    db.commit()
    return jsonify(result)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE email=?", (email,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session["is_admin"] = True
            session["admin_email"] = email
            return redirect(url_for("admin_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin.html")

@app.route("/api/admin/faqs", methods=["GET", "POST"])
@admin_required
def admin_faqs():
    db = get_db()
    if request.method == "GET":
        rows = db.execute("""
            SELECT f.id, f.question, f.answer, f.verified_status, f.category_id,
                   c.name AS category
            FROM faqs f JOIN categories c ON c.id=f.category_id
            ORDER BY f.id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows])
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    answer = (data.get("answer") or "").strip()
    category_id = data.get("category_id")
    status = data.get("verified_status", "sample")
    if not question or not answer or not category_id:
        return jsonify({"error": "Question, answer and category are required."}), 400
    if status not in ("sample", "verified"):
        status = "sample"
    db.execute(
        "INSERT INTO faqs (category_id, question, answer, verified_status) VALUES (?, ?, ?, ?)",
        (category_id, question, answer, status)
    )
    db.commit()
    return jsonify({"success": True})

@app.route("/api/admin/faqs/<int:faq_id>", methods=["PUT", "DELETE"])
@admin_required
def edit_faq(faq_id):
    db = get_db()
    if request.method == "DELETE":
        db.execute("DELETE FROM faqs WHERE id=?", (faq_id,))
        db.commit()
        return jsonify({"success": True})
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    answer = (data.get("answer") or "").strip()
    category_id = data.get("category_id")
    status = data.get("verified_status", "sample")
    if not question or not answer or not category_id:
        return jsonify({"error": "Question, answer and category are required."}), 400
    db.execute("""
        UPDATE faqs SET question=?, answer=?, category_id=?, verified_status=?
        WHERE id=?
    """, (question, answer, category_id, status, faq_id))
    db.commit()
    return jsonify({"success": True})

@app.route("/api/admin/stats")
@admin_required
def admin_stats():
    db = get_db()
    return jsonify({
        "faqs": db.execute("SELECT COUNT(*) FROM faqs").fetchone()[0],
        "verified": db.execute("SELECT COUNT(*) FROM faqs WHERE verified_status='verified'").fetchone()[0],
        "chats": db.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
    })

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
