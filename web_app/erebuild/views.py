from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify

import os
BASE_DIR = os.getcwd()


erebuild_land = Blueprint("erebuild_land", __name__)


@erebuild_land.route('/assessment/')
def landing_page(message=None):
    return render_template("index.html")

# Static files
@erebuild_land.route("/assessment/css/<path:filename>")
def custom_static_css(filename):
    return send_from_directory(os.path.join(BASE_DIR, "erebuild", "static", "css"), filename)


@erebuild_land.route("/assessment/js/<path:filename>")
def custom_static_js(filename):
    return send_from_directory(os.path.join(BASE_DIR, "erebuild", "static", "js"), filename)

