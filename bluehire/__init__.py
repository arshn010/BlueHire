from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "change-this-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bluehire.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from bluehire.auth.routes import auth_bp
    from bluehire.main import main_bp
    from bluehire.employer.routes import employer_bp
    from bluehire.worker.routes import worker_bp
    from bluehire.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(employer_bp, url_prefix="/employer")
    app.register_blueprint(worker_bp, url_prefix="/worker")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        from bluehire import models  # noqa: F401
        db.create_all()

    register_cli_commands(app)

    return app


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("seed-db")
    def seed_db_command():
        """Insert dummy data for development."""
        from bluehire.models import User, EmployerProfile, WorkerProfile, Job

        cities = [
            "Bengaluru",
            "Delhi",
            "Mysuru",
            "Mumbai",
            "Chennai",
            "Hyderabad",
            "Pune",
            "Kolkata",
            "Jaipur",
            "Ahmedabad",
        ]

        skills_sets = [
            "Electrician, Wiring, Maintenance",
            "Plumber, Pipe Fitting, Sanitation",
            "Driver, Heavy Vehicle, License",
            "Carpenter, Furniture Making, Fitting",
            "Welder, Fabrication, Cutting",
            "Mason, Construction, Brick Work",
            "Security Guard, Night Shift, Patrol",
            "Housekeeping, Cleaning, Maintenance",
            "Delivery Boy, Two Wheeler, Navigation",
            "AC Technician, Cooling Systems, Repair",
        ]

        # Only seed if no jobs exist yet
        if Job.query.first():
            print("Database already has data, skipping seed.")
            return

        # Create two employers
        emp1 = User(name="Metro Constructions", email="metro@bluehire.test", phone="9000000001", role="employer")
        emp1.set_password("password123")
        emp2 = User(name="City Logistics", email="logistics@bluehire.test", phone="9000000002", role="employer")
        emp2.set_password("password123")

        db.session.add_all([emp1, emp2])
        db.session.commit()

        eprof1 = EmployerProfile(user_id=emp1.id, company_name="Metro Constructions",
                                 company_description="Infra and building works across India.",
                                 location="Bengaluru")
        eprof2 = EmployerProfile(user_id=emp2.id, company_name="City Logistics",
                                 company_description="Last mile delivery services.",
                                 location="Delhi")
        db.session.add_all([eprof1, eprof2])

        # Create a few workers
        worker_users = []
        for i, skill in enumerate(skills_sets[:5], start=1):
            u = User(
                name=f"Worker {i}",
                email=f"worker{i}@bluehire.test",
                phone=f"910000000{i}",
                role="worker",
            )
            u.set_password("password123")
            db.session.add(u)
            worker_users.append((u, skill))
        db.session.commit()

        for (u, skill), city in zip(worker_users, cities):
            wprof = WorkerProfile(
                user_id=u.id,
                skills=skill,
                experience_years=2,
                preferred_location=city,
            )
            db.session.add(wprof)

        # Create sample jobs
        sample_jobs = [
            ("Electrician - Residential Projects", eprof1, skills_sets[0], "Bengaluru"),
            ("Plumber - Apartment Maintenance", eprof1, skills_sets[1], "Mysuru"),
            ("Heavy Vehicle Driver", eprof2, skills_sets[2], "Delhi"),
            ("Delivery Boy - E-commerce", eprof2, skills_sets[8], "Mumbai"),
            ("Security Guard - Night Shift", eprof2, skills_sets[6], "Hyderabad"),
        ]

        for title, employer_profile, skill, city in sample_jobs:
            job = Job(
                title=title,
                description="Good salary, overtime benefits, and PF/ESI as per company norms.",
                category=skill.split(",")[0],
                location=city,
                skills_required=skill,
                salary_min=15000,
                salary_max=25000,
                employer_id=employer_profile.id,
            )
            db.session.add(job)

        db.session.commit()
        print("Dummy data inserted successfully.")

