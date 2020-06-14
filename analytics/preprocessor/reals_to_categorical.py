""" Convert a case file containing real numbers to categorical """

import os
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys


def get_category_range():
    """
    Return manually verified ranges that make data categorical for each observable.

    These ranges are obtained from Peyman's case-gen code and histograms for each observable.
    """
    ranges = {
        "Angle": lambda x: 3 if x < 11.25 else 2 if 11.25 <= x < 33.75 else 1,
        "AssignmentComplete": lambda x: 3 if x == 1 else 1,
        "BuildingComplete": lambda x: 3 if x == 1 else 1,
        "Distance": lambda x: 3 if x < 5 else 2 if 5 <= x < 15 else 1,
        "LevelComplete": lambda x: 3 if x == 1 else 1,
        "MaterialsCredits": lambda x: 3 if x > 8000 else 2 if 2000 <= x <= 8000 else 1,
        "NumAssignments": lambda x: 3 if x <= 15 else 2 if 15 < x <= 22 else 1,
        "NumBlocks": 
            {"43Stadium1": lambda x: 3 if 93.75 <= x < 106.25 else 2 if (106.25 <= x < 118.75) or (81.25 <= x < 93.75) else 1,
             "Stadium2": lambda x: 3 if 187.5 <= x < 212.5 else 2 if (212.5 <= x < 237.5) or (162.5 <= x < 187.5) else 1,
             "IslandBuild01": lambda x: 3 if x <= 5 else 1,
             "IslandBuild02": lambda x: 3 if x <= 5 else 1,
             "IslandBuild03": lambda x: 3 if x <= 5 else 1,
             "SchoolBuild": lambda x: 3 if x <= 5 else 1,
             "default": lambda x: 3 if x <= 5 else 1,
            },
        "NumFailedAssignments": lambda x: 3 if x <= 2 else 2 if 2 < x <= 4 else 1,
        "NumFamilyCollected": lambda x: 3 if x <= 2 else 2 if 2 < x <= 4 else 1,
        "NumTrades": lambda x: 3 if x <= 2 else 2 if 2 < x < 5 else 1,
        "NumWrong": lambda x: 3 if x <= 1 else 2 if 1 < x < 3 else 1,
        "Size": lambda x: 3 if x < 10 else 2 if 10 <= x < 20 else 1,
        "Time": lambda x: 3 if x < 200 else 2 if 200 <= x < 500 else 1,
        "TotalLost": lambda x: 3 if x > -10 else 2 if -150 <= x < -10 else 1,
        "pretest":
            {"pre_math": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "pre_ratio": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "pre_geom":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "defaut": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            }
        }

    return ranges


def convert_reals_to_categorical(in_csv, out_csv, out_stu_name_csv):
    """
    Empty fields are left as is.
    """
    categorize_funcs = get_category_range()

    # Read the variable names
    # Last 2 columns hold level names and student names. Exclude both.
    with open(in_csv) as fp:
        var_names = fp.readline().strip("\n").split(",")[:-2]

    competency_vars = 'abcdefghijklmnopqrstuv'

    use_cols = tuple(i for i in range(len(var_names)))

    # Load all cases
    cases = np.genfromtxt(in_csv, delimiter=",", skip_header=1, usecols=use_cols)

    # Row-wise level names by excluding the header
    level_stu_names = [l.split(",")[-2:] for l in open(in_csv).read().split("\n")[1:-1]]


    # Array to hold evaluated categories
    hold_categories= np.zeros(cases.shape, dtype=np.int8)

    for col, var_name in enumerate(var_names):
        # Choose function to categorize
        cat_func = None
        if var_name not in categorize_funcs:
            # Variables not present as observables can be competency vars
            if var_name in competency_vars:
                if var_name == "a":
                    cat_func = categorize_funcs["pretest"]["pre_math"]
                elif var_name in "bcdefg":
                    cat_func = categorize_funcs["pretest"]["pre_ratio"]
                elif var_name in "hijklmnopqrstuv":
                    cat_func = categorize_funcs["pretest"]["pre_geom"]
                else:
                    cat_func = categorize_funcs["pretest"]["default"]
            else:
                continue
        else:
            cat_func = categorize_funcs[var_name]

        for row, val in enumerate(cases[:, col:col+1]):
            # Get category
            if np.isnan(val):
                category = 0
            else:
                if not callable(cat_func):
                    level = level_stu_names[row][0]
                    try:
                        cat_func = categorize_funcs[var_name][level]
                    except KeyError:
                        cat_func = categorize_funcs[var_name]["default"]

                category = cat_func(val)

            # Update category
            #print(row, col)
            hold_categories[row, col] = category

    # Write to file
    out_fp = open(out_csv, "wb")
    out_fp.write(b",".join([v.encode() for v in var_names]) + b"\n")
    #out_fp.write(b",".join(var_names) + b"\n")
    np.savetxt(out_fp, hold_categories, delimiter=",", fmt="%i")

    # Write the corresponding level and student names
    with open(out_stu_name_csv, "w") as fp:
        fp.write(f"level,student\n")
        for lvl, stu in level_stu_names:
            fp.write(f"{lvl},{stu}\n")


if __name__ == "__main__":
    in_csv = "data/cases_FallSpring16-17.csv"
    in_csv = sys.argv[1]
    convert_reals_to_categorical(in_csv)
