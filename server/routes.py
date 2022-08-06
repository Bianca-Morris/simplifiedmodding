import os
import requests
import urllib.parse
import datetime
import math
import time
import sys

from flask import Blueprint, redirect, render_template, request, session, jsonify

from server.db import db
from server.auth import login_required, admin_required
from server.helpers import handle_error

# Define a blueprint to use for the following routes
app_routes = Blueprint('app_routes', __name__)

@app_routes.route("/")
def index():
    """Show home page"""

    # Displays 3 most recently updated mods
    recently_updated_mods = db.execute("SELECT mods.id, title, updated, published, version, feature_img_url, users.username\
                                       FROM mods\
                                       JOIN users on users.id = mods.mod_author\
                                       WHERE is_draft = 0 AND is_private = 0\
                                       ORDER BY updated desc\
                                       LIMIT 3")

    # Displays 3 most recently published mods
    recently_published_mods = db.execute("SELECT mods.id, title, updated, published, version, feature_img_url, users.username\
                                        FROM mods\
                                         JOIN users on users.id = mods.mod_author\
                                         WHERE is_draft = 0 AND is_private = 0\
                                         ORDER BY published desc\
                                         LIMIT 3")

    # Display 3 most recently published tutorials
    recently_published_tutorials = db.execute("SELECT tutorials.id, title, updated, published, feature_img_url, users.username\
                                        FROM tutorials\
                                         JOIN users on users.id = tutorials.tutorial_author\
                                         WHERE is_draft = 0 AND is_private = 0\
                                         ORDER BY published desc\
                                         LIMIT 3")

    return render_template("index.html", context={
        "recently_published_mods": recently_published_mods,
        "recently_updated_mods": recently_updated_mods,
        "recently_published_tutorials": recently_published_tutorials
    })


@app_routes.route("/about")
def about():
    """Show a static page with some information about the platform"""
    return render_template("about.html")


@app_routes.route("/search", methods=["POST"])
def search():
    """Retrieve a list of mods and/or tutorials that have the keywords in the title"""
    
    # Grab the selected keywords
    keywords = request.form.get("keywords")

    # Ensure the keywords were submitted
    if not keywords:
        return handle_error("must provide keywords", 403)

    # Grabs all mods that contain this
    found_mods = db.execute("SELECT mods.id, title, updated, published, version, feature_img_url, users.username\
                            FROM mods\
                            JOIN users on users.id = mods.mod_author\
                            WHERE is_draft = 0 AND is_private = 0 AND title LIKE ?\
                            ORDER BY updated desc", "%" + keywords + "%")

    # Search tutorial titles too
    found_tutorials = db.execute("SELECT tutorials.id, title, updated, published, feature_img_url, users.username\
                            FROM tutorials\
                            JOIN users on users.id = tutorials.tutorial_author\
                            WHERE is_draft = 0 AND is_private = 0 AND title LIKE ?\
                            ORDER BY updated desc", "%" + keywords + "%")

    return render_template("search-results.html", context={
        "mods": found_mods,
        "tutorials": found_tutorials,
        "keywords": keywords
    })


@app_routes.route("/mods", methods=["GET"])
def mods():
    """Retrieve a list of all public mods available for download (in future, I'd like to add pagination)"""

    # Displays 3 most recently updated mods
    mods = db.execute("SELECT mods.id, title, updated, published, version, feature_img_url, users.username\
                                       FROM mods\
                                       JOIN users on users.id = mods.mod_author\
                                       WHERE is_draft = 0 AND is_private = 0\
                                       ORDER BY updated desc")

    return render_template("mods.html", mods=mods)


@app_routes.route("/mod/<mod_id>", methods=["GET"])
def mod(mod_id):
    """View a selected mod's full text and download; available to all users"""

    # If the user is not logged in, set a fake user_id for the purpose of the query
    if (session.get("user_id") is None):

         # Set a default user id that will not be found
        user_id = -1

    # Otherwise pull their real one
    else:
        user_id = session.get("user_id")

    # Grab information about the mod
    mod = db.execute("SELECT mods.id, title, description, download_url, feature_img_url, updated, published, version,\
                     is_private, is_draft, users.username, mod_author FROM mods\
                     JOIN users on users.id = mods.mod_author\
                     WHERE mods.id = ? AND ((is_private = 0 AND is_draft = 0) OR (mod_author = ?))",
                     mod_id, user_id)

    # Couldn't find it -- doesn't exist or may be unauthorized to view
    if len(mod) == 0:
        return handle_error("Mod not found", 404)

    return render_template("mod.html", mod=mod[0])


