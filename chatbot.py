import re
from difflib import SequenceMatcher

STOP_WORDS = {
    "what", "is", "the", "a", "an", "how", "can", "i", "where", "when",
    "do", "does", "my", "me", "please", "tell", "about", "for", "of",
    "to", "in", "on", "are", "your", "college", "rise"
}

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(words)

def find_answer(db, question):
    rows = db.execute("""
        SELECT f.id, f.question, f.answer, f.verified_status, c.name AS category
        FROM faqs f JOIN categories c ON c.id=f.category_id
    """).fetchall()
    q = normalize(question)
    best = None
    best_score = 0.0
    for row in rows:
        candidate = normalize(row["question"])
        score = SequenceMatcher(None, q, candidate).ratio()
        q_words = set(q.split())
        c_words = set(candidate.split())
        if q_words and c_words:
            overlap = len(q_words & c_words) / max(len(q_words), 1)
            score = max(score, overlap * 0.92)
        if score > best_score:
            best, best_score = row, score

    if best and best_score >= 0.42:
        return {
            "answer": best["answer"],
            "matched": True,
            "faq_id": best["id"],
            "category": best["category"],
            "verified_status": best["verified_status"],
            "confidence": round(best_score, 2),
            "notice": "Sample information – confirm with the college." if best["verified_status"] != "verified" else None
        }
    return {
        "answer": "I couldn't find a reliable answer in the current college FAQ database. Please contact your department office or college administration.",
        "matched": False,
        "faq_id": None,
        "category": None,
        "verified_status": None,
        "confidence": round(best_score, 2)
    }
