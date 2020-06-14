import random
import numpy as np
from sklearn.utils import shuffle as sklearn_shuffle
import sys
import re

def load_cases(fname):
    """
    Load cases from a categorical file. While doing that:
        1. Convert integer categories to symbols.
        2. Add IDnum for each case.
    """
    mapping = {0: None, 1: "l", 2: "m", 3: "h"}
    with open(fname) as fp:
        var_names = fp.readline().strip("\n").split(",")

    # Add IDnum to header
    var_names = ["IDnum"] + var_names

    cases = []
    for i, case in enumerate(np.loadtxt(fname, delimiter=",", skiprows=1, dtype=np.int8)):
        d = [str(i + 1)] + [str(val) for val in case]
        cases.append(d)

    return var_names, cases


def split_into_train_test(cases, stu_names):
    """
    70 % for training.
    """
    cases, stu_names = sklearn_shuffle(cases, stu_names)

    splt = int(0.7 * len(cases)) + 1

    return cases[:splt], stu_names[:splt], cases[splt:], stu_names[splt:]


def split_into_train_test_by_students(cases, stu_level_names):
    student_names = ['julia lehman', 'jonathan norton', 'isabel cannella',
                     'drew johnson', 'jojo smith', 'aidan mcarthur',
                     'ashley roorda', 'jonathan anzalone', 'caleb schaefer',
                     'stryder campbell', 'wes taylor', 'jackson lee',
                     'delonaga madden', 'josiah miller', 'sidnee moore',
                     'michael roorda', 'jonah bridges', 'alexandria glass',
                     'adah layerd', 'tristan carrasquilla', 'paige campbell']

    # Shuffle student names at random
    random.shuffle(student_names)

    # Shuffle cases and the corresponding student names in parallel
    cases, stu_level_names = sklearn_shuffle(cases, stu_level_names)

    splt = int(0.7 * len(student_names)) + 1
    train_stu_names = student_names[:splt]
    test_stu_names = student_names[splt:]

    train_d = []
    test_d = []
    for case, stu_lvl_name in zip(cases, stu_level_names):
        if stu_lvl_name[2] in train_stu_names:
            train_d.append((case, stu_lvl_name))
        else:
            test_d.append((case, stu_lvl_name))
    tr_cases, tr_stu_names = zip(*train_d)
    te_cases, te_stu_names = zip(*test_d)

    return tr_cases, tr_stu_names, te_cases, te_stu_names


def write_csv(data, out_fname):
    with open(out_fname, "w") as fp:
        for row in data:
            fp.write(",".join(row) + "\n")


def main():
    if len(sys.argv) != 4:
        print("Usage:\n\t <script> <categorical_data_file> <stu_name_file> <tag_for_output_file>\n")
        exit(0)

    data_fname = sys.argv[1]
    stu_names_fname = sys.argv[2]
    out_tag = sys.argv[3]

    run_split(data_fname, stu_names_fname, "stu_split")


def run_split(data_fname, stu_names_fname, split_type="stu_split"):
    *base, leaf = data_fname.split("/")

    patc = re.compile(r"_([A-Za-z]{3}_\d{2}_17_(all|rand|top3|none))")
    out_tag = patc.search(leaf).group(1)

    # Load cases
    var_names, cases = load_cases(data_fname)

    # Load student names corresponding to the cases.
    # In the mean time, track each with IDnum
    stu_fp = open(stu_names_fname)
    stu_header = ["IDnum"] + stu_fp.readline().strip("\n").split(",")
    stu_level_names = [[f"{i+1}"] + line.split(",") for i, line in enumerate(stu_fp.read().split("\n")[:-1])]

    assert len(cases) == len(stu_level_names)

    # Split into train/test by split type
    if split_type == "stu_split":
        tr_cases, tr_stu_names, te_cases, te_stu_names = split_into_train_test_by_students(cases, stu_level_names)
    elif split_type == "case_split":
        tr_cases, tr_stu_names, te_cases, te_stu_names = split_into_train_test(cases, stu_level_names)
    else:
        print("Unrecognized split method")
        exit(0)

    # For test, exclude the data for competency variables
    te_cases_filtered = []
    for case in te_cases:
        case_filtered = []
        for var, val in zip(var_names, case):
            if len(var) == 1 and var in 'abcdefghijklmnopqrstuvwxyz':
                case_filtered.append("0")
            else:
                case_filtered.append(val)

        te_cases_filtered.append(case_filtered)
                
    # Write to file
    tr_f = f"data/tr_{out_tag}_{split_type}.csv"
    tr_stu_f = f"data/tr_{out_tag}_stu_names_{split_type}.csv"
    te_f = f"data/te_{out_tag}_{split_type}.csv"
    te_stu_f = f"data/te_{out_tag}_stu_names_{split_type}.csv"

    write_csv([var_names] + list(tr_cases), tr_f)
    write_csv([var_names] + list(te_cases_filtered), te_f)

    write_csv([stu_header] + list(tr_stu_names), tr_stu_f)
    write_csv([stu_header] + list(te_stu_names), te_stu_f)


if __name__ == "__main__":
    main()
