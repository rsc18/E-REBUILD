from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify, make_response

from datetime import datetime
from erebuild.database_helpers import is_teacher
from erebuild.database_helpers import get_class_stats_for_teacher
import random


erebuild_admin_views = Blueprint("erebuild_admin_views", __name__)


@erebuild_admin_views.route('/assessment/admin')
def view_admin_page(user):
    # Query database for stats for the user
    return render_template("admin.html")

