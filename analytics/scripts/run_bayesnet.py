import argparse
from pomegranate import BayesianNetwork
import json


def yield_pred_truth(in_csv, bayes_f):
    # Load bayesian network
    bayes_jsn = json.loads(open(bayes_f).read())
    bayesnet = BayesianNetwork.from_json(bayes_jsn)

    lines = open(in_csv).read().split("\n")[:-1]

    header_line = lines[0]
    case_lines = lines[1:]

    obs_keys = ['Angle', 'AssignmentComplete', 'BuildingComplete',
                'Distance', 'LevelComplete', 'MaterialCredits',
                'NumAssignments', 'NumBlocks', 'NumFailedAssignments',
                'NumFamilyCollected', 'NumTrades', 'NumWrong',
                'Size', 'Time', 'TotalLost']

    header_keys = header_line.strip().split(",")
    #print(header_keys)
    truth_keys = ["post_math", "post_ratio", "post_geom"]
    pred_keys = ["a", "b", "h"]
    
    for line in case_lines:
        data = dict(zip(header_keys, line.strip().split(",")))
        #print(data)

        case = {k: data[k] for k in obs_keys if data[k] != ""}
        truth = {k: data[k] for k in truth_keys}

        beliefs = bayesnet.predict_proba(case)

        # Extract only the max marginals for each node
        max_marginals = []
        for bel in beliefs:
            mrgnl = json.loads(bel.to_json())["parameters"][0]
            max_mrgnl = sorted(mrgnl.items(), key=lambda x: x[1])[-1]
            prob = f"{max_mrgnl[1]:.4f}"
            max_marginals.append((max_mrgnl[0], prob))
    
        # Filter based on prediction keys
        pred = {state.name: pred for state, pred in zip(bayesnet.states, max_marginals)
                if state.name in pred_keys}

        yield data["student_name"], pred, truth


def analyze_pred_truth(in_csv, bayes_f):
    skip_names = ["brooks hickman", "chichi okoli", "emmanuel williams",
                  "haleigh davis", "harley mccord", "joseph boland",
                  "laniyah gennie", "layla sims"]

    truth_keys = ["post_math", "post_ratio", "post_geom"]
    pred_keys = ["a", "b", "h"]
    print("stu_name,a,b,h,post_math,post_ratio,post_geom")
    for stu_name, pred, truth in yield_pred_truth(in_csv, bayes_f):
        if stu_name in skip_names:
            continue

        vals = [stu_name] + [pred[k][0] for k in pred_keys] + [truth[k] for k in truth_keys]
        print(",".join(vals))


def get_commandline_args():
    detail = "Parse CSV file with gamelog data and predict competencies using bayes net"
    parser = argparse.ArgumentParser(description=detail)

    parser.add_argument("data_csv",
        help="CSV file containing categorical data. E.g: data/cases_cat_chrono_Feb_06_18.csv",
    )

    parser.add_argument("bayes_net",
        help="Trained Pomegranate Bayesian Network",
    )

    return parser.parse_args()


if __name__ == "__main__":
    cmd_args = get_commandline_args()

    in_csv = cmd_args.data_csv
    bayes_f = cmd_args.bayes_net

    analyze_pred_truth(in_csv, bayes_f)