@app_routes.route("/mods/add", methods=["GET", "POST"])
@login_required
@admin_required
def mod_add():
    """Allows admins to create a new mod post"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Grab everything from the form
        title = request.form.get("title")
        description = request.form.get("description") or ""
        download_url = request.form.get("download_url")
        feature_img_url = request.form.get("feature_img_url") or ""
        is_private = request.form.get("is_private")
        is_draft = request.form.get("is_draft")

        # Check for title
        if not title:
            return handle_error("must provide mod title", 403)

        # Check for download_url
        elif not download_url:
            return handle_error("must provide mod download url", 403)

        # Check for is_private
        elif not is_private:
            return handle_error("must confirm whether mod is private or not", 403)

        # Check for is_draft
        elif not is_draft:
            return handle_error("must confirm whether mod is draft or not", 403)

        # Update draft and private to be integers instead of strings
        is_private = int(is_private)
        is_draft = int(is_draft)

        # Grab mod_author's user ID from session
        user_id = session["user_id"]

        # Grab current time as a unix timestamp
        now = time.time()

        # Add new mod to database
        db.execute("INSERT INTO mods (title, description, download_url, feature_img_url, updated,\
                    published, version, is_private, is_draft, mod_author)\
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", title, description, download_url,
                    feature_img_url, now, now, 1, is_private, is_draft, user_id )

        # Redirect user to index page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admin_add_mod.html")


@app_routes.route("/mod/edit/<mod_id>", methods=["GET", "PATCH", "DELETE"])
@login_required
@admin_required
def mod_edit(mod_id):
    """Retrieve, create, or update a specific mod, by database ID number"""

    # Grab mod_author's user ID from session to ensure they are editing their own mods only
    user_id = session["user_id"]

    # # User reached route via PUT (as by deleting something via an ajax request); returns JSON
    if request.method == "PATCH":

        # Grab everything from the form
        title = request.form.get("title")
        description = request.form.get("description") or ""
        download_url = request.form.get("download_url")
        feature_img_url = request.form.get("feature_img_url") or ""
        is_private = request.form.get("is_private")
        is_draft = request.form.get("is_draft")

        # Check for title
        if not title:
            return handle_error("must provide mod title", 403)

        # Check for download_url
        elif not download_url:
            return handle_error("must provide mod download url", 403)

        # Check for is_private
        elif not is_private:
            return handle_error("must confirm whether mod is private or not", 403)

        # Check for is_draft
        elif not is_draft:
            return handle_error("must confirm whether mod is draft or not", 403)

        # Update draft and private to be integers instead of strings
        is_private = int(is_private)
        is_draft = int(is_draft)

        # Grab mod_author's user ID from session
        user_id = session["user_id"]

        # Grab current time as a unix timestamp
        now = time.time()

        # Update database with new values
        num_updated = db.execute("UPDATE mods SET title = ?, description = ?, download_url = ?, feature_img_url = ?, updated = ?,\
                    version = version + 1, is_private = ?, is_draft = ?\
                    WHERE id = ? and mod_author = ?", 
                    title, description, download_url, feature_img_url, now, is_private, is_draft,
                    mod_id, user_id
        )

        # Check that this happened, and if it didn't indicate a potential failure
        if num_updated != 1:
            return jsonify("{\"error\": \"Update may not have occurred; most likely couldn't find the item or authenticate user"), 503

        # Otherwise return good status
        return jsonify("{\"status\":\"OK\"}"), 200

    # User reached route via DELETE (as by deleting something via an ajax request); returns JSON
    if request.method == "DELETE":

        # Delete the item
        num_deleted = db.execute("DELETE FROM mods WHERE id = ? AND mod_author = ?", mod_id, user_id)
        
        # If a single item not deleted, indicate there was a failure in returned response
        if num_deleted != 1:
            return jsonify("{\"error\": \"Deletion may not have occurred; most likely couldn't find the item or authenticate user"), 503

        # Otherwise return good status
        return jsonify("{\"status\":\"OK\"}"), 200

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Pull the details of this item to pre-populate the form-fields
        mod = db.execute("SELECT title, description, download_url, feature_img_url,\
                    is_private, is_draft FROM mods\
                    WHERE id = ? AND mod_author = ?",
                    mod_id, user_id)

        # Couldn't find it -- doesn't exist or may be unauthorized to view
        if len(mod) == 0:
            return handle_error("Mod not found", 404)
        
        # Convert empty optional fields to empty strings if unavailable
        if not mod[0]["description"]:
            mod[0]["description"] = ""
        if not mod[0]["feature_img_url"]:
            mod[0]["feature_img_url"] = ""

        return render_template("admin_edit_mod.html", context={ "mod": mod[0], "mod_id": mod_id })


@app_routes.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    """Show recently uploaded mods, tutorials, and other information for the current user that are editable"""

    # Grab mod_author's user ID from session
    user_id = session["user_id"]

    # Displays all of the user's published mods in order of most recently updated
    published_mods = db.execute("SELECT mods.id, title, updated, is_private, published, version, feature_img_url\
                                       FROM mods\
                                       WHERE is_draft = 0 AND mod_author = ?\
                                       ORDER BY updated desc", user_id)
    
    # Displays all of the user's draft mods in order of most recently updated
    draft_mods = db.execute("SELECT mods.id, title, updated, is_private, published, version, feature_img_url\
                                        FROM mods\
                                         WHERE is_draft = 1 AND mod_author = ?\
                                         ORDER BY updated desc", user_id)

    # Displays all of the user's published mods in order of most recently updated
    published_tutorials = db.execute("SELECT tutorials.id, title, updated, is_private, published, feature_img_url\
                                     FROM tutorials\
                                     WHERE is_draft = 0 AND tutorial_author = ?\
                                     ORDER BY updated desc", user_id)

    # Displays all of the user's draft mods in order of most recently updated
    draft_tutorials = db.execute("SELECT tutorials.id, title, updated, is_private, published, feature_img_url\
                                 FROM tutorials\
                                 WHERE is_draft = 1 AND tutorial_author = ?\
                                 ORDER BY updated desc", user_id)

    return render_template("admin_dash.html", context={ "published_mods": published_mods, "draft_mods": draft_mods, "published_tutorials": published_tutorials, "draft_tutorials": draft_tutorials })


@app_routes.route("/my-profile", methods=["GET"])
@login_required
@admin_required
def getUserProfile():
    """Display the profile for the currently logged in user. In the future, I'd like to make this a more general user endpoint
    and make it a public place to view mods posted by a specific user or change profile settings (like avatar, etc)."""

    # Grab mod_author's user ID from session
    user_id = session["user_id"]

    # Pull the user's profile information from the database
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Couldn't find it -- user doesn't exist or may be unauthorized to view
    if len(user) == 0:
        return handle_error("User not found", 404)

    return render_template("user.html", users=user)


@app_routes.route("/tutorials/add", methods=["GET", "POST"])
@login_required
@admin_required
def tutorials_add():
    """Allows admins to create a new tutorial post"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Grab everything from the form
        title = request.form.get("title")
        tutorial_text = request.form.get("tutorial_text")
        video_embed_url = request.form.get("video_embed_url") or ""
        feature_img_url = request.form.get("feature_img_url") or ""
        is_private = request.form.get("is_private")
        is_draft = request.form.get("is_draft")

        # Check for title
        if not title:
            return handle_error("must provide tutorial title", 403)

        # Check for tutorial text
        if not tutorial_text:
            return handle_error("must provide tutorial title", 403)

        # Check for is_private
        elif not is_private:
            return handle_error("must confirm whether tutorial is private or not", 403)

        # Check for is_draft
        elif not is_draft:
            return handle_error("must confirm whether tutorial is draft or not", 403)

        # Update draft and private to be integers instead of strings
        is_private = int(is_private)
        is_draft = int(is_draft)

        # Grab mod_author's user ID from session
        user_id = session["user_id"]

        # Grab current time as a unix timestamp
        now = time.time()

        # Add new mod to database
        db.execute("INSERT INTO tutorials (title, tutorial_text, video_embed_url, feature_img_url, updated,\
                    published, is_private, is_draft, tutorial_author)\
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", title, tutorial_text, video_embed_url,
                    feature_img_url, now, now, is_private, is_draft, user_id )

        # Redirect user to index page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admin_add_tutorial.html")


