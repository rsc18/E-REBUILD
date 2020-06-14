import pandas as pd
import sys


def transform_csv(in_csv, out_csv, to_rename, to_add, to_del, col_order):
    """
    """
    df = pd.read_csv(in_csv)
    n_row, n_col = df.shape

    # rename
    df = df.rename(columns=to_rename)

    # add
    for col, val in to_add:
        df.insert(n_col, col, val)

    # delete
    df.drop(to_del, inplace=True, axis=1)


    df = df[col_order]
    with open(out_csv, "w") as fp:
        fp.write(df.to_csv(index=False, header=False))


def transform_UserInfo():
    """
    CREATE TABLE UserInfo (
      user_email VARCHAR NOT NULL PRIMARY KEY,
      user_password VARCHAR NOT NULL,
      user_firstname TEXT,
      user_lastname TEXT,
      user_school TEXT,
      user_class TEXT,
      user_type INT NOT NULL);

    """
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    to_rename = {"email": "user_email",
            "lastname": "user_lastname",
            "firstname": "user_firstname",
            "class": "user_class",
            "password": "user_password",
            }
    to_add = [("user_type", 2), ("user_school", "fsu")]
    to_del = ["user_id", "levels_completed","badges_spent"]

    # Same order as in the db schema
    col_order = ["user_email", "user_password",
            "user_firstname", "user_lastname",
            "user_school", "user_class", "user_type"]

    transform_csv(in_csv, out_csv, to_rename, to_add, to_del, col_order)


if __name__ == "__main__":
    transform_UserInfo()
