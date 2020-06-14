def get_pre_post_scores():
    # Function to categorize the scores.
    # Same for pretest as in reals_to_categorical.py
    categorizer = {"pre_math": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "pre_ratio": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "pre_geom":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "defaut": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            }

    # data source
    fname = "data/prepost_ratio_geom_math_scores.csv"

    # Discard comments. Read header and score lines
    num_comments = 0
    with open(fname) as fp:
        comment = [fp.readline() for i in range(num_comments)]
        header = fp.readline().strip().split(",")
        lines = fp.read().split("\n")[:-1]

    scores = dict()
    for line in lines:
        name, pre_ratio, pre_geom, pre_math, post_ratio, post_geom, post_math = line.split(",")

        scores[name] = {"post_ratio": (categorizer["pre_ratio"](float(post_ratio)), float(post_ratio)),
                        "post_geom": (categorizer["pre_geom"](float(post_geom)), float(post_geom)),
                        "post_math": (categorizer["pre_math"](float(post_math)), float(post_math)),
                        "pre_ratio": (categorizer["pre_ratio"](float(pre_ratio)), float(pre_ratio)),
                        "pre_geom": (categorizer["pre_geom"](float(pre_geom)), float(pre_geom)),
                        "pre_math": (categorizer["pre_math"](float(pre_math)), float(pre_math)),
                       }

    return scores

