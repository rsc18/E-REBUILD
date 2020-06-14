import pandas as pd


def rename_prev_netica_csv_casefile(old_csv_fn, new_csv_fn):
    """
    In the previous version of the Bayesian Network, we had named
    competency nodes as a, b, c, d, e, f, and so on.
    In the newer version, we are directly using the Common Core Competency
    names (with slight modification).

    We have to change the node names in the training/test data as well.
    """
    # The following nodes are used as the two children of the root node
    # in the previous Baysian Network:
    #     "b": "cc7_rp_3",
    #     "h": "cc_8_g_9"
    # So, they don't appear in comp_nodes.
    comp_nodes = [
        "cc8_g_1",
        "cc7_rp_2_a",
        "cc6_g_2",
        "cc6_rp_3_c",
        "cc6_rp_3_a",
        "cc6_g_3",
        "cc6_ns_1",
        "cc6_rp_1",
        "cc8_g_3",
        "cc8_g_4",
        "cc8_g_6",
        "cc8_g_7",
        "cc8_g_2",
        "cc7_rp_2_b",
        "cc7_rp_2_d",
        "cc7_rp_2_c",
        "cc7_g_4",
        "cc7_g_5",
        "cc8_g_5",
        "cc6_rp_2",
        "cc6_rp_3_d",
        "cc7_rp_1",
        "cc8_g_8",
        "cc6_g_4",
        "cc7_g_6",
        "cc6_g_1",
        "cc7_g_2",
        "cc7_g_3",
        "cc6_rp_3_b",
        "cc7_g_1",
        "cc8_g_a_3",
        "cc8_g_a_1",
        "cc7_rp_a_1",
        "cc6_rp_a_3",
        "cc7_rp_a_3",
        "cc7_g_b_5",
        "cc6_g_a_1",
        "cc6_g_a_2",
        "cc7_g_b_4",
        "cc7_g_b_6",
        "cc8_g_c_9",
        "cc6_g_a_4",
        "cc8_g_a_2",
        ]

    to_change = {
        "a": "math",
        "b": "cc7_rp_3",
        "h": "cc_8_g_9"
        }

    to_del = ['c', 'd', 'e', 'f', 'g', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v']

    new_obs = [
        "LevelComplete",
        "MaterialCredits",
        "Time",
        "BuildingComplete",
        "NumBlocks",
        "NumTrades",
        "AssignmentComplete",
        "Angle",
        "Distance",
        "NumAssignments",
        "NumFailedAssignments",
        "NumFamilyCollected",
        "NumWrong",
        "Size",
        "HappinessCredit",
        "Collect",
        "EmptyInventory",
        "FillArea2D",
        "FillVolume",
        "Fold3D",
        "LivingArea",
        "Paint",
        "PercentLost",
        "PlaceItems",
        "ProtectFloor",
        "TotalLost"
        ]


    # Skip first two rows because they are Netica related identifiers.
    dframe = pd.read_csv(old_csv_fn, skiprows=2)

    # rename a, b, h
    dframe = dframe.rename(columns=to_change)

    # delete
    dframe.drop(to_del, inplace=True, axis=1)

    # insert new competency nodes with default vals as *
    idx = 4
    for nd in comp_nodes:
        dframe.insert(idx, nd, "*")
        idx += 1

    # insert observables if they don't exist
    for nd in new_obs:
        if nd not in dframe.columns:
            dframe[nd] = "*"

    with open(new_csv_fn, "w") as out_fp:
        out_fp.write("// ~->[CASE-1]->~\n\n")
        dframe.to_csv(out_fp, index=None, sep=",")

if __name__ == "__main__":
    import sys

    old_csv_fn = "data/netica_tr_old_bnet_jan_15.csv"
    new_csv_fn = "data/netica_tr_new_bnet_jan_15.csv"

    rename_prev_netica_csv_casefile(old_csv_fn, new_csv_fn)
