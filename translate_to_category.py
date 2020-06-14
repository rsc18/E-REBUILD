import sys
from thomasville_categorization import TMS_CATEGORIZATION
import pandas as pd
import numpy as np
from bayesnet_node_info import get_observable_vars


def categorize(real_csv, cat_csv, rules):
    """
    Args:
        real_csv: csv filename
            File created by game_xml_logs_to_csv.py. Contains 
            raw gamelog data. real => real numbers

        cat_csv: output csv filename
            Data in real_csv undergo categorization and are saved 
            into this file.

        rules: nested dictionary
            Printed out by categorization_rues.print_categorization_rules().
            These rules should be created with the same data in real_csv.
    """
    df = pd.read_csv(real_csv, header=0)

    # dataframe to store categorical values
    df_cat = df.copy()

    all_vars = get_observable_vars() + ["math"]
    for idx, row in df.iterrows():
        row_cat = row.copy()
        game_lvl = row.loc["game_level"]
        for var in all_vars:
            if var == "math":
                val = row.loc[var]
                row_cat[var] = rules[var](val)
                #print(val, var, rules[var](val))
            else:
                if var in rules and game_lvl in rules[var]:
                    val = row.loc[var]
                    if not np.isnan(val):
                        row_cat[var] = rules[var][game_lvl](val)
                        #print(val, var, game_lvl, rules[var][game_lvl](val))
                else:
                    row_cat[var] = np.NaN

        df_cat.loc[idx] = row_cat
        #print(df_cat.loc[idx])
        #exit(0)

    # Save
    df_cat.to_csv(cat_csv, index=False)



if __name__ == "__main__":
    real_csv = sys.argv[1]
    cat_csv = sys.argv[2]
    rules = TMS_CATEGORIZATION

    categorize(real_csv, cat_csv, rules)


