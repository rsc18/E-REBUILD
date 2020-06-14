from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify, make_response

from datetime import datetime
from erebuild.database_helpers import get_class_stats_for_teacher
from erebuild.database_helpers import get_user_stats, get_latest_user_competency
from erebuild.stealth_helpers import prepare_json_for_trajectory_plot
from erebuild.stealth_helpers import load_partial_learning_trajectory
from erebuild.stealth_helpers import insert_competency_into_trajectory

import random
import json

erebuild_display_stats = Blueprint("erebuild_display_stats", __name__)


@erebuild_display_stats.route('/assessment/stats')
def view_user_stats():
    if not session["logged_in"]:
        print("Not logged in")
        return render_template("404.html")

    # Query database for stats for the user
    data = get_user_stats(session["user_email"])

    return render_template("user_stats.html", user=session["user_email"], data=data)


@erebuild_display_stats.route('/assessment/stats_json', methods=['POST'])
def get_trajectory_graph():
    #if not session["logged_in"]:
    #    print("Not logged in")
    #    return render_template("404.html")

    print("Extract data from ajax")
    user_info = request.get_json()
    print("Extracted data from ajax", user_info)

    uname = user_info["userid"]

    # Query database for stats for the user
    #data = get_user_stats(uname)
    data = get_latest_user_competency(uname)

    # Partial learning trajectory
    trj_part = load_partial_learning_trajectory()

    # Populate the partial learning trajectory with competency data
    unlocked_nodes = []
    trj = insert_competency_into_trajectory(trj_part, data, unlocked_nodes)

    #print(trj)
    return trj


@erebuild_display_stats.route('/assessment/class')
def view_class_stats_for_teacher():
    # In case the URL end point is reached before login
    if not (session["logged_in"] and session["is_teacher"]):
        return render_template("404.html")

    # Extract class information for the teacher
    # Returns:
    #     stu_info: dictionary with user_email and user_firstname
    #     class_data: dictionary with competency data for each student
    stu_info, class_data = get_class_stats_for_teacher(session["user_email"])
    print(stu_info)
    print(class_data)

    # Read and display class stats for the teacher
    return render_template("class_data.html", teacher=session["user_email"], stu_info=stu_info, class_data=class_data)


@erebuild_display_stats.route('/assessment/test')
def view_learning_trajectory():
    return render_template("user_learning_trajectory.html")

@erebuild_display_stats.route('/assessment/testd3')
def view_test_d3():
    return render_template("test_d3_basic.html")
    #return render_template("test_d3.html")
    #return render_template("test_d3_tree.html")
    #return render_template("test_svg.html")
    #return render_template("bar_chart.html")
    #return render_template("test_d3_graph_with_rect_nodes.html")
