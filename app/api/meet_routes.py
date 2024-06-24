from flask import Blueprint, request, jsonify
from mysql.connector import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import execute_query, database_connect

meet = Blueprint("meet", __name__)

@meet.route("/open")
@jwt_required()
def open_meet():
    return 