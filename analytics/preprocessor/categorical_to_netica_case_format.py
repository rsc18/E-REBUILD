"""
Convert categorical format to Netica Case file format.

More details here: http://www.norsys.com/tutorials/netica/Case_File_Format.txt

"""

import os
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Convert categorical CSV file to Netica Case file format')
    parser.add_argument("in_csv", help="CSV file to convert to Netica Case format.")

    return parser.parse_args()

def convert_to_netica_case(in_fname):
    #mapping = {"0": "*", "1": "l", "2": "m", "3": "h"}
    mapping = {"0": "*", "1": "Low", "2": "Medium", "3": "High"}
    mapping = {"": "*", "Low": "Low", "Medium": "Medium", "High": "High"}

    *base, tail = in_fname.split(os.sep)
    out_fname = os.sep.join(base + ["netica_" + tail])

    in_fp = open(in_fname)
    out_fp = open(out_fname, "w")

    # Write the Netica Case format marker
    out_fp.write("// ~->[CASE-1]->~\n\n")

    # Write header
    header = "IDnum," + ",".join(in_fp.readline().strip("\n").split(","))
    #header = ",".join(in_fp.readline().strip("\n").split(","))
    out_fp.write(header + "\n")

    for i, line in enumerate(in_fp):
        if line.startswith("#"):
            continue

        #case = str(i + 1) + "," + ",".join([mapping[v] for v in line.strip("\n").split(",")])
        idnum, *vals = line.strip("\n").split(",")
        case = idnum + "," + ",".join([mapping[v] for v in vals])

        # Write case
        out_fp.write(case + "\n")

    print(f"\tWritten: {out_fname}")

if __name__ == "__main__":
    cmd_args = get_args()
    in_fname = cmd_args.in_csv

    convert_to_netica_case(in_fname)