@app_routes.route("/tutorial/edit/<tutorial_id>", methods=["GET", "PATCH", "DELETE"])
@login_required
@admin_required
def tutorial_edit(tutorial_id):
    """Retrieve, create, or update a specific tutorial, by database ID number"""

    # Grab tutorial_author's user ID from session to ensure they are editing their own tutorials only
    user_id = session["user_id"]

    # # User reached route via PUT (as by deleting something via an ajax request); returns JSON
    if request.method == "PATCH":

        # Grab everything from the form
        title = request.form.get("title")
        tutorial_text = request.form.get("tutorial_text") or ""
        video_embed_url = request.form.get("video_embed_url")
        feature_img_url = request.form.get("feature_img_url") or ""
        is_private = request.form.get("is_private")
        is_draft = request.form.get("is_draft")

        # Check for title
        if not title:
            return handle_error("must provide tutorial title", 403)

        # Check for tutorial_text
        elif not tutorial_text:
            return handle_error("must provide tutorial text", 403)

        # Check for is_private
        elif not is_private:
            return handle_error("must confirm whether tutorial is private or not", 403)

        # Check for is_draft
        elif not is_draft:
            return handle_error("must confirm whether tutorial is draft or not", 403)

        # Update draft and private to be integers instead of strings
        is_private = int(is_private)
        is_draft = int(is_draft)

        # Grab tutorial_author's user ID from session
        user_id = session["user_id"]

        # Grab current time as a unix timestamp
        now = time.time()

        # Update database with new values
        num_updated = db.execute("UPDATE tutorials SET title = ?, tutorial_text = ?, video_embed_url = ?, feature_img_url = ?,\
                    updated = ?, is_private = ?, is_draft = ?\
                    WHERE id = ? and tutorial_author = ?", 
                    title, tutorial_text, video_embed_url, feature_img_url, now, is_private, is_draft,
                    tutorial_id, user_id)

        # Check that this happened, and if it didn't indicate a potential failure
        if num_updated != 1:
            return jsonify("{\"error\": \"Update may not have occurred; most likely couldn't find the item or authenticate user"), 503

        # Otherwise return good status
        return jsonify("{\"status\":\"OK\"}"), 200

    # User reached route via DELETE (as by deleting something via an ajax request); returns JSON
    if request.method == "DELETE":

        # Delete the item
        num_deleted = db.execute("DELETE FROM tutorials WHERE id = ? AND tutorial_author = ?", tutorial_id, user_id)
        
        # If a single item not deleted, indicate there was a failure in returned response
        if num_deleted != 1:
            return jsonify("{\"error\": \"Deletion may not have occurred; most likely couldn't find the item or authenticate user"), 503

        # Otherwise return good status
        return jsonify("{\"status\":\"OK\"}"), 200

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Pull the details of this item to pre-populate the form-fields
        tutorial = db.execute("SELECT title, tutorial_text, video_embed_url, feature_img_url,\
                    is_private, is_draft FROM tutorials\
                    WHERE id = ? AND tutorial_author = ?",
                    tutorial_id, user_id)

        # Couldn't find it -- doesn't exist or may be unauthorized to view
        if len(tutorial) == 0:
            return handle_error("tutorial not found", 404)
        
        # Convert empty optional fields to empty strings if unavailable
        if not tutorial[0]["tutorial_text"]:
            tutorial[0]["tutorial_text"] = ""
        if not tutorial[0]["feature_img_url"]:
            tutorial[0]["feature_img_url"] = ""

        return render_template("admin_edit_tutorial.html", context={ "tutorial": tutorial[0], "tutorial_id": tutorial_id })


