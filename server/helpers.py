
from flask import redirect, render_template, request, session

def handle_error(message, code=400):
    """Render message as an apology to user. Adapted from Finance PSET."""
    return render_template("error.html", code=code, message=message)


