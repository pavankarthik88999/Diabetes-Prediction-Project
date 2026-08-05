"""Diabetes Prediction web app with user auth and prediction history (Neon DB)."""
import os
import pickle
from functools import wraps

import numpy as np
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from db import get_connection, init_db

load_dotenv()

# 1. Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
PREDICTIONS_PASSCODE = os.environ.get("PREDICTIONS_PASSCODE", "7768")

# 2. Load the pickled model and scaler
with open("model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

# 3. Ensure the database tables exist
init_db()

# Ordered form fields -> matches the training column order
FEATURE_FIELDS = [
    "pregnancies",
    "glucose",
    "bloodPressure",
    "skinThickness",
    "insulin",
    "bmi",
    "dpf",
    "age",
]


def login_required(view):
    """Redirect anonymous users to the login page."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not name or not username or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    flash("That username is already taken.", "error")
                    return render_template("register.html")
                cur.execute(
                    "INSERT INTO users (name, username, password_hash) "
                    "VALUES (%s, %s, %s)",
                    (name, username, password_hash),
                )
            conn.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            flash(f"Welcome, {user['name']}!", "success")
            return redirect(url_for("predict"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Protected pages
# ---------------------------------------------------------------------------
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "POST":
        try:
            values = [float(request.form[field]) for field in FEATURE_FIELDS]
            features_array = np.array([values])
            scaled_features = scaler.transform(features_array)
            prediction = int(model.predict(scaled_features)[0])

            # Probability of the positive (high-risk) class, as a percentage
            if hasattr(model, "predict_proba"):
                probability = float(model.predict_proba(scaled_features)[0][1]) * 100
            else:
                probability = 100.0 if prediction == 1 else 0.0

            if prediction == 1:
                result_text = "The model predicts: High Risk of Diabetes"
            else:
                result_text = "The model predicts: Low Risk of Diabetes"

            # Store the prediction once and get its id (Post/Redirect/Get)
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO predictions (
                            user_id, pregnancies, glucose, blood_pressure,
                            skin_thickness, insulin, bmi, dpf, age,
                            prediction, result_text, probability
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            session["user_id"], *values,
                            prediction, result_text, probability,
                        ),
                    )
                    new_id = cur.fetchone()[0]
                conn.commit()

            # Redirect so a browser refresh cannot resubmit the form
            return redirect(url_for("result", prediction_id=new_id))

        except (ValueError, KeyError):
            flash("Please make sure all inputs are valid numbers.", "error")

    return render_template("index.html")


@app.route("/result/<int:prediction_id>")
@login_required
def result(prediction_id):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM predictions WHERE id = %s AND user_id = %s",
                (prediction_id, session["user_id"]),
            )
            record = cur.fetchone()

    if record is None:
        flash("Prediction not found.", "error")
        return redirect(url_for("predict"))

    return render_template("result.html", r=record)


@app.route("/predictions", methods=["GET", "POST"])
@login_required
def predictions():
    # Gate the history behind the shared passcode
    if not session.get("passcode_ok"):
        if request.method == "POST":
            if request.form.get("passcode", "") == PREDICTIONS_PASSCODE:
                session["passcode_ok"] = True
            else:
                flash("Incorrect passcode.", "error")
                return render_template("passcode.html")
        else:
            return render_template("passcode.html")

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT p.*, u.name AS user_name, u.username
                FROM predictions p
                JOIN users u ON u.id = p.user_id
                ORDER BY p.created_at DESC
                """
            )
            rows = cur.fetchall()

    return render_template("predictions.html", rows=rows)


# 5. Run the application
if __name__ == "__main__":
    app.run(debug=True)