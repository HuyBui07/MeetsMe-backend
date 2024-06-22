from flask import Blueprint, request, jsonify
from mysql.connector import Error
from bcrypt import hashpw, gensalt, checkpw
from ..utils.db import execute_query

user = Blueprint("user", __name__)

@user.route("/signup", methods=["POST"])
def sign_up():
    # Extract data from the request
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    # Hash the password
    salt = gensalt()
    hashed_password = hashpw(password.encode("utf-8"), salt)

    try:
        rowcount = execute_query("INSERT INTO User(username, password) VALUES(%s, %s)", (username, hashed_password))
        return jsonify({"message": "User created successfully"}), 201

    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500


@user.route("/signin", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data["username"]
    password = data["password"].encode("utf-8")

    try:
        
            user = execute_query("SELECT * FROM user WHERE username = %s", (username, ), fetchone=True)

            if user is not None:
                stored_password = user[2].encode("utf-8")
                if checkpw(password, stored_password):
                    return jsonify({"message": "Authenticated successfully"}), 201
                else: 
                    return jsonify({"message": "Wrong password"}), 401
            else:
                return jsonify({"error": "User is not existed"}), 401
            
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
            