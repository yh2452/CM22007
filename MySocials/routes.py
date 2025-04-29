"""
Non-authentication routes (i.e. home page, settings, etc.)
"""
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, request, g, session
from .backend import *
from .auth import login_required

main = Blueprint('main', __name__)

## HOME/EVENTS
@main.route("/", methods=["POST", "GET"])
# TODO: Implement filters - yusuf
def index():
    filters = {}
    # Create cursor
    conn, cursor = get_db_conn_cursor()
    cursor.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        # MARKING EVENT AS ATTENDED
        if request.form['attendButton'] and g.user:
            toggleAttend(cursor, session["userID"], request.form['attendButton'])
            conn.commit()
    
    if request.method == 'GET':
        for field in request.args:
            # If the filter/field has been filled, add it to the dictionary
            if request.args[field]:
                filters[field] = request.args[field]
   
    # Get list of societies and events. 
    events = getAllEvents(cursor, filters)
    societies = getAllSocieties(cursor)
    
    # Code to get only the eventID for the events to be attended
    attending = []
    if g.user:
        attendingEvents = getAllAttendingEvents(cursor, session["userID"])
        for event in attendingEvents:
            attending.append(event["eventID"])
    
    cursor.close()
    
    # CODE FOR DETERMINING WHETHER OR NOT TO USE THE ALT CSS STYLING
    USE_ALT_STYLE = session.get("use_alt_style")
    if USE_ALT_STYLE is None:
        session["use_alt_style"] = False
        USE_ALT_STYLE = False
   
    
    return render_template("index.html", events=events, societies=societies, 
                           attending=attending, alt_style=USE_ALT_STYLE)

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
        elif key == "subscribed":
            attending = []
            # _, temp_cursor = get_db_conn_cursor()
            if g.user:
                attendingEvents = cursor.execute("SELECT Event.eventID FROM Event INNER JOIN Attending ON Event.eventID=Attending.eventID WHERE Attending.userID = (?)", (session["userID"],)).fetchall()
                for event in attendingEvents:
                    attending.append(event["eventID"])
                if len(attending) > 0:
                    filter_queries.append(f"Event.eventID IN {tuple(attending)}")
                else:
                    return []

            
            
        elif key == "onCampus":
            filter_queries.append(f"Event.eventTags LIKE '%{filters[key]}%'")
    
    # SOCIETY SELECTION
    if "socID" in session:
        if session["socID"] != -1:
            filter_queries.append(f"Society.societyID = {session['socID']}")
    
    if len(filter_queries) > 0:
        query = query + ' WHERE ' + ' AND '.join(filter_queries)
        print(f"Selecting events, query: {query}")
    query += ' ORDER BY Event.eventDate DESC'
          
    cursor.execute(query)
    values = cursor.fetchall()
    return values
    
def getAllSocieties(cursor):
    cursor.execute("SELECT * FROM Society")
    values = cursor.fetchall()
    return values

# REDIRECT FOR FILTERING BY SOCIETY 
@main.route("/society/<int:id>")
def filter_society(id):
    # filters the shown events on home page by society
    if "socID" in session:
        if session["socID"] == id:
            # If the same one is selected again, remove it entirely 
            session["socID"] = -1
            print(f"Current Selected Society ID is: {session['socID']}")
            return redirect(url_for('main.index'))
        
    session["socID"] = id
    print(f"Current Selected Society ID is: {session['socID']}")
    return redirect(url_for('main.index'))


# CREATE EVENT 
@main.route("/create", methods=["POST", "GET"])
@login_required
def create():
    # Function for creating events
    conn, cursor = get_db_conn_cursor()
    cursor.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        title = request.form['title']
        socID = request.form['societyDropdown']
        location = request.form['location']
        date = request.form["date"]
        description = request.form["description"]
        tags = request.form["tags"]
        
        addSocial(cursor, socID, g.user["userID"], title, date, description, tags)
        conn.commit()
        return redirect(url_for('main.index'))
    
    # Gets the societies the user has admin permissions for
    cursor.execute("SELECT * FROM Committee INNER JOIN Society WHERE Committee.userID = (?) AND Society.societyID = Committee.societyID AND Committee.adminFlag = 1", (g.user["userID"],))
    user_societies = cursor.fetchall()
    
    return render_template("create_event.html", societies=user_societies)

# SETTINGS
@main.route("/settings")
def settings():
    return render_template("settings.html")

@main.route("/toggle_style")
def toggle_style():
    """Changes between the different css files.
    """
    session['use_alt_style']  = not session.get('use_alt_style', False)
    print("Alternate CSS being used: {}".format(session['use_alt_style']))
    return redirect(url_for('main.index'))


