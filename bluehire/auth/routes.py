import random
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from bluehire import db
from bluehire.models import User, OTP, EmployerProfile, WorkerProfile
from . import auth_bp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        role = request.form.get("role", "worker")

        if not all([name, email, password, role]):
            flash("Please fill all required fields.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        user = User(name=name, email=email, phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == "employer":
            profile = EmployerProfile(user_id=user.id, company_name=f"{name}'s Company")
            db.session.add(profile)
        elif role == "worker":
            profile = WorkerProfile(user_id=user.id)
            db.session.add(profile)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        login_user(user)
        flash("Logged in successfully.", "success")

        if user.role == "employer":
            return redirect(url_for("employer.dashboard"))
        if user.role == "worker":
            return redirect(url_for("worker.dashboard"))
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/otp/request", methods=["GET", "POST"])
def request_otp():
    if request.method == "POST":
        phone = request.form.get("phone")
        if not phone:
            flash("Please enter a phone number.", "danger")
            return render_template("otp_request.html")

        code = f"{random.randint(100000, 999999)}"
        otp = OTP(phone=phone, code=code)
        db.session.add(otp)
        db.session.commit()

        # In real system, send SMS here. For now, show on screen for demo.
        flash(f"Your OTP code is: {code} (for demo only)", "info")
        session["otp_phone"] = phone
        return redirect(url_for("auth.verify_otp"))

    return render_template("otp_request.html")


@auth_bp.route("/otp/verify", methods=["GET", "POST"])
def verify_otp():
    phone = session.get("otp_phone")
    if not phone:
        flash("Please request an OTP first.", "warning")
        return redirect(url_for("auth.request_otp"))

    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            flash("Enter the OTP code.", "danger")
            return render_template("otp_verify.html", phone=phone)

        otp = (
            OTP.query.filter_by(phone=phone, code=code, is_used=False)
            .order_by(OTP.created_at.desc())
            .first()
        )
        if not otp or datetime.utcnow() - otp.created_at > timedelta(minutes=10):
            flash("Invalid or expired OTP.", "danger")
            return render_template("otp_verify.html", phone=phone)

        otp.is_used = True
        db.session.commit()

        user = User.query.filter_by(phone=phone).first()
        if user:
            login_user(user)
            flash("Logged in with mobile OTP.", "success")
            if user.role == "employer":
                return redirect(url_for("employer.dashboard"))
            if user.role == "worker":
                return redirect(url_for("worker.dashboard"))
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
        else:
            flash("Phone verified. Please complete registration.", "success")
            return redirect(url_for("auth.register"))

    return render_template("otp_verify.html", phone=phone)


