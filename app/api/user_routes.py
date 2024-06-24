from flask import Blueprint, request, jsonify
from mysql.connector import Error
from bcrypt import hashpw, gensalt, checkpw
from ..utils.db import execute_query, database_connect
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta

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
        # Establish database connection
        connection = database_connect()
        cursor = connection.cursor()
        
        # Insert user in database
        rowcount = execute_query("INSERT INTO User(username, password) VALUES(%s, %s)", 
                                 connection, 
                                 cursor,
                                 (username, hashed_password))
        
        return jsonify({"message": "User created successfully with" + rowcount + "changed."}), 201

    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500


@user.route("/signin", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data["username"]
    password = data["password"].encode("utf-8")

    try:
        # Establish database connection
        connection = database_connect()
        cursor = connection.cursor()
        
        # Get user's data to check for existed state
        user = execute_query("SELECT * FROM user WHERE username = %s", 
                             connection, 
                             cursor, 
                             (username, ), 
                             fetchone=True)

        if user is not None:
            stored_password = user[2].encode("utf-8")
            if checkpw(password, stored_password):
                access_token = create_access_token(identity={"id": user[0], "username": user[1]}, expires_delta=timedelta(hours=24))
                return jsonify({"access token": access_token}), 201
            else: 
                return jsonify({"message": "Wrong password"}), 401
        else:
            return jsonify({"error": "User is not existed"}), 401
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
    
@user.route("/search", methods=["GET"])
def search_users():
    data = request.get_json()
    user_query = data["query"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        query = "SELECT * FROM user WHERE username LIKE %s"
        params = (f"%{user_query}%", )
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        user_list = [{"id": result[0], "username": result[1]} for result in results]
        return jsonify(user_list), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
            