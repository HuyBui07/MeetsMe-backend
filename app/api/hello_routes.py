from flask import Blueprint

hello = Blueprint("hello", __name__)

@hello.route("/")
def hello_world():
    return "<p>Hello world!</p>"