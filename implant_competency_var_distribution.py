"""
    This module fills out portions of missing fields in the training split
    of the dataset. The fields are the common core competency standards.

    We have no prior information about the more fine-grained math competency 
    of the students. We only know their pre-post math scores and also the
    chronologically adjusted math scores. We can fill out based on this score.

    Rule:
        avg, std => mean and standard devisation of premath scores
        lower = avg
        upper = avg + std

        If x is the chronologically adjusted score, the category of
        a competency (say cc6_g_a_1) will be:
            High, if x > upper
            Medium, if lower <= x < upper
            Low, if x < lower

        We apply this rule to all the common core competency vars in the
        Bayesian Network.
"""

import sys
import pandas as pd
import numpy as np
from bayesnet_node_info import get_competency_vars


def fill_competency(in_csv, prepost_csv, out_csv):
    df_in = pd.read_csv(in_csv, header=0)

    # output dataframe
    df_out = df_in.copy()

    df_prepost = pd.read_csv(prepost_csv, header=0)
    avg = df_prepost["premath"].mean()
    std = df_prepost["premath"].std()
    upper = avg + std
    lower = avg 

    # Common core competency vars used in the Bayesian Network
    comp_var = get_competency_vars()

    for idx, row in df_in.iterrows():
        row_cp = row.copy()

        # Convert the value under 'math' into category.
        # It holds the chronologically adjusted score.
        score = row.loc["chronology_math"]
        if score > upper:
            category = "High"
        elif lower <= score <= upper:
            category = "Medium"
        else:
            category = "Low"

        # Update the copied row
        for var in comp_var:
            row_cp[var] = category

        # Update the output dataframe.
        df_out.loc[idx] = row_cp

    # Write out the csv
    df_out.to_csv(out_csv, index=False)


if __name__ == "__main__":
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    prepost_csv = sys.argv[3]

    fill_competency(in_csv, prepost_csv, out_csv)
