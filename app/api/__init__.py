from flask import Blueprint
from .hello_routes import hello
from .user_routes import user

api = Blueprint("api", __name__)
api.register_blueprint(hello, url_prefix="/hello")
api.register_blueprint(user, url_prefix="/user")