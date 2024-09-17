from flask import Blueprint, request, jsonify
from app.models.base import db
#from app.models.Request import Request
from app.models import course

courseBP = Blueprint('course', __name__)


