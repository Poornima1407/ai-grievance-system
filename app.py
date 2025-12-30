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
    conn = sqlite3.connect("grievance.db")
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

init_db()

# ===============================
# Department Prediction (FINAL)
# ===============================
def predict_department(text):
    text = text.lower()

    # Health Department
    if any(word in text for word in [
        "ambulance", "hospital", "doctor", "medical", "health", "emergency"
    ]):
        return "Health Department"

    # Public Safety
    if any(word in text for word in [
        "dog", "dogs", "street dog", "noise", "theft", "robbery",
        "fight", "unsafe", "crime"
    ]):
        return "Public Safety Department"

    # Transport
    if any(word in text for word in [
        "bus", "transport", "traffic", "signal", "parking", "road accident"
    ]):
        return "Transport Department"

    # Sanitation & Waste
    if any(word in text for word in [
        "garbage", "waste", "drainage", "sewer", "overflow", "cleaning"
    ]):
        return "Sanitation & Waste Management"

    # Electricity
    if any(word in text for word in [
        "street light", "power", "electricity", "wire", "current"
    ]):
        return "Electricity Department"

    # Water
    if any(word in text for word in [
        "water", "pipeline", "leakage", "water supply"
    ]):
        return "Water Supply Department"

    # ML fallback
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# ===============================
# Complaint Page
# ===============================
@app.route("/", methods=["GET", "POST"])
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    department = None

    if request.method == "POST":
        complaint_text = request.form.get("complaint", "").strip()
        area = request.form.get("area")
        city = request.form.get("city")
        pincode = request.form.get("pincode")

        department = predict_department(complaint_text)

        conn = sqlite3.connect("grievance.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints
            (complaint_text, department, area, city, pincode, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (complaint_text, department, area, city, pincode, "Submitted"))
        conn.commit()
        conn.close()

    return render_template("complaint.html", department=department)

# ===============================
# Admin Dashboard
# ===============================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    cursor.execute("""
        SELECT department, COUNT(*)
        FROM complaints
        GROUP BY department
    """)
    dept_counts = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        dept_counts=dept_counts
    )

# ===============================
# Run App (Render Compatible)
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))





