from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify, make_response

from datetime import datetime
from erebuild.database_helpers import insert_login_info
from erebuild.database_helpers import get_class_stats_for_teacher
from erebuild.database_helpers import get_user_stats
from erebuild.database_helpers import is_valid_registration_code
from erebuild.database_helpers import is_already_registered
from erebuild.database_helpers import get_active_registration_codes
from erebuild.database_helpers import remove_registration_code
from erebuild.database_helpers import insert_registration_code
from erebuild.database_helpers import get_class_names
from erebuild.database_helpers import drop_user
from erebuild.database_helpers import get_student_info_under_teacher

import secrets

erebuild_registration = Blueprint("erebuild_registration", __name__)


@erebuild_registration.route('/assessment/teacher/new/<randstr>')
def view_teacher_registration(randstr):
    # Check if randstr has expired
    if not is_valid_registration_code(randstr):
        message = f"Invalid registration link."
        return render_template("feedback.html", feedback=message)

    return render_template("registration_user.html", validcode=randstr)


@erebuild_registration.route('/assessment/user/new', methods=['POST'])
def register_new_user():
    # Extract form data as a dictionary
    user_info = request.form.to_dict(flat=True)

    register_code = user_info.get("register_code", None)

    if register_code is not None:
        # Check if the registration code has already expired or is invalid.
        # If valid, remove it from the database and proceed to register.
        if not is_valid_registration_code(register_code):
            message = f"Invalid registration link."
            return render_template("feedback.html", feedback=message)
        else:
            remove_registration_code(register_code)

        # user_type = "teacher"
        user_info["user_type"] = 1
    else:
        # user_type = "user"
        user_info["user_type"] = 2

    #print(user_info)
    # Check if Teacher already exists
    if is_already_registered(user_info["user_email"]):
        feedback = f"{user_info['user_email']} is already registered as a User."
        return render_template("feedback.html", feedback=feedback)

    # Update database with new user info
    insert_login_info(user_info)

    feedback = f"{user_info['user_email']} is now registered as a {user_info['user_type']}."
    return render_template("feedback.html", feedback=feedback)


@erebuild_registration.route('/assessment/user/new')
def view_user_registration():
    return render_template("registration_user.html", validcode=None)


@erebuild_registration.route('/assessment/active_registrations')
def show_teacher_registration_urls():
    if session["is_superuser"] and session["logged_in"]:
        base = "/".join(request.base_url.split("/")[:-1])
        active_codes = get_active_registration_codes()
        active_urls = [f"{base}/teacher/new/{code}" for code in active_codes]
        return render_template("active_registrations.html", active_urls=active_urls)
    else:
        return redirect(url_for("erebuild_land.landing_page"))


@erebuild_registration.route('/assessment/bulk/new', methods=['POST'])
def register_users_in_bulk():
    if session["is_teacher"] and session["logged_in"]:
        # Extract the student registration info from json payload
        bulk_info = request.get_json()
        reg_status = dict()
        for stu_info in bulk_info:
            # Update current registration info with school and class info.
            stu_info = {**stu_info, 
                "user_school": session["user_school"],
                "user_class": session["user_class"],
                "user_type": 2
                }

            if is_already_registered(stu_info["user_email"]):
                reg_status[stu_info["user_email"]] = "pre-exists"
            else:
                try:
                    insert_login_info(stu_info)
                    reg_status[stu_info["user_email"]] = "success"
                except:
                    reg_status[stu_info["user_email"]] = "error"

        response = jsonify(reg_status)
    else:
        response = jsonify({"": ""})


    return response
    


@erebuild_registration.route('/assessment/active_registrations/new')
def create_teacher_registration_code():
    #print(session.keys())
    if session["is_superuser"] and session["logged_in"]:
        # Create a random string
        rand_code = secrets.token_urlsafe(16)

        # Insert to db
        insert_registration_code(rand_code)

        return redirect(url_for("erebuild_registration.show_teacher_registration_urls"))

    else:
        return redirect(url_for("erebuild_land.landing_page"))


@erebuild_registration.route('/assessment/current_schools', methods=['POST'])
def get_current_schools():
    """
    Return a json with current school names.
    """
    return jsonify(get_class_names())


@erebuild_registration.route('/assessment/current_students', methods=['POST'])
def get_current_students():
    """
    Return a json with student info for the logged in teacher
    """
    if session["is_teacher"] and session["logged_in"]:
        stu_info = get_student_info_under_teacher(session["user_email"])

        return jsonify(stu_info)

    return jsonify({"": ""})

@erebuild_registration.route('/assessment/to_drop', methods=['POST'])
def drop_students():
    """
    Remove students from the user info database.
    """
    if session["is_teacher"] and session["logged_in"]:
        stu_emails_to_drop = request.get_json()
        for user_email in stu_emails_to_drop:
            drop_user(user_email)

        return "success"

    return "error"

