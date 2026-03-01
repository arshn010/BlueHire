from flask import Blueprint

employer_bp = Blueprint("employer", __name__, template_folder="../templates")

from . import routes  # noqa: E402,F401


