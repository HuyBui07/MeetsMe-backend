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
        group_member_rowcount = execute_query("INSERT INTO group_member (group_id, user_id) VALUES (%s, %s)", 
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
        query = "SELECT group_id, `group`.name FROM group_member INNER JOIN `group` ON group_member.group_id = `group`.id WHERE user_id = %s;"
        params = (user_id, )
        cursor.execute(query, params)
        groups = cursor.fetchall()
        cursor.close()
        connection.close()
        
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
        
        # Get a specific group's details
        query = "SELECT `group`.id, name, user.username FROM `group` INNER JOIN user ON `group`.creator_id = user.id WHERE `group`.id = %s;"
        params = (group_id, )
        cursor.execute(query, params)
        group = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if group:
            group_details = {"group_id": group[0], "group_name": group[1], "group_creator": group[2]}
            return jsonify(group_details), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
# Get all groups members
@group.route("/get_group_members", methods=["GET"])
@jwt_required()
def get_group_members():
    group_id = request.args.get("group_id")
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Get a specific group's details
        query = "select user_id as member_id, username as member_name, group_id from group_member join user on user_id = id where group_id= %s;"
        params = (group_id, )
        cursor.execute(query, params)
        group = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if group:
            group_members = [{"member_id": member[0], "member_name": member[1]} for member in group]
            return jsonify(group_members), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
# Send group invitation
@group.route("/invite", methods=["POST"])
@jwt_required()
def group_invitation():
    # Get request body's data
    data = request.get_json()
    receiver_id = data["receiver_id"]
    group_id = data["group_id"]
    
    # Get current user's id
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    # Insert group request
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        query = "INSERT INTO group_invitation (sender_id, receiver_id, group_id) VALUES (%s, %s, %s)"
        params = (user_id, receiver_id, group_id)
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Group invitation sent successfully"}), 200
        
    except Error as e:
        print("Error while trying to work with MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
# Get group invitations
@group.route("/invitations", methods=["GET"])
@jwt_required()
def get_group_invitations():
    # Get current's user id
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        query = "select sender_id, username, receiver_id, group_id, name from group_invitation inner join user on group_invitation.sender_id = user.id inner join `group` on group_invitation.group_id = `group`.id where receiver_id = %s;"
        params = (user_id, )
        cursor.execute(query, params)
        invitations = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        
        if invitations:
            invitations_list = [{"group_id": invitation[3], "group_name": invitation[4]} for invitation in invitations]
            return jsonify(invitations_list), 200
        else:
            return jsonify([]), 200
        
    except Error as e:
        print("Error while trying to work with MySQL:", e)
        return jsonify({"error": str(e)}), 500
            

# Response group invitation
@group.route("/response", methods=["POST"])
@jwt_required()
def group_invitation_response():
    # Get request body's data
    data = request.get_json()
    group_id = data["group_id"]
    response = data["response"]
    
    # Get current user's id
    current_user = get_jwt_identity()
    receiver_id = current_user["id"]
    
    # Insert group request
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        if response == "accept":
            query = "INSERT INTO group_member (group_id, user_id) VALUES (%s, %s)"
            params = (group_id, receiver_id)
            cursor.execute(query, params)
            connection.commit()
            
        query = "DELETE FROM group_invitation WHERE receiver_id = %s AND group_id = %s"
        params = (receiver_id, group_id)
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Group invitation response sent successfully with" + response}), 200
        
    except Error as e:
        print("Error while trying to work with MySQL:", e)
        return jsonify({"error": str(e)}), 500
