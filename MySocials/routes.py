"""
Non-authentication routes (i.e. home page, settings, etc.)
"""
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, request, g
from .backend import *
from .auth import login_required

main = Blueprint('main', __name__)

## HOME/EVENTS
@main.route("/", methods=["POST", "GET"])
# TODO: Implement filters - yusuf
def index():
    filters = {}
    if request.method == 'GET':
        for field in request.args:
            # If the filter/field has been filled, add it to the dictionary
            if request.args[field]:
                filters[field] = request.args[field]
    # Create cursor
    _, cursor = get_db_conn_cursor()
    cursor.row_factory = sqlite3.Row
    # Get list of societies and events. For now, we're not implementing filters
    events = getAllEvents(cursor, filters)
    societies = getAllSocieties(cursor)
    cursor.close()
    
    return render_template("index.html", events=events, societies=societies)

# TEMP FUNCTIONS untill i implement filters properly
def getAllEvents(cursor, filters):
    query = "SELECT * FROM Event INNER JOIN Society ON Event.societyID = Society.societyID"
    
    filter_queries = []
    for key in filters:
        if key == "search":
            filter_queries.append(f"Event.eventName LIKE '%{filters[key]}%'")
        elif key == "startDate":
            if "startTime" in filters:
                startDateTime = f"{filters['startDate']} {filters['startTime']}"
            else:
                startDateTime = f"{filters['startDate']} 00:00"
            filter_queries.append(f"Event.eventDate >= '{startDateTime}'")
        elif key == "endDate":
            if "endTime" in filters:
                endDateTime = f"{filters['endDate']} {filters['endTime']}"
            else:
                endDateTime = f"{filters['endDate']} 23:59"
            filter_queries.append(f"Event.eventDate <= '{endDateTime}'")
    
    if len(filter_queries) > 0:
        query = query + ' WHERE ' + ' AND '.join(filter_queries)
        print(query)
          
    cursor.execute(query)
    values = cursor.fetchall()
    return values
    
def getAllSocieties(cursor):
    cursor.execute("SELECT * FROM Society")
    values = cursor.fetchall()
    return values


# CREATE EVENT 
@main.route("/create", methods=["POST", "GET"])
@login_required
def create():
    # Function for creating events
    if request.method == 'POST':
        title = request.form['title']
        socID = request.form['societyDropdown']
        location = request.form['location']
        date = request.form["date"]
        description = request.form["description"]
    
    conn, cursor = get_db_conn_cursor()
    cursor.row_factory = sqlite3.Row
    # Gets the societies the user has admin permissions for
    cursor.execute("SELECT * FROM Committee INNER JOIN Society WHERE Committee.userID = (?) AND Society.societyID = Committee.societyID AND Committee.adminFlag = 1", (g.user["userID"],))
    user_societies = cursor.fetchall()
    
    return render_template("create_event.html", societies=user_societies)

# SETTINGS
@main.route("/settings")
def settings():
    return render_template("settings.html")


