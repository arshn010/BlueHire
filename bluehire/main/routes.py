print("MAIN ROUTES FILE LOADED")
from flask import render_template, request, redirect, url_for, abort, flash, current_app
from flask_login import current_user

from . import main_bp
from ..models import Job, Tool, ToolRental, WorkerProfile
from datetime import datetime, timedelta
from ..models import ToolRental, WorkerProfile
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from bluehire import db
from flask import request, jsonify

@main_bp.route("/")
def index():
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

    jobs = jobs_query.order_by(Job.created_at.desc()).limit(20).all()

    return render_template("index.html", jobs=jobs, q=q, location=location, category=category, user=current_user)

@main_bp.route("/tools")
@login_required
def tools():

    tools = Tool.query.all()

    return render_template("tools.html", tools=tools)

@main_bp.route("/jobs")
def jobs():
    from bluehire.models import Job
    jobs = Job.query.all()
    return render_template("worker_jobs.html", jobs=jobs)


@main_bp.route('/add_tool', methods=['GET', 'POST'])
def add_tool():

    if request.method == 'POST':

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
            name=request.form['name'],
            description=request.form['description'],
            price_per_day=int(request.form['price']),           
            image=filename
        )

        db.session.add(tool)
        db.session.commit()

        return redirect(url_for('main.tools'))

    return render_template('add_tool.html')


@main_bp.route('/rent/<int:tool_id>', methods=['POST'])
@login_required
def rent_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    if current_user.role != "worker":        
        abort(403)

    if not tool.is_available:
        return redirect(url_for('main.tools'))

    days = int(request.form.get('days', 1))

    worker_profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()

    if not worker_profile:
        return "Only workers can rent tools."

    end_date = datetime.utcnow() + timedelta(days=days)
    total_price = tool.price_per_day * days

    rental = ToolRental(
        tool_id=tool.id,
        worker_id=worker_profile.id,
        end_date=end_date,
        total_price=total_price
    )

    tool.is_available = False

    db.session.add(rental)
    db.session.commit()

    return redirect(url_for('main.tools'))

@main_bp.route('/return/<int:rental_id>')
@login_required
def return_tool(rental_id):
    rental = ToolRental.query.get_or_404(rental_id)

    # Ensure only the worker who rented it can return it
    worker_profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()

    if not worker_profile or rental.worker_id != worker_profile.id:
        return "Unauthorized access"

    rental.status = "returned"
    rental.tool.is_available = True

    db.session.commit()

    return redirect(url_for('main.tools'))

@main_bp.route('/my_rentals')
@login_required
def my_rentals():

    if current_user.role != "worker":
        abort(403)

    worker_profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()

    if not worker_profile:
        flash("Worker profile not found.", "warning")
        return redirect(url_for("main.index"))

    rentals = ToolRental.query.filter_by(worker_id=worker_profile.id).all()

    return render_template('my_rentals.html', rentals=rentals)

@main_bp.route('/payment/<int:tool_id>', methods=['GET', 'POST'])
@login_required
def payment_page(tool_id):

    tool = Tool.query.get_or_404(tool_id)

    if request.method == "POST":
        days = int(request.form.get("days", 1))
    else:
        days = int(request.args.get("days", 1))

    total_price = tool.price_per_day * days

    return render_template(
        "payment.html",
        tool=tool,
        days=days,
        total_price=total_price
    )

@main_bp.route('/confirm_payment/<int:tool_id>', methods=['POST'])
@login_required
def confirm_payment(tool_id):

    tool = Tool.query.get_or_404(tool_id)

    days = int(request.form.get("days"))
    payment_method = request.form.get("payment_method")

    worker_profile = WorkerProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    end_date = datetime.utcnow() + timedelta(days=days)

    total_price = tool.price_per_day * days

    rental = ToolRental(
        tool_id=tool.id,
        worker_id=worker_profile.id,
        end_date=end_date,
        total_price=total_price,
        status="active"
    )

    tool.is_available = False

    db.session.add(rental)
    db.session.commit()

    flash(f"Payment successful via {payment_method.upper()}!", "success")

    return redirect(url_for("main.my_rentals"))

@main_bp.route("/chatbot", methods=["POST"])
def chatbot():

    message = request.json.get("message").lower()

    if "job" in message:
        reply = "You can find available jobs on the homepage or click 'Find Jobs' in your dashboard."

    elif "tool" in message:
        reply = "Go to the Tools page and click 'Rent Now' to rent equipment."

    elif "worker" in message:
        reply = "Employers can view worker applications and contact them via Email or WhatsApp."

    elif "help" in message:
        reply = "You can ask me about jobs, tools, workers, or how to use BlueHire."

    else:
        reply = "Sorry, I didn't understand. Try clicking one of the options."

    return jsonify({"reply": reply})