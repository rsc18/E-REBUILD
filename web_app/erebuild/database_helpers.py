# Import SQLAlchemy database defined in erebuild/__init__.py
from erebuild import E_DB
from erebuild.database_models import UserGameLogs
from erebuild.database_models import UserCompetency
from erebuild.database_models import UserInfo
from erebuild.database_models import TeacherRegistrationCodes
from erebuild.database_models import LatestBayesNet
import json
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from collections import defaultdict
import sqlalchemy

def rename_to_db_keys(obs):
    """
    In case there's a discrepancy between the keys sent over
    from Unity and the database column names, normalize then names
    before inserting into the database.
    """
    map_db_schema = {"Angle": "angle",
                 "LevelComplete": "level_complete",
                 "MaterialCredits": "materials_credits",
                 "Time": "time",
                 "BuildingComplete": "building_complete",
                 "NumBlocks": "num_blocks",
                 "NumTrades": "num_trades",
                 "AssignmentComplete": "assignment_complete",
                 "Distance": "distance",
                 "NumAssignments": "num_assignments",
                 "NumFailedAssignments": "num_failed_assignments",
                 "NumFamilyCollected": "num_fam_collected",
                 "NumWrong": "num_wrong",
                 "Size": "size",
                }

    renamed = {map_db_schema[k]:obs[k] for k in obs}

    return renamed


def insert_observables(user_email, level_id, observables):
    #obs = rename_to_db_keys(observables)
    play_info = {"user_email": user_email, "level_id": level_id}
    tbl_entry = UserGameLogs(**{**play_info, **observables})
    E_DB.session.add(tbl_entry)
    E_DB.session.commit()


def insert_competencies(user_email, level_id, dtime, comp):
    # jsonify dictionary of competencies
    comp = json.dumps(comp)

    # prep entry for table
    user_info = {"user_email": user_email, "level_id": level_id, "play_time": dtime}
    tbl_entry = UserCompetency(**user_info, competency=comp)

    E_DB.session.add(tbl_entry)
    E_DB.session.commit()


def get_latest_user_competency(user_email):
    """
    Return last recorded math competency of the student.
    """
    try:
        row = UserCompetency.query.filter_by(user_email=user_email).order_by(UserCompetency.play_time.desc()).limit(1).all()[0]
        comp = json.loads(row.competency)
    # There's no entry for the user.
    except IndexError:
        comp = dict()

    return comp


def insert_login_info(user_info):
    # Get the column names from the table
    column_names = UserInfo.__table__.columns.keys()

    #print(user_info)
    # Filter out user info keys which don't correspond to the column names
    user_info = {k: v for k, v in user_info.items() if k in column_names}
    print("Inserting login info: ", user_info)

    # Hash the password
    user_info["user_password"] = generate_password_hash(user_info["user_password"])

    tbl_entry = UserInfo(**user_info)

    E_DB.session.add(tbl_entry)
    E_DB.session.commit()


def get_active_registration_codes():
    codes = [row.code for row in TeacherRegistrationCodes.query.all()]
    return codes


def drop_user(user_email):
    entry = UserInfo.query.filter_by(user_email=user_email).first()
    E_DB.session.delete(entry)
    E_DB.session.commit()


def remove_registration_code(reg_code):
    entry = TeacherRegistrationCodes.query.filter_by(code=reg_code).first()
    E_DB.session.delete(entry)
    E_DB.session.commit()


def insert_registration_code(reg_code):
    entry = TeacherRegistrationCodes(code=reg_code)
    E_DB.session.add(entry)
    E_DB.session.commit()


def verify_user_login(user_email, password):
    user = UserInfo.query.filter_by(user_email=user_email).first()

    status = {"valid": False, "is_teacher": False,
              "is_superuser": False, "is_user": False,
              "id": -1, "user_email": None, "user_school": None,
              "user_class": None
             }

    if user is not None:
        #print(user.user_password, user.user_email)
        #hashed_pass = generate_password_hash(password)
        if check_password_hash(user.user_password, password):
            status["valid"] = True
            status["is_teacher"] = user.user_type == 1
            status["is_superuser"] = user.user_type == 0
            status["is_user"] = user.user_type == 2
            status["id"] = user.id
            status["user_email"] = user.user_email
            status["user_school"] = user.user_school
            status["user_class"] = user.user_class

    return status


def verify_oauth_login(email_id):
    user = UserInfo.query.filter_by(user_email=email_id).first()
    status = {"valid": False, "teacher": False, "superuser": False, "user": False}

    if user is not None:
        status["valid"] = True
        status["teacher"] = user.is_teacher
        status["superuser"] = user.is_superuser
        status["user"] = user.is_user

    return status


def is_already_registered(email_id):
    try:
        user = UserInfo.query.filter_by(user_email=email_id).one()
        return True
    except sqlalchemy.orm.exc.NoResultFound:
        return False


def get_class_stats_for_teacher(teacher):
    # get class id of the teacher
    tchr = UserInfo.query.filter_by(user_email=teacher).first()
    tchr_class = tchr.user_class

    # Get all the students in the same class
    class_stu_ids = {row.user_email: row.user_firstname for row in UserInfo.query.filter_by(user_class=tchr_class).all()
                     if row.user_type == 2
                    }

    print(class_stu_ids)

    # Extract competency for each student
    stu_comp = {stu_email:row.competency for stu_email in class_stu_ids
                for row in UserCompetency.query.filter_by(user_email=stu_email).all()}

    return class_stu_ids, stu_comp


def get_student_info_under_teacher(teacher_email):
    """
    """
    # get class id of the teacher
    tchr = UserInfo.query.filter_by(user_email=teacher_email).first()
    tchr_class = tchr.user_class

    # Get all the students in the same class
    stu_info = {row.user_email: [row.user_firstname, row.user_lastname]
            for row in UserInfo.query.filter_by(user_class=tchr_class).all()
            if row.user_type == 2}

    return stu_info


def get_class_names():
    """
    Return all schools and their class names that exist.
    """
    class_names = defaultdict(set)
    for row in UserInfo.query.all():
        if row is not None:
            class_names[row.user_school].add(row.user_class)

    class_names = {k: sorted(v) for k, v in class_names.items()}

    return class_names


def get_teacher_class_names(teacher_email):
    """
    Return class names for a teacher.
    """
    class_ids = set([row.user_class for row in UserInfo.query.all() if row.user_email == teacher_email])

    return class_ids


def get_user_stats(user_email):
    """
    Return math competency of the student per game level.
    """
    data = [(row.level_id, row.competency) for row in UserCompetency.query.filter_by(user_email=user_email).all()]
    data = {i:tup for i, tup in enumerate(data)}
    return data


def is_valid_registration_code(randstr):
    """
    Check if the randstr is valid.
    Validity has two aspects:
        1. Is it in the database?
        2. Has it expired?
    """
    code = TeacherRegistrationCodes.query.filter_by(code=randstr).first()
    if code is not None:
        return True
    else:
        return False

