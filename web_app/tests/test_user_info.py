import os
import sys
sys.path.append(os.getcwd())

from erebuild.database_helpers import insert_login_info, verify_user_login, drop_user


def test_user_info():
    email = "sishya@sishya"
    password = "sishya"
    u_type = 2
    u_school = "fsu"
    u_class = "eme5078"
    u_first = u_last = "sishya"

    # First, drop this user if it already exists.
    drop_user(email)

    user_info = {"user_email": email,
        "user_password": password,
        "user_firstname": u_first,
        "user_lastname": u_last,
        "user_school": u_school,
        "user_class": u_class,
        "user_type": u_type
        }

    insert_login_info(user_info)

    status = verify_user_login(email, password)

    assert status["is_user"]
    assert status["user_school"] == u_school
    assert status["user_class"] == u_class
    assert not status["is_superuser"]


if __name__ == "__main__":
    test_user_info()

    
