"""
This module parses XML gamelog files present in a directory
and creates a CSV file such that each XML log becomes a single
row in the csv file. 

Formats supported:
    1. Real numbers
        The parsed information is stored as reals. It is useful
        for learning algorthims that process numeric data.
"""

import os
from lxml import etree
import pprint
import sys
import random
import argparse
from datetime import datetime
from collections import defaultdict
import pandas as pd
from stu_name_corrections import get_correct_names_thomasville_harrell
from bayesnet_node_info import get_bayesnet_node_sequence


def get_pre_post_scores(csv_fn):
    """
    Header for file: data/prepost_ratio_geom_math_scores.csv contains
        student_name,premath,postmath,postmath_adjusted

    Things to note:
        premath => pre-test score
        postmath => post-test score
        postmath_adjusted => max(premath, postmath)
    """
    df = pd.read_csv(csv_fn, header=0)
    df_stu = df.set_index("student_name")

    return df_stu


def get_xml_files(src_dir):
    """
    Given a source directory, yield all XML file paths in the directory.
    """
    for rootdir, subdirs, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith('.xml'):
                yield os.path.join(rootdir, filename)


def get_stu_names_from_logs(src_dir):
    stu_names = set()
    track = defaultdict(set)
    for xml_path in get_xml_files(src_dir):
        # Parse XML
        # Get an iterable and turn it into an iterator
        context = iter(etree.iterparse(xml_path, events=("start",), encoding='UTF-8'))

        # Get the root element
        event, root = next(context)

        # Convert XML data into a dictionary.
        # This is again for maintaining the order.
        xml_dict = {elem.tag: elem.text for event, elem in context}

        # get correct student name
        stu_name = xml_dict["Name"]
        if stu_name is None:
            continue

        stu_name = stu_name.lower()
        stu_names.add(stu_name)
        track[stu_name[:3]].add(stu_name)

    #for name in sorted(list(stu_names)):
    #   print(name)
        
    for k, names in track.items():
        print()
        for n in names:
            print(f'         "{n}": "",')


def get_stu_name_level_from_xml(xml_path):
    #name_corrections = get_correct_names()
    name_corrections = get_correct_names_thomasville_harrell()

    # Parse XML
    # Get an iterable and turn it into an iterator
    context = iter(etree.iterparse(xml_path, events=("start",)))

    # Get the root element
    event, root = next(context)

    # Convert XML data into a dictionary.
    # This is again for maintaining the order.
    xml_dict = {elem.tag: elem.text for event, elem in context}


    # Get the correct student name.
    # For Thomasville Middle School, the names are stored as:
    #    LoganBaxterHarrell4
    stu_name = xml_dict["Name"]

    flag = 0
    try:
        stu_name = name_corrections[stu_name]
    except:
        flag = 1

    if flag:
        print("need to correct this name: ", stu_name)
        exit(0)

    level = xml_dict["Level"]

    return stu_name, level


def get_dict_from_xml(xml_path):
    # Parse XML
    # Get an iterable and turn it into an iterator
    context = iter(etree.iterparse(xml_path, events=("start",)))

    # Get the root element
    event, root = next(context)

    # Convert XML data into a dictionary.
    # This is again for maintaining the order.
    xml_dict = {elem.tag: elem.text for event, elem in context}

    return xml_dict


