import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, render_template
from flask_session import Session

from server.auth import app_auth
from server.routes import app_routes

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Import general routes and authentication routes and register the blueprints
app.register_blueprint(app_auth)
app.register_blueprint(app_routes)

# Add a custom jinja filter for handling unix dates
@app.template_filter('stime')
def timestime(s):
    return datetime.fromtimestamp(s).strftime('%m/%d/%y %-I:%M %p')
