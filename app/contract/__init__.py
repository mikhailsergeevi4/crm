from flask import Blueprint

bp = Blueprint('contract', __name__)

from app.contract import routes
