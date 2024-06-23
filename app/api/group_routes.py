from flask import Blueprint, request, jsonify
from mysql.connector import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import execute_query, database_connect

group = Blueprint("group", __name__)

@group.route("/add", methods=["POST"])
@jwt_required()
def add_group():
    # Get inputed group name
    data = request.get_json()
    group_name = data["name"]
    
    # Get user id from access token
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Insert new group
        query = "INSERT INTO `group`(name, creator_id) VALUES (%s, %s)"
        params = (group_name, user_id)
        cursor.execute(query, params)
        connection.commit()
        new_group_id = cursor.lastrowid
        
        # Insert new group member
        group_member_rowcount = execute_query("INSERT INTO groupmember (group_id, user_id) VALUES (%s, %s)", 
                                 connection=connection, 
                                 cursor=cursor, 
                                 params=(new_group_id, user_id))
        
        if new_group_id and group_member_rowcount > 0:
            return jsonify({"message": "Group added successfully"}), 200
        else: 
            return jsonify({"message": "Failed to add the group"}), 400
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    

# Get all the user's groups
@group.route("/get_all_groups", methods=["GET"])
@jwt_required()
def get_all_groups():
    # Get user id from access token
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Get all user's groups
        query = "SELECT group_id, `group`.name FROM groupmember INNER JOIN `group` ON groupmember.group_id = `group`.id WHERE user_id = %s;"
        params = (user_id, )
        cursor.execute(query, params)
        groups = cursor.fetchall()
        
        if groups:
            groups_list = [{"group_id": group[0], "name": group[1]} for group in groups]
            return jsonify(groups_list), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500


# Get one group's details
@group.route("/get_group_details", methods=["GET"])
@jwt_required()
def get_group_details():
    data = request.get_json()
    group_id = data["group_id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Get all user's groups
        query = "SELECT `group`.id, name, user.username FROM `group` INNER JOIN user ON `group`.creator_id = user.id WHERE `group`.id = %s;"
        params = (group_id, )
        cursor.execute(query, params)
        group = cursor.fetchone()
        
        if group:
            group_details = {"group_id": group[0], "group_name": group[1], "group_creator": group[2]}
            return jsonify(group_details), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    