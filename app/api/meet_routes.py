from flask import Blueprint, request, jsonify
from mysql.connector import Error
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.db import execute_query, database_connect
from ..utils.serialize import serialize
from datetime import datetime

meet = Blueprint("meet", __name__)

# Open a meet
@meet.route("/open", methods=["POST"])
@jwt_required()
def open_meet():
    # Get inputs
    data = request.get_json()
    group_id = data["group_id"]
    title = data["title"]
    location = data["location"]
    date = data["date"]
    time = data["time"]
    
    # Get user id from access token
    current_user = get_jwt_identity()
    opener_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Check if the user is a member of the meet's group
        member_query = "SELECT * FROM group_member WHERE user_id = %s AND group_id = %s"
        member_params = (opener_id, group_id)
        cursor.execute(member_query, member_params)
        member = cursor.fetchone()
        
        if member is None:
            return jsonify({"message": "You are not a member of this meet's group"}), 401
        
        # Insert the meet
        query = "INSERT INTO `meet`(group_id, title, location, time, opener_id, date) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (group_id, title, location, time, opener_id, date)
        cursor.execute(query, params)
        connection.commit()
        
        if cursor.lastrowid:
            return jsonify({"message": "Meet opened successfully"}), 200
        else:
            return jsonify({"message": "Failed to open the meet"}), 400
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500

# Close a meet
@meet.route("/close", methods=["PATCH"])
@jwt_required()
def close_meet():
    # Get inputs
    data = request.get_json()
    meet_id = data["meet_id"]
    
    # Get user id from access token
    current_user = get_jwt_identity()
    closer_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Check if the user is the opener of the meet
        opener_query = "SELECT opener_id FROM `meet` WHERE id = %s"
        closer_params = (meet_id, )
        cursor.execute(opener_query, closer_params)
        opener_id = cursor.fetchone()[0]
        
        if closer_id != opener_id:
            return jsonify({"message": "You are not the opener of this meet"}), 401
        
        query = "UPDATE `meet` SET status = \"closed\" WHERE id = %s"
        params = (meet_id, )
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        if cursor.rowcount > 0:
            return jsonify({"message": "Meet closed successfully"}), 200
        else:
            return jsonify({"message": "Failed to close the meet"}), 400
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500

# Get all the group's meets
@meet.route("/get_all_meets", methods=["GET"])
@jwt_required()
def get_all_meets():
    # Get inputs
    group_id = request.args.get('group_id')
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        query = "SELECT meet.id, title, username, status FROM `meet` INNER JOIN user on `meet`.opener_id = user.id WHERE group_id = %s"
        params = (group_id, )
        cursor.execute(query, params)
        meets = cursor.fetchall()
        meet_list = [{"id": meet[0], "title": meet[1], "opener_name": meet[2], "status": meet[3]} for meet in meets]
        
        cursor.close()
        connection.close()
        
        if meets:
            return jsonify(meet_list), 200
        else:
            return jsonify({"message": "No meets found"}), 404
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500


# Get meet details
@meet.route("/get_meet_details", methods=["GET"])
@jwt_required()
def get_meet_details():
    # Get inputs
    meet_id = request.args.get('meet_id')
    group_id = request.args.get('group_id')
    
    # Get user id from access token
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Check if the user is a member of the meet's group
        member_query = "SELECT * FROM group_member WHERE user_id = %s AND group_id = %s"
        params = (user_id, group_id)
        cursor.execute(member_query, params)
        member = cursor.fetchone()
        
        if member is None:
            return jsonify({"message": "You are not a member of this meet's group"}), 401
        
        # Get the meet's details
        query = "SELECT meet.id, title, location, date, time, username, status FROM `meet` INNER JOIN user on meet.opener_id = user.id WHERE meet.id = %s"
        params = (meet_id, )
        cursor.execute(query, params)
        meet = cursor.fetchone()

        # Convert timedelta to time object
        meet_time = meet[4]
        converted_time = (datetime.min + meet_time).time()
        time_string = converted_time.strftime('%H:%M:%S')
        
        meet_details = {"id": meet[0], "title": meet[1], "location": meet[2], "date": meet[3].strftime("%d/%m/%y"), "time": time_string, "opener_name": meet[5], "status": meet[6]}
        
        if meet:
            return jsonify(meet_details), 200
        else:
            return jsonify({"message": "Meet not found"}), 404
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500

# Accept a meet
@meet.route("/accept", methods=["POST"])
@jwt_required()
def accept_meet():
    # Get inputs
    data = request.get_json()
    meet_id = data["meet_id"]
    
    # Get user id from access token
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        # Check if the user is a member of the meet's group
        group_query = "SELECT group_id, status FROM `meet` WHERE id = %s"
        group_params = (meet_id, )
        cursor.execute(group_query, group_params)
        data = cursor.fetchone()
        group_id = data[0]
        status = data[1]
        
        if status == "closed":
            return jsonify({"message": "This meet is closed"}), 400
        
        member_query = "SELECT * FROM group_member WHERE user_id = %s AND group_id = %s"
        member_params = (user_id, group_id)
        cursor.execute(member_query, member_params)
        member = cursor.fetchone()
        
        if member is None:
            return jsonify({"message": "You are not a member of this meet's group"}), 401
        
        # Insert the user into the meet's attendees
        query = "INSERT INTO meet_member(user_id, meet_id) VALUES (%s, %s)"
        params = (user_id, meet_id)
        cursor.execute(query, params)
        connection.commit()
        insert_check = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return jsonify({"message": "Meet accepted successfully"}), 200
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500
    
# Get all the meet's attendees
@meet.route("/get_all_attendees", methods=["GET"])
@jwt_required()
def get_all_attendees():
    # Get inputs
    
    meet_id = request.args.get('meet_id')
    
    try:
        connection = database_connect()
        cursor = connection.cursor()
        
        query = "SELECT username FROM meet_member INNER JOIN user on meet_member.user_id = user.id WHERE meet_id = %s"
        params = (meet_id, )
        cursor.execute(query, params)
        attendees = cursor.fetchall()
        attendees_list = [attendee[0] for attendee in attendees]
        
        cursor.close()
        connection.close()
        
        if attendees:
            return jsonify(attendees_list), 200
        else:
            return jsonify({"message": "No attendees found"}), 404
        
    except Error as e:
        print("Error while trying to connect to MySQL:", e)
        return jsonify({"error": str(e)}), 500