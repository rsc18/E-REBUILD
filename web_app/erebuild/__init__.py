from flask import Flask, render_template, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime
import logging
import socket


# If mileresearch.coe.fsu.edu, we want to access from
# "assessment" subdirectory.
if socket.gethostname() == "COE-EPLS-APPS2":
    root_path = ""
else:
    root_path = "/"

app = Flask(__name__)  #, root_path=root_path)

# Load other configs
app.config.from_object("config")

# Define the database object which is imported
# by modules and controllers
E_DB = SQLAlchemy(app)

# If the tables in the database are not created, run the folowing:
#     >>> from erebuild import E_DB
#     >>> E_DB.create_all()


from .views import erebuild_land
from .oauth_login import erebuild_oauth_login
from .stealth_assessment import erebuild_stealth
from .display_stats_views import erebuild_display_stats
from .registration_views import erebuild_registration

## Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_500(error):
    return render_template('500.html', message=error), 500

@app.before_request
def before_request():
    """ Expire after 20 minutes of inactivity """
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    session.modified = True

    #return "Ok"
    #return redirect(url_for("erebuild_land.landing_page"))
    #message = "Session timed out."
    #return render_template("index.html")

app.register_blueprint(erebuild_land)
app.register_blueprint(erebuild_oauth_login)
app.register_blueprint(erebuild_stealth)
app.register_blueprint(erebuild_display_stats)
app.register_blueprint(erebuild_registration)


logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('access.log')
logger.addHandler(handler)

# Also add the handler to Flask's logger for cases
#  where Werkzeug isn't used as the underlying WSGI server.
app.logger.addHandler(handler)
