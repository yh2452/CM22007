'''User Authentication

This includes registering accounts and logging into said accounts, along with managing user sessions for the whole site. 
'''

from flask import g, render_template, redirect, url_for, request, flash, session, Blueprint
from .backend import *

auth = Blueprint('auth', __name__)


@auth.before_app_request
def load_logged_in_user():
    """
    Stores the data of the current logged in user while making a request. 
    """
    user_id = session.get("userID")
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db_cursor().execute(
            'SELECT * FROM User WHERE userID = (?)', (user_id)
        ).fetchone()


@auth.route('/register', methods=["POST", "GET"])
def register():
    #TODO: add more validation checks for entered information
    # e.g. things like making sure the password is of a certain strength, etc.
    if request.method == 'POST':
        cursor = get_db_cursor()
        
        forename = request.form["Forename"]
        surname = request.form["Surname"]
        username = request.form["Username"]
        email = request.form["Email"]
        password = request.form["Password"]
        confirm_pass = request.form["Confirm Password"]
        error = None
    
        # If the password and confirm password fields are different, raise error
        if password != confirm_pass:
            error = 'Confirm password should be identical to password.'
            #TODO: make this sound human jesus
        
        # If any field is left empty, raise error
        for field in request.form:
            if not request.form[field]:
                error = f'{field} is required.'
        
        if error is None:
            # This is where I add the user to the database
            # TODO: create a function in backend.py to do this.
            # Check if there are any duplicate users
            if isUserDuplicate():
                error = 'User is already registered.'
            else:
                addUser(cursor, forename, surname, username, password, email)
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
        
        cursor = get_db_cursor()
        user = getUserFromUsername(cursor, username)
        if user is None:
            error = "Incorrect username."
        elif not checkPasswordHash(user["password"], username, passsword):
            error = "Incorrect password."
        cursor.close()
        
        if error is None:
            # Set the given user ID to our current user session.
            session.clear()
            session["userID"] = user["userID"]
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('login.html')
        

def checkPasswordHash(hash, username, password):
    """
    Compares entered password to stored hash
    """
    new_hash = SHA3(password, username)
    if hash == new_hash:
        return True
    else:
        return False


# LOGOUT
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))