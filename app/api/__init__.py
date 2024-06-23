from flask import Blueprint
from .group_routes import group
from .user_routes import user

api = Blueprint("api", __name__)
api.register_blueprint(group, url_prefix="/group")
api.register_blueprint(user, url_prefix="/user")