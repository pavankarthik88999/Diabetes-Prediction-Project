# 🩺 Diabetes Prediction System

A Flask web application that predicts a patient's risk of diabetes from eight standard
medical measurements using a trained machine learning model (a neural network / MLP).
It features user authentication, an interactive visual risk report, and a
passcode-protected prediction history — all backed by a **Neon PostgreSQL** database.

---

## ✨ Features

- **User accounts** — register, log in, and log out (passwords are securely hashed).
- **ML predictions** — enter 8 medical metrics and get an instant diabetes risk assessment.
- **Visual report** — risk-probability gauge, patient-vs-healthy comparison chart, and a value summary (powered by Chart.js).
- **Prediction history** — every prediction is stored in the database and viewable behind a passcode.
- **Cloud database** — user and prediction data is persisted in Neon PostgreSQL.

---

## 🗺️ User Flow

```
Home  →  Register / Login  →  New Prediction  →  Visual Report
                                     │
                                     └──►  View Predictions (passcode required)  →  Logout
```

---

## 🧰 Tech Stack

| Layer      | Technology                                   |
|------------|----------------------------------------------|
| Backend    | Python, Flask                                |
| ML         | scikit-learn (MLPClassifier), NumPy          |
| Database   | Neon PostgreSQL (via `psycopg` 3)            |
| Frontend   | HTML, CSS, Jinja2 templates, Chart.js        |
| Auth       | Werkzeug password hashing, Flask sessions    |

---

## 📁 Project Structure

```
Diabetes-Prediction-Project/
├── app.py                  # Flask app: routes, auth, prediction, history
├── db.py                   # Neon PostgreSQL connection + table creation
├── model.pkl               # Trained ML model (MLPClassifier)
├── scaler.pkl              # Fitted StandardScaler
├── diabetes.csv            # Dataset used for training
├── requirements.txt        # Python dependencies
├── .env                    # Secrets (NOT committed) — you create this
├── .gitignore
├── Predict Diabets With Machine Learning.ipynb   # Model training notebook
├── templates/
│   ├── base.html           # Shared layout, navbar, styles
│   ├── home.html           # Landing page
│   ├── register.html       # Sign-up page
│   ├── login.html          # Login page
│   ├── index.html          # Prediction form
│   ├── result.html         # Visual prediction report
│   ├── passcode.html       # Passcode gate for history
│   └── predictions.html    # Prediction history + charts
└── .github/workflows/
    └── deploy.yml          # GitHub Actions boot-check workflow
```

---

## ✅ Prerequisites

- **Python 3.12+** installed ([python.org](https://www.python.org/downloads/))
- A **Neon** account and database ([neon.tech](https://neon.tech)) — free tier is fine
- **Git** (to clone the repository)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pavankarthik88999/Diabetes-Prediction-Project.git
cd Diabetes-Prediction-Project
```

### 2. Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a file named **`.env`** in the project root with the following content:

```dotenv
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
SECRET_KEY=your-long-random-secret-string
PREDICTIONS_PASSCODE=7768
```

- **`DATABASE_URL`** — copy your connection string from the Neon dashboard.
- **`SECRET_KEY`** — any long random string. Generate one with:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **`PREDICTIONS_PASSCODE`** — the passcode required to view prediction history (default `7768`).

> ⚠️ **Never commit `.env`.** It is already listed in `.gitignore`.

### 5. Run the application

```bash
python app.py
```

The database tables (`users` and `predictions`) are created automatically on first run.

Open your browser at **http://127.0.0.1:5000**

---

## 📖 How to Use

1. **Register** a new account from the home page.
2. **Log in** with your username and password.
3. On the **New Prediction** page, enter the 8 medical values:
   Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI,
   Diabetes Pedigree Function, and Age.
4. Click **Run Prediction** to see the **visual report** (risk gauge + charts).
5. Click **View Predictions** in the navbar and enter the **passcode** (`7768`)
   to see the full history of all predictions.
6. **Logout** when finished.

---

## 🤖 The Machine Learning Model

- Trained on the **Pima Indians Diabetes** dataset (`diabetes.csv`, 768 records).
- Zero values in medical columns are replaced with the column mean/median.
- Features are standardized with `StandardScaler`, then classified with an
  `MLPClassifier` (neural network).
- The training process lives in **`Predict Diabets With Machine Learning.ipynb`**,
  which exports `model.pkl` and `scaler.pkl` used by the app.

> **Disclaimer:** This tool is for educational and screening-support purposes only.
> It does **not** provide a medical diagnosis. Always consult a qualified healthcare professional.

---

## ☁️ Deployment

GitHub itself cannot host a live Flask server (Pages is static-only and Actions
runners are temporary). To deploy publicly, use a platform such as **Render**,
**Railway**, or **PythonAnywhere**:

1. Add `gunicorn` to `requirements.txt`.
2. Set the start command to `gunicorn app:app`.
3. Add `DATABASE_URL`, `SECRET_KEY`, and `PREDICTIONS_PASSCODE` as environment
   variables in the host's dashboard.
4. Set `debug=False` in `app.py` for production.

Your Neon database is already cloud-hosted, so it works with any of these hosts.

---

## 🔒 Security Notes

- Passwords are hashed with Werkzeug before storage — plain passwords are never saved.
- Secrets live only in `.env` (git-ignored) and are read via environment variables.
- If a database credential is ever exposed, **rotate it** in the Neon dashboard.