def collect_cases_from_game_logs(src_dir, prepost_score_fn):
    """
    Treat each XML file as a case.
    Args:
        src_dir: string
            Directory containing game logs (XML files)

        prepost_score_fn: string
            File containing pre/post test scores

        competency_update: string
            Competency variables are hidden and are not observed.
            We want to update some of them with pre/post scores
            so that the learning of bayesnet may converge.

            chrono:
                Users have pretest scores, then they play game levels
                and, finally, they have post test scores.
                Each game play is given a scale based on when the game
                was played.
                scale = i / n, where i is the chronological position of
                the game and n is the total number of games.
    """
    name_corrections = get_correct_names_thomasville_harrell()
    stu_scores = get_pre_post_scores(prepost_score_fn)

    # Get chronologically ordered list of game logs per student
    competency_update = "chrono"
    chron_order = order_levels_per_player_chronology(src_dir)

    # Keys to track the player and the game play event
    info_keys = ["student_name", "game_level", "game_time"]

    # Keys that correspond to the nodes in the Bayesian Network
    feature_keys = get_bayesnet_node_sequence()

    # Key to hold chronologically adjusted math score
    feature_keys += ["math"]

    # Keys to track the pre/post test scores
    #     postmath_adjusted => max(premath, postmath)
    score_keys = ["premath", "postmath_adjusted"]

    # Additional keys
    #     chronology_math => chronologically adjusted score
    extra_keys = ["chronology_math"]

    # Header of case csv file
    header_keys = info_keys + feature_keys + score_keys + extra_keys

    all_cases = [header_keys]

    for stu in chron_order:
        for entry in chron_order[stu]:
            # Unpack: alpha is the weight based on when the time the game was played
            time_units, level, xml_path, alpha = entry

            # Initialize all fields to empty strings
            hold_f = {fld: "" for fld in header_keys}
    
            # Parse XML
            xml_dict = get_dict_from_xml(xml_path)
    
            # Correct student name
            #stu_name = xml_dict["Name"].lower().strip()
            stu_name = xml_dict["Name"]
            if stu_name not in stu_scores:
                stu_name = name_corrections[stu_name]
    
            hold_f["student_name"] = stu_name
            hold_f["game_level"] = level
    
            # Extract time from XML path
            dt = "-".join(xml_path.split(".")[0].split("/")[-1].split("_")[-2:])
            hold_f["game_time"] = dt
            #time_units = [int(v) for v in dt.split("-")]
    
            # Extract pre/post test scores
            for scr_key in score_keys:
                hold_f[scr_key] = stu_scores.loc[stu_name][scr_key]
    
            # Extract observables with corrections
            skip = False
            for k in xml_dict:
                try:
                    if xml_dict[k] == "true":
                        hold_f[k] = "1"
                    elif xml_dict[k] == "false":
                        hold_f[k] = "0"
                    else:
                        hold_f[k] = xml_dict[k]
                except KeyError:
                    if k == "PercentLost":
                        hold_f["TotalLost"] = xml_dict[k]
                    else:
                        print(f"Unidentified Attribute {k} for XML file {xml_path}")
                        skip = True
    
            if skip:
                continue

            # Update selected competency variables based on the scheme
            if competency_update == "chrono":
                hold_f = update_competency_chronology(hold_f, alpha)
            else:
                pass

            # Add to the list of cases
            all_cases.append([hold_f[k] for k in header_keys])

    return all_cases


def order_levels_per_player_chronology(src_dir):
    ordering = defaultdict(list)
    alpha = .0
    for xml_path in get_xml_files(src_dir):
        try:
            # Extract date and time from filename
            dt = "-".join(xml_path.split(".")[0].split("/")[-1].split("_")[-2:])
            #print(dt)
            time_units = [int(v) for v in dt.split("-")]
        except:
            # Skip if any parsing error is encountered
            print("Time extraction error: ", xml_path)
            continue

        try:
            # Extract student name and the level name
            stu_name, level = get_stu_name_level_from_xml(xml_path)
            #print(stu_name, level)
        except KeyError:
            # Skip if any parsing error is encountered
            print("Name extraction error: ", xml_path)
            continue

        ordering[stu_name].append((time_units, level, xml_path, alpha))

    # Sort
    stu_names = ordering.keys()
    for stu in stu_names:
        ordering[stu] = sorted(ordering[stu], key=lambda x: datetime(*x[0]))
        for i in range(len(ordering[stu])):
            ordering[stu][i] = (ordering[stu][i][0], ordering[stu][i][1], ordering[stu][i][2], (i/len(ordering[stu])))

    return ordering


def update_competency_chronology(hold_f, alpha):
    """
    Given a dictionary of student observables, competencies, pre/post scores
    and a chronological scale, update the chronologically adjusted math score.
    """
    #stu_ratio = (1 - alpha) * float(hold_f["pre_ratio"]) + alpha * float(hold_f["post_ratio"])
    #stu_geom = (1 - alpha) * float(hold_f["pre_geom"]) + alpha * float(hold_f["post_geom"])
    stu_math = (1 - alpha) * float(hold_f["premath"]) + alpha * float(hold_f["postmath_adjusted"])

    hold_f["math"] = str(stu_math)
    hold_f["chronology_math"] = str(stu_math)

    return hold_f


def write_csv(data, out_f):
    with open(out_f, "w") as fp:
        for l in data:
            l = [str(v) for v in l]
            fp.write(",".join(l) + "\n")


def get_commandline_args():
    detail = "Parse XML gamelogs in a source directory and generate case file in csv format"
    parser = argparse.ArgumentParser(description=detail)

    parser.add_argument("src_dir",
        help="Source directory containing gamelogs",
    )
    parser.add_argument("prepost_csv",
        help="CSV file containing the pre/post test scores.",
    )
    parser.add_argument("out_real_csv",
        help="Output csv file with real data (numbers not categories)",
    )

    return parser.parse_args()


def main():
    cmd_args = get_commandline_args()

    src_dir = cmd_args.src_dir
    prepost_fn = cmd_args.prepost_csv
    out_real_f = cmd_args.out_real_csv

    cases = collect_cases_from_game_logs(src_dir, prepost_fn)


    print(f"Saving to:\n\t{out_real_f}\n")
    write_csv(cases, out_real_f)



if __name__ == "__main__":
    #src_dir = "from_peyman/Spring2017/dan_logfiles"
    #get_stu_names_from_logs(src_dir)
    main()
