import os
import requests
import urllib.parse

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, redirect, render_template, request, session
from functools import wraps

from server.helpers import handle_error
from server.db import db

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Checks that there is a session active for the current user
        if session.get("user_id") is None:

            # If not, redirects them to login
            return redirect("/login")

        # Otherwise allows the method to run as expected
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorate routes to require admin access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Check to see if the currently logged in user is an admin

        # Otherwise allow the method to run as expected
        return f(*args, **kwargs)

    return decorated_function


# Define a blueprint to use for the following routes
app_auth = Blueprint('app_auth', __name__)

@app_auth.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return handle_error("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return handle_error("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return handle_error("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to admin dashboard
        return redirect("/dashboard")

        # TODO: Redirect user conditionally; if they are admin go to dashboard, if not admin, go to user profile

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app_auth.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app_auth.route("/register", methods=["GET", "POST"])
def register():
    """Register an admin user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return handle_error("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return handle_error("must provide password", 400)

        # Ensure password confirm was submitted
        elif not request.form.get("confirmation"):
            return handle_error("must confirm password", 400)

        # Ensure passwords match and confirmation isn't empty
        elif request.form.get("confirmation") != request.form.get("password"):
            return handle_error("passwords must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is available
        if len(rows) != 0:
            return handle_error("username is already taken", 400)

        # Hash the password
        hash = generate_password_hash(request.form.get("password", "sha256"))

        # Add the user to the database
        db.execute("INSERT INTO users (is_admin, username, hash) VALUES(?, ?, ?)", 1, request.form.get("username"), hash)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app_auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allows logged in user to change their password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure that old password was submitted
        if not request.form.get("old-password"):
            return handle_error("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return handle_error("must provide password", 400)

        # Ensure password confirm was submitted
        elif not request.form.get("confirmation"):
            return handle_error("must confirm password", 400)

        # Ensure passwords match and confirmation isn't empty
        elif request.form.get("confirmation") != request.form.get("password"):
            return handle_error("passwords must match", 400)

        # Query database for password hash
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Ensure old password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("old-password")):
            return handle_error("old password inputted incorrectly", 403)

        # Hash the new password
        hash = generate_password_hash(request.form.get("password", "sha256"))

        # Add the user to the database
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change-password.html")
