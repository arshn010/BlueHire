from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from bluehire import db
from bluehire.models import WorkerProfile, Job, Application
from . import worker_bp


def worker_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "worker":
            flash("Worker access only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


@worker_bp.route("/dashboard")
@login_required
@worker_required
def dashboard():
    profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()
    applications = []
    if profile:
        applications = Application.query.filter_by(worker_id=profile.id).all()
    return render_template("worker_dashboard.html", profile=profile, applications=applications)


@worker_bp.route("/profile", methods=["GET", "POST"])
@login_required
@worker_required
def profile():
    profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        skills = request.form.get("skills")
        experience_years = request.form.get("experience_years") or 0
        preferred_location = request.form.get("preferred_location")

        if not profile:
            profile = WorkerProfile(
                user_id=current_user.id,
                skills=skills,
                experience_years=int(experience_years),
                preferred_location=preferred_location,
            )
            db.session.add(profile)
        else:
            profile.skills = skills
            profile.experience_years = int(experience_years)
            profile.preferred_location = preferred_location
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("worker.dashboard"))
    return render_template("worker_profile.html", profile=profile)


@worker_bp.route("/jobs")
@login_required
@worker_required
def browse_jobs():
    q = request.args.get("q", "")
    location = request.args.get("location", "")
    category = request.args.get("category", "")

    jobs_query = Job.query
    if q:
        like = f"%{q}%"
        jobs_query = jobs_query.filter(Job.title.ilike(like) | Job.skills_required.ilike(like))
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))
    if category:
        jobs_query = jobs_query.filter(Job.category.ilike(f"%{category}%"))

    jobs = jobs_query.order_by(Job.created_at.desc()).all()
    return render_template("worker_jobs.html", jobs=jobs, q=q, location=location, category=category)


@worker_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@login_required
@worker_required
def apply_job(job_id):
    profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Please complete your profile before applying.", "warning")
        return redirect(url_for("worker.profile"))

    job = Job.query.get_or_404(job_id)

    existing = Application.query.filter_by(worker_id=profile.id, job_id=job.id).first()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for("worker.browse_jobs"))

    application = Application(worker_id=profile.id, job_id=job.id)
    db.session.add(application)
    db.session.commit()

    # Simple notification stub – replace with SMS or email integration
    print(f"[NOTIFY] New application: worker_profile={profile.id} job={job.title}")

    flash("Applied successfully.", "success")
    return redirect(url_for("worker.dashboard"))


