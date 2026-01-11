from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pickle
import os

app = Flask(__name__)

# ===============================
# Load ML model & vectorizer
# ===============================
model = pickle.load(open("grievance_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ===============================
# Initialize Database
# ===============================
def init_db():
    db_path = os.path.join(os.getcwd(), "grievance.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_text TEXT,
            department TEXT,
            area TEXT,
            city TEXT,
            pincode TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ===============================
# Department Prediction
# ===============================
def predict_department(text):
    text = text.lower()

    if any(word in text for word in [
        "ambulance", "hospital", "doctor", "medical", "health", "emergency"
    ]):
        return "Health Department"

    if any(word in text for word in [
        "dog", "dogs", "street dog", "noise", "theft", "robbery",
        "fight", "unsafe", "crime", "pothole", "patholes"
    ]):
        return "Public Safety Department"

    if any(word in text for word in [
        "bus", "transport", "traffic", "signal", "parking", "road accident"
    ]):
        return "Transport Department"

    if any(word in text for word in [
        "garbage", "waste", "drainage", "sewer", "overflow", "cleaning","Mosquito","stagnant water"
    ]):
        return "Sanitation & Waste Management"

    if any(word in text for word in [
        "street light", "power", "electricity", "wire", "current",
    ]):
        return "Electricity Department"

    if any(word in text for word in [
        "water", "pipeline", "leakage", "water supply"
    ]):
        return "Water Supply Department"

    # ML fallback
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# ===============================
# HOME → LOGIN
# ===============================
@app.route("/")
def home():
    return redirect(url_for("login"))

# ===============================
# LOGIN PAGE
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("complaint"))
    return render_template("login.html")

# ===============================
# COMPLAINT PAGE
# ===============================
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    department = None

    if request.method == "POST":
    try:
        complaint_text = request.form.get("complaint")
        area = request.form.get("area")
        city = request.form.get("city")
        pincode = request.form.get("pincode")

        department = predict_department(complaint_text)

        db_path = os.path.join(os.getcwd(), "grievance.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO complaints
            (complaint_text, department, area, city, pincode, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (complaint_text, department, area, city, pincode, "Submitted"))

        conn.commit()
        conn.close()

    except Exception as e:
        print("ERROR:", e)
        department = "Error saving complaint"


# ===============================
# ADMIN DASHBOARD
# ===============================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()

    # All complaints
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    # Department-wise count
    cursor.execute("""
        SELECT department, COUNT(*)
        FROM complaints
        GROUP BY department
    """)
    dept_counts = cursor.fetchall()

    # Total complaints
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        dept_counts=dept_counts,
        total_complaints=total_complaints
    )

@app.route("/status")
def status():
    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT complaint_text, department, area, city, pincode, status
        FROM complaints
        ORDER BY id DESC
    """)
    complaints = cursor.fetchall()
    conn.close()

    return render_template("status.html", complaints=complaints)


# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




