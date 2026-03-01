from flask import Blueprint

worker_bp = Blueprint("worker", __name__, template_folder="../templates")

from . import routes  # noqa: E402,F401


