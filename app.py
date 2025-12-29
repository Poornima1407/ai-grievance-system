from flask import Flask, render_template, request
import sqlite3
import pickle
import os

app = Flask(__name__)

# -------------------------
# Load ML Model & Vectorizer
# -------------------------
model = pickle.load(open("grievance_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# -------------------------
# Database Initialization
# -------------------------
def init_db():
    if os.path.exists("grievance.db"):
        os.remove("grievance.db")  # force fresh DB on start

    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_text TEXT,
            department TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

# -------------------------
# Hybrid Prediction Function
# -------------------------
def predict_department(text):
    text = text.lower()

    # Health Department
    if any(word in text for word in ["ambulance", "hospital", "doctor", "medical", "health"]):
        return "Health Department"

    # Public Safety Department
    if any(word in text for word in ["dog", "dogs", "noise", "theft", "robbery", "fight", "unsafe"]):
        return "Public Safety Department"

    # Transport Department
    if any(word in text for word in ["bus", "transport", "traffic", "signal", "parking"]):
        return "Transport Department"

    # Sanitation & Waste Management
    if any(word in text for word in ["garbage", "waste", "drainage", "sewer"]):
        return "Sanitation & Waste Management"

    # Electricity Department
    if any(word in text for word in ["street light", "power", "electricity", "wire"]):
        return "Electricity Department"

    # Water Supply Department
    if any(word in text for word in ["water", "pipeline", "leakage"]):
        return "Water Supply Department"

    # ML fallback
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# -------------------------
# Routes
# -------------------------

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    department = None

    if request.method == "POST":
        complaint_text = request.form["complaint"]
        department = predict_department(complaint_text)

        conn = sqlite3.connect("grievance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complaints (complaint_text, department, status) VALUES (?, ?, ?)",
            (complaint_text, department, "Submitted")
        )
        conn.commit()
        conn.close()

    return render_template("complaint.html", department=department)

@app.route("/admin")
def admin():
    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    conn.close()
    return render_template("admin.html", complaints=complaints)

@app.route("/status")
def status():
    conn = sqlite3.connect("grievance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    conn.close()
    return render_template("status.html", complaints=complaints)

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



