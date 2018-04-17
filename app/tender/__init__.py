from flask import Blueprint

bp = Blueprint('tender', __name__)

from app.tender import routes
