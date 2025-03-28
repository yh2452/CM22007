'''User Authentication

This includes registering accounts and logging into said accounts, along with managing user sessions for the whole site. 
'''
import functools
from flask import g, render_template, redirect, url_for, request, flash, session, Blueprint
from .backend import *

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=["POST", "GET"])
def register():
    #TODO: add more validation checks for entered information
    # e.g. things like making sure the password is of a certain strength, etc.
    if request.method == 'POST':
        connection, cursor = get_db_conn_cursor()
        
        forename = request.form["Forename"]
        surname = request.form["Surname"]
        username = request.form["Username"]
        email = request.form["Email"]
        password = request.form["Password"]
        confirm_pass = request.form["Confirm Password"]
        error = None

        #TODO: better password verification
        # If the password and confirm password fields are different, raise error
        if password != confirm_pass:
            error = 'Confirm password should be identical to password.'
            #TODO: make this sound human jesus
        
        if "@" not in email:
            error = "Please enter a valid email address."
        
        # If any field is left empty, raise error
        for field in request.form:
            if not request.form[field]:
                error = f'{field} is required.'
        
        if error is None:
            # This is where I add the user to the database
            # TODO: create a function in backend.py to do this.
            # Check if there are any duplicate users
            if isUserDuplicate(cursor, username, email):
                error = 'User is already registered.'
            else:
                addUser(cursor, forename, surname, username, password, email)
                connection.commit()
                cursor.close()
                return redirect(url_for("auth.login"))
        
        flash(error)
    
    return render_template("register.html")



# LOGIN
@auth.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        
        _, cursor = get_db_conn_cursor()
        cursor.row_factory = sqlite3.Row
        user = getUserFromUsername(cursor, username)
        if user is None:
            error = "Incorrect username."
        elif not checkHash(password, user["password"]):
            error = "Incorrect password."
        cursor.close()
        
        if error is None:
            # Set the given user ID to our current user session.
            session.clear()
            session["userID"] = user["userID"]
            return redirect(url_for('main.index'))
        
        flash(error)
    
    return render_template('login.html')

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('userID')
    
    if user_id is None:
        g.user = None
    else:
        _, cursor = get_db_conn_cursor()
        cursor.row_factory = sqlite3.Row
        g.user = cursor.execute("SELECT * FROM User WHERE userID = (?)", (user_id,)).fetchone()

# LOGOUT
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


def login_required(view):
    # Wrapper used when a view requires the user to be logged in
    # e.g. creating blog posts
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view