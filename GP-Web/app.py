from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "3b1f9a4d0e6243c6ac91e41a6b1ec23f"
DB_NAME = "database.db"

# =========================
# INIT DB IF NOT EXISTS
# =========================
def init_db():
    if not os.path.exists(DB_NAME):
        with open("schema.sql") as f:
            sql = f.read()
        with sqlite3.connect(DB_NAME) as conn:
            conn.executescript(sql)
            conn.commit()
        print("Database initialized.")

# =========================
# DB CONNECTION
# =========================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip()


    if not name or not email or not password or not role:
        return {"error": "All fields are required"}, 400

    hashed_password = generate_password_hash(password)

    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, role)
            )
            conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        return {"error": "Email already registered"}, 400
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")
@app.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json(force=True)  # force=True ensures JSON is parsed even if headers are weird
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            return {"message": "Login successful"}, 200
        else:
            return {"error": "Invalid email or password"}, 401

    except Exception as e:
        print("[LOGIN ERROR]", e)
        return {"error": "Internal server error"}, 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        doctor = request.form.get("doctor", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        message = request.form.get("message", "").strip()

        save_appointment(name, email, phone, doctor, date, time, message)
        send_email_confirmation(name, email, doctor, date, time)

        flash("Appointment saved. Confirmation email sent.", "success")
        return redirect(url_for("appointments"))

    # Dynamically load doctors from DB
    with get_db_connection() as conn:
        doctors = conn.execute("SELECT name FROM users WHERE role = 'doctor'").fetchall()

    return render_template("appointments.html", doctors=doctors)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    with get_db_connection() as conn:
        role = session["role"]
        name = session["name"]
        print(f"[DASHBOARD] Viewing as: {name} ({role})")

        if role == "patient":
            appointments = conn.execute("SELECT * FROM appointments WHERE patient_name = ?", (name,)).fetchall()
            return render_template("dashboard.html", appointments=appointments, role=role)
        elif role == "doctor":
            doctor_name = f"Dr. {name}"
            appointments = conn.execute("SELECT * FROM appointments WHERE doctor = ?", (doctor_name,)).fetchall()
            return render_template("doctor_dashboard.html", appointments=appointments)

@app.route("/add_note/<int:appointment_id>", methods=["POST"])
def add_note(appointment_id):
    if "user_id" not in session or session["role"] != "doctor":
        return redirect(url_for("login"))

    note = request.form.get("note", "").strip()
    with get_db_connection() as conn:
        conn.execute("UPDATE appointments SET note = ? WHERE id = ?", (note, appointment_id))
        conn.commit()

    flash("Note added successfully.", "success")
    return redirect(url_for("dashboard"))

# =========================
# SAVE APPOINTMENT
# =========================
def save_appointment(name, email, phone, doctor, date, time, message):
    try:
        with sqlite3.connect(DB_NAME, timeout=10) as conn:
            cursor = conn.cursor()
            doctor_full = f"Dr. {doctor}"  # Prefix before saving
            cursor.execute("""
                INSERT INTO appointments (patient_name, email, phone, doctor, appointment_date, appointment_time, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, doctor_full, date, time, message))
            conn.commit()
            print("Appointment saved.")
    except sqlite3.Error as e:
        print("Database Error:", e)


# =========================
# SEND EMAIL CONFIRMATION
# =========================
def send_email_confirmation(name, recipient_email, doctor, date, time):
    sender_email = "gpsurgery25@gmail.com"
    sender_password = "dqjvxlqgtwzfkebk"  # App password

    subject = "Appointment Confirmation – The GP Clinic"
    body = f"""
Dear {name},

This is a confirmation email for your appointment at The GP Clinic.

Date: {date}
Time: {time}
Doctor: {doctor}

If you have any questions or need to make changes, please contact us at +447402273372.

Thank you,  
The GP Clinic Team
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Confirmation email sent.")
    except Exception as e:
        print("Error sending email:", e)

@app.route("/edit_appointment/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if "user_id" not in session or session["role"] != "patient":
        return redirect(url_for("login"))

    conn = get_db_connection()
    appointment = conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()

    if request.method == "POST":
        new_date = request.form.get("date")
        new_time = request.form.get("time")
        new_message = request.form.get("message")

        conn.execute("""
            UPDATE appointments SET appointment_date = ?, appointment_time = ?, message = ?
            WHERE id = ?
        """, (new_date, new_time, new_message, appointment_id))
        conn.commit()
        conn.close()
        flash("Appointment updated successfully.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit_appointment.html", appointment=appointment)

@app.route("/cancel_appointment/<int:appointment_id>")
def cancel_appointment(appointment_id):
    if "user_id" not in session or session["role"] != "patient":
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    flash("Appointment cancelled.", "info")
    return redirect(url_for("dashboard"))

@app.route("/edit_cancel_menu")
def edit_cancel_menu():
    if "user_id" not in session or session["role"] != "patient":
        return redirect(url_for("login"))

    conn = get_db_connection()
    name = session["name"]
    appointments = conn.execute("SELECT * FROM appointments WHERE patient_name = ?", (name,)).fetchall()
    conn.close()
    return render_template("edit_cancel_menu.html", appointments=appointments)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
