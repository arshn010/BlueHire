print("MAIN ROUTES FILE LOADED")
from flask import render_template, request, redirect, url_for
from flask_login import current_user

from . import main_bp
from bluehire.models import Job, Tool
from .. import db
from datetime import datetime, timedelta
from ..models import ToolRental, WorkerProfile
from flask_login import login_required

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

@main_bp.route('/tools')
def tools():
    tools = Tool.query.all()
    return render_template('tools.html', tools=tools)


@main_bp.route('/add_tool', methods=['GET', 'POST'])
def add_tool():
    if request.method == 'POST':
        tool = Tool(
            name=request.form['name'],
            description=request.form['description'],
            price_per_day=request.form['price']
        )
        db.session.add(tool)
        db.session.commit()
        return redirect(url_for('main.tools'))

    return render_template('add_tool.html')


@main_bp.route('/rent/<int:tool_id>', methods=['POST'])
@login_required
def rent_tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)

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
    worker_profile = WorkerProfile.query.filter_by(user_id=current_user.id).first()

    if not worker_profile:
        return "Only workers can view rentals."

    rentals = ToolRental.query.filter_by(worker_id=worker_profile.id).all()

    return render_template('my_rentals.html', rentals=rentals)