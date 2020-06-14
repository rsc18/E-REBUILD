from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify

from flask_oauthlib.client import OAuth
from erebuild.database_helpers import verify_user_login
from erebuild.database_helpers import verify_oauth_login

erebuild_oauth_login = Blueprint("erebuild_oauth_login", __name__)


# Globals for handling oauth
OAUTH_OBJECT = None
OAUTH_NAME = None
OAUTH_TOKEN_KEY_NAME = None
OAUTH_USERINFO_KEY = None

def set_oauth_service(client):
    """
        Interface to resolve OAuth service related dependicies
    """
    global OAUTH_OBJECT
    global OAUTH_NAME
    global get_oauth_token
    global OAUTH_TOKEN_KEY_NAME
    global OAUTH_USERINFO_KEY

    which_oauth = {
                   "google": get_google_oauth
                  }

    oauth_token_key_names = {
                             "google": "access_token"
                            }

    keys_for_user_info = {
                          "google": "userinfo"
                         }
    OAUTH_NAME = client
    OAUTH_OBJECT = which_oauth[client]()
    OAUTH_TOKEN_KEY_NAME = oauth_token_key_names[client]
    OAUTH_USERINFO_KEY = keys_for_user_info[client]

    # Explicit decoration
    get_oauth_token = OAUTH_OBJECT.tokengetter(get_oauth_token)


def get_oauth_token():
    return session.get("session_oauth_token")


def get_google_oauth():
    oauth = OAuth(erebuild_oauth_login)
    google = oauth.remote_app(
        'google',
        consumer_key="955373043902-jrnlv14mvmve1q9mbpm792qh4cuia26q.apps.googleusercontent.com",
        consumer_secret="X25E0aeGgjZlJVC8FwMMIptI",
        request_token_params={
            'scope': 'email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

    return google


@erebuild_oauth_login.route('/assessment/oauth', methods=['POST'])
def login():
    return redirect(url_for("erebuild_land.landing_page"))

    # Assume we are going to use google for now
    auth_client = "google"
    set_oauth_service(auth_client)

    return OAUTH_OBJECT.authorize(callback=url_for('erebuild_oauth_login.authorized', _external=True))
    #return OAUTH_OBJECT.authorize(callback=url_for('erebuild_oauth.authorized',
    #                                               next=request.referrer,
    #                                               _external=True))


@erebuild_oauth_login.route('/assessment/authorized')
def authorized():
    return redirect(url_for("erebuild_land.landing_page"))

    resp = OAUTH_OBJECT.authorized_response()
    if resp is None:
        return redirect(url_for("/"))

    session['session_oauth_token'] = (resp[OAUTH_TOKEN_KEY_NAME], '')
    me = OAUTH_OBJECT.get(OAUTH_USERINFO_KEY)
    uname = me.data["email"]

    user_status = verify_oauth_login(uname)

    # Track user's session
    session["logged_in"] = False
    session["user_email"] = None
    session["is_teacher"] = False
    session["is_user"] = False
    session["is_superuser"] = False

    if user_status["valid"]:
        session["logged_in"] = True
        session["user_email"] = uname
        if user_status["superuser"]:
            session["is_superuser"] = True
            #return redirect(url_for("erebuild_registration.create_teacher_registration"))
        elif user_status["teacher"]:
            session["is_teacher"] = True
            #return redirect(url_for("erebuild_display_stats.view_class_stats_for_teacher"))
        else:
            session["is_user"] = True
            #return redirect(url_for("erebuild_display_stats.view_user_stats"))
        return redirect(url_for("erebuild_land.landing_page"))
    else:
        # Redirect to homepage
        return redirect(url_for("erebuild_land.landing_page"))


@erebuild_oauth_login.route('/assessment/login', methods=['POST', 'GET'])
def login_with_erebuild_cred():
    """
    Update session to keep track of login status. The keys are:
    """
    if request.method == "GET":
        return redirect(url_for("erebuild_land.landing_page"))

    # Extract the data from the request.
    # It can be sent either as a form or as json.
    login_info = request.form.to_dict(flat=True)
    if len(login_info) == 0:
        login_info = request.get_json()

    user_email = login_info["user_email"]
    user_password = login_info["user_password"]
    unity3d_request = login_info.get("request_type", None)

    # Session keys to track user's session
    session["logged_in"] = False
    session["user_email"] = None
    session["user_school"] = None
    session["user_class"] = None
    session["is_teacher"] = False
    session["is_user"] = False
    session["is_superuser"] = False

    # update the session with the user status
    user_status = verify_user_login(user_email, user_password)
    for k in user_status:
        if k in session:
            session[k] = user_status[k]

    if unity3d_request is not None:
        response = jsonify(user_status)
    else:
        if user_status["valid"]:
            session["logged_in"] = True
            response = redirect(url_for("erebuild_land.landing_page"))

        else:
            # Redirect to homepage
            message = f"Login was not successful"
            response = render_template("feedback.html", feedback=message)

    return response


@erebuild_oauth_login.route('/assessment/logout')
def logout():
    session["logged_in"] = False
    session["user_email"] = None
    session["user_school"] = None
    session["user_class"] = None
    session["is_teacher"] = False
    session["is_user"] = False
    session["is_superuser"] = False

    return redirect(url_for("erebuild_land.landing_page"))

