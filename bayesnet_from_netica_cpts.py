"""

1. How to save CPTs from .neta file
   --------------------------------

    Netica => CTRL-A => Report => To file => Enter filename, say 'cpts.txt'
    => CPT Tables

    Please note that Netica sometimes renames the nodes. You have to manually
    correct those before parsing the CPTs with this program.


2. Format of thus created 'cpts.txt'
   ---------------------------------
    <node>:
    <label> <label> <label> <parent_node> <parent_node>
    <prob>  <prob>  <prob>  <label>       <label>
    ...
    ...
    <newline>
    <newline>
    <node>:
    <label> <label> <label> <parent_node> <parent_node>
    <prob>  <prob>  <prob>  <label>       <label>
    ...
    ...
    <newline>
    <newline>
    ...
    ...

   CPT of <node> is defined by its parents <parent_node>.
   Two newlines separate consecutive CPT definition.

   (a) <label> is a category a node can take.
       We assume it is not composed of only numbers.

   (b) <prob> is the probability value. Always a number.
       There are no tabs.

   For a more elaborate example, you can check "asia_cpts.txt".

"""

import os
BASE_DIR = os.getcwd()
import sys
sys.path.append(BASE_DIR)

from pomegranate import DiscreteDistribution
from pomegranate import ConditionalProbabilityTable
from pomegranate import BayesianNetwork, Node
from collections import defaultdict
from bayesian_network.bn_visualizer import visualize_network 
import networkx as nx


def get_num_category(netica_cpt_node):
    """
    Given the CPT of a Netica node, return the number of categories for the node.

    For example, for dyspnea, the number of categories is two: True, False.

        dyspnea:
        True False tuberculosis_or_cancer bronchitis
        0.96 0.04  True                   True
        0.89 0.11  True                   False
        0.96 0.04  False                  True
        0.89 0.11  False                  False
    """
    # Count the number of floats in the second line
    prob_count = 0
    for v in netica_cpt_node.strip().split("\n")[2].split():
        try:
            float(v)
            prob_count += 1
        except:
            continue

    return prob_count


def get_ordered_node_blobs(cpt_txt):
    """
    Since the CPTs may not be in order, i.e. sometimes the definition of
    of a parent can be below that of the child, the nodes need to be
    ordered.
    """
    # Load file content
    node_blobs = open(cpt_txt).read().strip().split("\n\n\n")

    # Track BayesNet nodes along with the node names
    blobs = dict()

    # Create a directed acyclic graph
    G = nx.DiGraph()

    # Parse and create individual nodes
    for blob in node_blobs:
        lines = blob.strip().split("\n")

        # get the number of labels for the node in the current blob
        num_labels = get_num_category(blob)

        # Extract the current node name
        node_name = lines[0].split(":")[0]      # "a:"

        # Extract parents and labels
        parents_line = [v.strip() for v in lines[1].split()]         # "High  Medium  Low  d"
        parents = parents_line[num_labels:]

        if len(parents) == 0:
            root = node_name
        else:
            for p in parents:
                G.add_edge(p, node_name)

        blobs[node_name] = blob

    order = nx.topological_sort(G)

    return [blobs[k] for k in order]


