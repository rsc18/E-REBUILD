import os
BASE_DIR = os.getcwd()
import sys
sys.path.append(BASE_DIR)

from datetime import datetime
import subprocess
import argparse

from preprocessor.logs_to_csv import gen_cases_from_game_logs
from preprocessor.reals_to_categorical import convert_reals_to_categorical
from preprocessor.train_test_split import run_split
from preprocessor.categorical_to_netica_case_format import convert_to_netica_case

def write_csv(data, out_f):
    with open(out_f, "w") as fp:
        for l in data:
            fp.write(",".join(l) + "\n")


def get_commandline_args():
    detail = "Parse XML gamelogs in a source directory and generate case file in csv format"
    parser = argparse.ArgumentParser(description=detail)

    parser.add_argument("-src",
        "--src_dir",
        help="Source directory containing gamelogs"
    )

    parser.add_argument("comp_scheme",
        choices=set(["all", "top3", "rand", "none"]),
        help="Scheme to update competency vars"
    )

    return parser.parse_args()


def main():
    cmd_args = get_commandline_args()

    src_dir = cmd_args.src_dir
    comp_scheme = cmd_args.comp_scheme

    fname_tag = f"{datetime.now():%b_%d_%y}_{comp_scheme}"

    # File names
    case_csv = f"data/cases_{fname_tag}.csv"

    # convert_reals_to_categorical() creates the following files
    category_csv = f"data/categorical_cases_{fname_tag}.csv"
    stu_names_csv = f"level_student_names_cases_{fname_tag}.csv"

    if src_dir is None:
        src_dir = "from_peyman/FallSpring16-17"

    print()
    print(f"(1) Generating cases from logs")
    cases = gen_cases_from_game_logs(src_dir, comp_scheme)

    print(f"(2) Saving cases:\n\t{case_csv}\n")
    write_csv(cases, case_csv)

    print("(3) Converting real values in case files to categories:")
    convert_reals_to_categorical(case_csv, category_csv, stu_names_csv)

    print("(4) Splitting into train and test. Produced:")
    split_type = "stu_split"
    run_split(category_csv, stu_names_csv, split_type)
    tr_f = f"data/tr_{fname_tag}_{split_type}.csv"
    te_f = f"data/te_{fname_tag}_{split_type}.csv"
    print(f"\t1. {tr_f}\n\t2. {te_f}")

    # generate netica format files
    print(f"(5) Creating Netica format files")
    convert_to_netica_case(tr_f)
    convert_to_netica_case(te_f)
    print()

if __name__ == "__main__":
    main()
