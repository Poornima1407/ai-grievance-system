from flask import Flask, render_template, request
import pickle
import sqlite3
import os

app = Flask(__name__)

# Load model
model = pickle.load(open("grievance_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def predict_department(text):
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    department = None
    if request.method == "POST":
        complaint_text = request.form["complaint"]
        department = predict_department(complaint_text)

        # Save to database
        conn = sqlite3.connect("grievance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complaints (complaint_text, department, status) VALUES (?, ?, ?)",
            (complaint_text, department, "Submitted")
        )
        conn.commit()
        conn.close()

    return render_template("complaint.html", department=department)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


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
    dept_count = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        dept_count=dept_count
    )

