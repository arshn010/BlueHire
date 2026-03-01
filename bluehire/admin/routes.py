from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from bluehire.models import User, Job, Application
from . import admin_bp


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()
    return render_template("admin_dashboard.html", users=users, jobs=jobs, applications=applications)