@app_routes.route("/tutorial/<tutorial_id>", methods=["GET"])
def tutorial(tutorial_id):
    """View a selected tutorial's full text and download; available to all users"""

    # If the user is not logged in, set a fake user_id for the purpose of the query
    if (session.get("user_id") is None):

         # Set a default user id that will not be found
        user_id = -1

    # Otherwise pull their real one
    else:
        user_id = session.get("user_id")

    # Grab information about the tutorial
    tutorial = db.execute("SELECT tutorials.id, title, tutorial_text, video_embed_url, feature_img_url, updated, published,\
                          is_private, is_draft, users.username, tutorial_author FROM tutorials\
                          JOIN users on users.id = tutorials.tutorial_author\
                          WHERE tutorials.id = ? AND ((is_private = 0 AND is_draft = 0) OR (tutorial_author = ?))",
                          tutorial_id, user_id)

    # Couldn't find it -- doesn't exist or may be unauthorized to view
    if len(tutorial) == 0:
        return handle_error("Tutorial not found", 404)

    return render_template("tutorial.html", tutorial=tutorial[0])


@app_routes.route("/tutorials", methods=["GET"])
def tutorials():
    """Retrieve a list of all public tutorials available for download (in future, I'd like to add pagination)"""

    # Displays 3 most recently updated tutorials
    tutorials = db.execute("SELECT tutorials.id, title, updated, published, feature_img_url, users.username\
                           FROM tutorials\
                           JOIN users on users.id = tutorials.tutorial_author\
                           WHERE is_draft = 0 AND is_private = 0\
                           ORDER BY updated desc")

    return render_template("tutorials.html", tutorials=tutorials)