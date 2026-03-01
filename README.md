## BlueHire – Job Portal for Blue-Collar Workers

BlueHire is a Flask-based web app that connects blue-collar workers with employers.  
It supports email/password and mobile OTP authentication, worker/employer/admin dashboards, job posting and search, basic notifications, and simple multilingual voice help (English/Hindi).

---

### 1. Features Overview

- **Authentication**
  - Email + password login/registration.
  - Mobile number OTP login flow (demo: OTP shown on screen instead of SMS).
  - Role-based dashboards: **worker**, **employer**, **admin**.

- **Workers**
  - Create/update **work profile** (skills, experience, preferred location).
  - Browse and **search jobs** by skill, category, and location.
  - Apply to jobs and track applications.

- **Employers**
  - Manage **company profile**.
  - **Post jobs** with category, city, skills, salary range.
  - View applications per job.

- **Admin**
  - Simple overview dashboard for counts of users, jobs, applications.

- **UX & Accessibility**
  - Mobile-first, responsive layout using **Bootstrap 5**.
  - **Material Icons** and card-based UI for low-literacy friendliness.
  - **Voice Help** via browser Speech Synthesis API (EN + HI).

- **Tech**
  - Flask 3, Flask-SQLAlchemy, Flask-Login.
  - SQLite database (`bluehire.db`).

---

### 2. Prerequisites

- **Python** 3.10+ (recommended).
- **pip** and **virtualenv** (or `python -m venv`).
- Git (optional, for pushing to GitHub).

---

### 3. Project Structure (High-Level)

```text
BlueHire/
  app.py                # Flask entrypoint using app factory
  requirements.txt      # Python dependencies
  bluehire/
    __init__.py         # create_app, db, login_manager, CLI commands
    models.py           # User, EmployerProfile, WorkerProfile, Job, Application, OTP
    auth/               # auth blueprint (login, register, OTP)
    main/               # main blueprint (home, search)
    employer/           # employer dashboard & job management
    worker/             # worker dashboard, profile, job actions
    admin/              # admin dashboard
    templates/          # Jinja2 templates (Bootstrap + Material UI)
    static/
      css/style.css     # light custom overrides on top of Bootstrap
      js/voice.js       # language + voice-help helper
```

---

### 4. Local Setup (End-to-End)

#### 4.1. Clone the repository

```bash
git clone https://github.com/ikshitiz/BlueHire.git
cd BlueHire
```

> If you are using SSH, adjust URL accordingly.

#### 4.2. Create & activate virtual environment

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

#### 4.3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4.4. Configure environment (optional)

By default, the app uses:

- `SECRET_KEY="change-this-secret-key"`
- `SQLALCHEMY_DATABASE_URI="sqlite:///bluehire.db"`

For local development this is fine.  
For production, override via environment variables or an `instance` config.

---

### 5. Running the App

You can run via **Flask CLI** or directly with Python.

#### Option A – Flask CLI (recommended)

From the project root:

```bash
export FLASK_APP=app.py        # macOS / Linux
# set FLASK_APP=app.py         # Windows PowerShell

flask run
```

Visit: `http://127.0.0.1:5000`

#### Option B – Direct Python

```bash
python app.py
```

This uses `debug=True` by default for development.

---

### 6. Database & Dummy Data

The app automatically creates tables on startup.  
To make the UI meaningful, you can load **dummy data** via a custom CLI command.

#### 6.1. Create / migrate DB

On first run, the SQLite DB (`bluehire.db`) will be created automatically when you start the app.

#### 6.2. Seed dummy data

With your virtual environment active:

```bash
export FLASK_APP=app.py
flask seed-db
```

What this does:

- Adds employers in **Bengaluru** and **Delhi** with profiles.
- Adds workers with blue-collar skills such as:
  - Electrician, Plumber, Driver, Carpenter, Welder, Mason,
  - Security Guard, Housekeeping, Delivery Boy, AC Technician.
- Uses Indian cities like **Bengaluru, Delhi, Mysuru, Mumbai, Chennai, Hyderabad, Pune, Kolkata, Jaipur, Ahmedabad** for worker preferences and job locations.
- Creates sample jobs like:
  - “Electrician - Residential Projects” (Bengaluru)
  - “Plumber - Apartment Maintenance” (Mysuru)
  - “Heavy Vehicle Driver” (Delhi)
  - “Delivery Boy - E-commerce” (Mumbai)
  - “Security Guard - Night Shift” (Hyderabad)

If data already exists, the command safely skips reseeding.

---

### 7. Using the App

#### 7.1. Roles & Dashboards

- **Worker**
  - Register with role “Worker”.
  - Fill your work profile (skills, experience, preferred location).
  - Use **Find Jobs** (or home page) to search and **Apply**.
  - See your applications on the **Worker Dashboard**.

- **Employer**
  - Register with role “Employer”.
  - Complete your **Company Profile**.
  - **Post Jobs** and later view **Applications** per job.

- **Admin**
  - Create an admin user manually via a Python shell if needed:

    ```bash
    python
    >>> from bluehire import create_app, db
    >>> from bluehire.models import User
    >>> app = create_app()
    >>> app.app_context().push()
    >>> admin = User(name="Admin", email="admin@bluehire.test", role="admin")
    >>> admin.set_password("admin123")
    >>> db.session.add(admin)
    >>> db.session.commit()
    ```

  - Login as admin and visit `/admin/dashboard`.

#### 7.2. OTP Login (Demo)

1. Go to **“Login with Mobile OTP”**.
2. Enter a phone number (matching an existing user’s phone for auto-login, or any number for demo).
3. The app generates an OTP and **displays it in a flash message** (in real deployment, you’d send SMS).
4. Enter the OTP on the next screen to log in.

---

### 8. Voice Help & Multilingual

- Buttons in the header let you toggle language: **EN / हिन्दी**.
- **Voice Help** button uses `speechSynthesis` in the browser to read a short help message in English or Hindi.
  - Implemented in `static/js/voice.js`.
  - No backend dependency; works purely on the client if the browser supports Web Speech API.

---

### 9. Development Tips

- To run tests or add new ones, you can add pytest/unittest as needed (not included by default).
- For real **email/SMS notifications**, replace `print` statements (e.g., when a worker applies to a job) with integration to a provider (Twilio, SendGrid, etc.).
- For production:
  - Use a stronger `SECRET_KEY`.
  - Consider PostgreSQL/MySQL instead of SQLite.
  - Run via a WSGI server (gunicorn/uwsgi) behind Nginx or similar.

---

### 10. License

This project is intended as a learning/demo project for a blue-collar job portal.  
Add your preferred license here (e.g. MIT) if you plan to open-source it.


