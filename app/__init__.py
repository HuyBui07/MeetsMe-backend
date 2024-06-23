import os
from flask import Flask
from .api import api as api_blueprint
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_blueprint, url_prefix="/api")

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    JWTManager(app)

    return app