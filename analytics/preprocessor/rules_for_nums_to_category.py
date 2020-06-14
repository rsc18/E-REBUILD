def translate_to_category(attr_val, attr_name, level):
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
             "default": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            },
        "posttest":
            {
             "post_math": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "a": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "post_ratio": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "b": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "post_geom":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "h":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "default": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            }
        }


    try:
        category = ranges[attr_name](attr_val)
    except TypeError:
        # Didn't encounter a callable. It was a dictionary.
        try:
            category = ranges[attr_name][level](attr_val)
        except KeyError:
            category = ranges[attr_name]["default"](attr_val)

    return category


if __name__ == "__main__":
    print(translate_to_category(75, "Angle", "my"))
    print(translate_to_category(75, "posttest", "my"))
    print(translate_to_category(100, "NumBlocks", "43Stadium1"))
    print(translate_to_category(100, "NumBlocks", "m"))
