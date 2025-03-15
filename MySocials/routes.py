"""
Non-authentication routes (i.e. home page, settings, etc.)
"""
from flask import Blueprint, render_template, redirect, url_for, request

main = Blueprint('main', __name__)

# HOME/EVENTS
@main.route("/")
@main.route("/index")
def index():
    return render_template("index.html")


# SETTINGS
@main.route("/settings")
def settings():
    return render_template("settings.html")