def build_bayesnet_from_netica_cpts(netica_cpt_txt):
    """
    For a CPT obtained from Netica, given below:

        dyspnea:
        True False tuberculosis_or_cancer bronchitis
        0.96 0.04  True                   True
        0.89 0.11  True                   False
        0.96 0.04  False                  True
        0.89 0.11  False                  False

    instantiate the following pomegranate's ConditionalProbabilityTable:
        dyspnea = ConditionalProbabilityTable(
            [[ 'True', 'True', 'True', 0.96 ],
             [ 'True', 'True', 'False', 0.04 ],
             [ 'True', 'False', 'True', 0.89 ],
             [ 'True', 'False', 'False', 0.11 ],
             [ 'False', 'True', 'True', 0.96 ],
             [ 'False', 'True', 'False', 0.04 ],
             [ 'False', 'False', 'True', 0.89 ],
             [ 'False', 'False', 'False', 0.11 ]], [tuberculosis_or_cancer, bronchitis])
    """
    # Track BayesNet nodes along with the node names
    nodes = defaultdict(dict)

    # Track dependency between nodes as tuples of node name pairs.
    # (x, y) means x is the parent of y.
    transition_tracker = []

    # Parse and create individual nodes
    for blob in get_ordered_node_blobs(netica_cpt_txt):
        lines = blob.strip().split("\n")

        # get the number of labels for the node in the current blob
        num_labels = get_num_category(blob)

        # Extract the current node name
        node_name = lines[0].split(":")[0]      # "a:"

        # Extract parents and labels
        parents_line = [v.strip() for v in lines[1].split()]         # "High  Medium  Low  d"
        curr_node_lbls = parents_line[:num_labels]
        parents = parents_line[num_labels:]
        #print(parents_line)

        # Check for root node based on the no. of parents
        if len(parents) == 0:
            probs = [float(v) for v in lines[2].split()]
            nodes[node_name] = DiscreteDistribution(dict(zip(curr_node_lbls, probs)))
        else:
            table = []
            for line in lines[2:]:
                # Read probabilities and parent labels in the current line.
                line = line.split()
                probs = [float(v) for v in line[:num_labels]]
                pa_lbls = line[num_labels:]

                for i, lbl in enumerate(curr_node_lbls):
                    row = []
                    # Append order: labels for the parents, then the curr node label.
                    row += pa_lbls
                    row.append(lbl)

                    # Finally the probability value
                    row.append(probs[i])

                    table.append(row)

            # Create node
            nodes[node_name] = ConditionalProbabilityTable(table, [nodes[k] for k in parents])

            # Track transition
            transition_tracker += [(pa, node_name) for pa in parents]

    # Create Node objects
    states = {k: Node(nodes[k], name=k) for k in nodes}

    #print(list(nodes.keys()))
    #for k in nodes:
    #    print(nodes[k])

    # Create the Bayesian network object with a useful name
    model = BayesianNetwork("Mini Network")

    # Add states
    model.add_states(*states.values())

    # Add transitions
    for src, dest in transition_tracker:
        model.add_transition(states[src], states[dest])

    model.bake()

    return model


def test_asia():
    import json

    asia_netica = "bayesian_network/asia_cpts.txt"
    model = build_bayesnet_from_netica_cpts(asia_netica)

    observations = { 'tuberculosis' : 'True', 'smoking' : 'False', 'bronchitis' : 'True' }
    expected_marginals = {"asia": {"True": 0.9523809523809523, "False": 0.047619047619047616},
                          "tuberculosis_or_cancer": {"True": 1.0, "False": 0.0},
                          "dyspnea": {"True": 0.96, "False": 0.04}
                         }

    beliefs = model.predict_proba(observations)

    for st, bel in zip(model.states, beliefs):
        if st.name in expected_marginals:
            pred = json.loads(bel.to_json())["parameters"][0]
            for k in pred:
                diff = abs(pred[k] - expected_marginals[st.name][k])
                print(st.name, k, diff)
                assert diff <= 0.000001


def main():
    #cpt_f = "bayesian_network/cpts.txt"
    #cpt_f = "bayesian_network/cpts_per20.txt"
    cpt_f = sys.argv[1]
    tag = cpt_f.split(os.sep)[-1].split(".")[0]
    json_f = f"net_{tag}.json"
    model = build_bayesnet_from_netica_cpts(cpt_f)

    # write to a file
    import json
    with open(json_f, "w") as fp:
        fp.write(json.dumps(model.to_json()))

    #visualize_network(model, "bn_from_netica_cpts.pdf")

if __name__ == "__main__":
    #test_asia()
    main()
