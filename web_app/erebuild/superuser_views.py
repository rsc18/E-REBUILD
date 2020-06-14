from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_from_directory, jsonify, make_response

from datetime import datetime
from erebuild.database_helpers import insert_login_info
from erebuild.database_helpers import get_class_stats_for_teacher
from erebuild.database_helpers import get_user_stats
from erebuild.database_helpers import is_valid_registration_code
from erebuild.database_helpers import is_already_registered
from erebuild.database_helpers import get_active_registration_codes
from erebuild.database_helpers import get_class_names

erebuild_superuser = Blueprint("erebuild_superuser", __name__)


