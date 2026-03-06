from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import os
from flask import current_app
from bluehire import db
from bluehire.models import EmployerProfile, Job, Application, WorkerProfile
from . import employer_bp
from bluehire.models import Tool, EmployerProfile
from flask import redirect, request
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def employer_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "employer":
            flash("Employer access only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


@employer_bp.route("/dashboard")
@login_required
@employer_required
def dashboard():
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    jobs = Job.query.filter_by(employer_id=profile.id).all() if profile else []
    return render_template("employer_dashboard.html", profile=profile, jobs=jobs)


@employer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@employer_required
def profile():
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        company_name = request.form.get("company_name")
        description = request.form.get("company_description")
        location = request.form.get("location")
        if not profile:
            profile = EmployerProfile(
                user_id=current_user.id,
                company_name=company_name or current_user.name,
                company_description=description,
                location=location,
            )
            db.session.add(profile)
        else:
            profile.company_name = company_name or profile.company_name
            profile.company_description = description
            profile.location = location
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("employer.dashboard"))
    return render_template("employer_profile.html", profile=profile)


@employer_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@employer_required
def create_job():
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Please complete your company profile first.", "warning")
        return redirect(url_for("employer.profile"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        location = request.form.get("location")
        skills_required = request.form.get("skills_required")
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None

        if not all([title, description, category, location]):
            flash("Please fill all required fields.", "danger")
            return render_template("employer_job_form.html")

        job = Job(
            title=title,
            description=description,
            category=category,
            location=location,
            skills_required=skills_required,
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            employer_id=profile.id,
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully.", "success")
        return redirect(url_for("employer.dashboard"))

    return render_template("employer_job_form.html")


@employer_bp.route("/jobs/<int:job_id>/applications")
@login_required
def view_applications(job_id):

    job = Job.query.get_or_404(job_id)

    applications = Application.query.filter_by(job_id=job.id).all()

    recommended_workers = recommend_workers(job)

    return render_template(
        "employer_applications.html",
        job=job,
        applications=applications,
        recommended_workers=recommended_workers
    )


@employer_bp.route("/tools/add", methods=["GET","POST"])
@login_required
def add_tool():

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]

        image = request.files.get("image")

        filename = None

        if image:
            filename = secure_filename(image.filename)

            image_path = os.path.join(
                current_app.root_path,
                "static",
                "tool_images",
                filename
            )

            image.save(image_path)

        tool = Tool(
            name=name,
            description=description,
            price_per_day=int(price),
            image=filename
        )

        db.session.add(tool)
        db.session.commit()

        return redirect(url_for("main.tools"))

    return render_template("add_tool.html")

@employer_bp.route("/applications/<int:app_id>/accept")
@login_required
def accept_worker(app_id):

    application = Application.query.get_or_404(app_id)

    application.status = "accepted"

    db.session.commit()

    flash("Worker accepted successfully.", "success")

    return redirect(request.referrer)

@employer_bp.route("/application/<int:app_id>/reject")
@login_required
def reject_worker(app_id):

    application = Application.query.get_or_404(app_id)

    application.status = "rejected"

    db.session.commit()

    flash("Worker rejected.", "danger")

    return redirect(request.referrer)

def recommend_workers(job):

    from bluehire.models import WorkerProfile

    workers = WorkerProfile.query.all()

    if not workers:
        return []

    worker_skills = [w.skills or "" for w in workers]

    texts = [job.skills_required] + worker_skills

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    ranked_workers = sorted(
        zip(workers, similarity),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_workers[:5]   # top 5 workers