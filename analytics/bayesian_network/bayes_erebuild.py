from pomegranate import DiscreteDistribution as DDist
from pomegranate import ConditionalProbabilityTable as CPT
from pomegranate import BayesianNetwork as BayesNet
from pomegranate import State
import os
import itertools
import pygraphviz
import random
import numpy as np
import json
from sklearn.utils import shuffle as sklearn_shuffle

def get_feature_sequence():
    graph_nodes = 'abcdefghijklmnopqrstuv'
    competency_vars = list(graph_nodes)

    observable_vars = ['Angle', 'AssignmentComplete', 'BuildingComplete',
                       'Distance', 'LevelComplete', 'MaterialCredits',
                       'NumAssignments', 'NumBlocks', 'NumFailedAssignments',
                       'NumFamilyCollected', 'NumTrades', 'NumWrong',
                       'Size', 'Time', 'TotalLost']

    return competency_vars + observable_vars


def get_nodes_relationships():
    # Competency variables:
    # Parent assignment is based on model2.pdf 30 June, 2017.
    competency_vars = {
        "a":  {"parents": [],
               "title": "Solving mathematical problems involving ..."},
        "b":  {"parents": ["a"], 
               "title":"Reason with ratio and proportional resoning ..."},
        "c":  {"parents": ["b"], 
               "title":"Solve real-world math problems using ratio ..."},
        "d":  {"parents": ["c"], 
               "title":"Solve unit rate real-world problems"},
        "e":  {"parents": ["d"], 
               "title":"Calculate the unit rate (a/b) associated with a ratio (a : b)"},  # attach obs
        "f":  {"parents": ["d"], 
               "title":"Solve problems involving finding the whole, given a part or a percent"},  # attach obs
        "g":  {"parents": ["c", "b"], 
               "title":"Comprehend a ratio relationship via numerical, verbal, and symbolic forms"},  # attach obs
        "h":  {"parents": ["a"], 
               "title":"Solving mathematical real world problems..."},
        "i":  {"parents": ["h"], 
               "title":"Solve problems involving area, volume..."},
        "j":  {"parents": ["h"], 
               "title":"Solve problems involving volume of cylinder..."},
        "k":  {"parents": ["h"], 
               "title":"Compute an unknown angle in ..."},
        "l":  {"parents": ["i"], 
               "title":"Compute the area of triangles, quadrilaterals..."},
        "m":  {"parents": ["i"], 
               "title":"Compute volumes of right rectangular ..."},
        "n":  {"parents": ["l"], 
               "title":"(De)compose quadrilaterals and polygons into (right) triangles and rectangles"},  # attach obs
        "o":  {"parents": ["l"], 
               "title":"Compute the area and perimeter of triangle and rectangle"},  # attach obs
        "p":  {"parents": ["m"], 
               "title":"Find surface areas of 3D figures using nets of rectangles and (right) triangles"},  # attach obs
        "q":  {"parents": ["m"], 
               "title":"Compute the volume of right rectangular prisms (V = l w h, V = b h)"},  # attach obs
        "r":  {"parents": ["j"], 
               "title":"Compute area and circumference of a circle using formulas"},  # attach obs
        "s":  {"parents": ["j"], 
               "title":"Compute the volumes of cones, cylinders and spheres."},  # attach obs
        "t":  {"parents": ["k"], 
               "title":"Recognize and determine supplementary, complementary, vertical, and adjacent angles"},  # attach obs
        "u":  {"parents": ["k"], 
               "title":"Understand that the angles are created when parallel lines are cut by a transversal"},  # attach obs
        "v":  {"parents": ["k"], 
               "title":"Understand congruence and similarity using physical models, transparencies, geometry software"},  # attach obs
        }

    # Observables:
    # Parent assignment:
    #    If Q-matrix has a 1 for a given level, all observables for that level
    #    have the corresponding competency variable as a parent.
    observable_vars = {
        "Angle":   {"parents": ['n', 'v', 'g', 'p', 'e', 'o', 'f', 't'],
               "title":"Angle"},
        "AssignmentComplete": {"parents": ["a"],  # ['g', 'e', 'o', 'f', 'q'],
               "title":"AssignmentComplete"},
        "BuildingComplete": {"parents": ["a"],  # ['n', 'v', 'g', 'p', 'e', 'o', 'f', 't'],
               "title":"BuildingComplete"},
        "LevelComplete":   {"parents": ["a"],  # ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n', 'q'],
               "title":"LevelComplete"},
        "Distance":   {"parents": ['p', 't', 'f', 'o', 'g', 'v', 'e', 'n'],
               "title":"Distance"},
        "MaterialCredits":   {"parents": ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n'],
               "title":"MaterialCredits"},
        "NumAssignments":   {"parents": ['o', 'f', 'g', 'e', 'q'],
               "title":"NumAssignments"},
        "NumBlocks":   {"parents": ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n'],
               "title":"NumBlocks"},
        "NumFailedAssignments":   {"parents": ['o', 'f', 'g', 'e', 'q'],
               "title":"NumFailedAssignments"},
        "NumFamilyCollected":   {"parents": ['o', 'f', 'g', 'e', 'q'],
               "title":"NumFamilyCollected"},
        "NumTrades":   {"parents": ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n'],
               "title":"NumTrades"},
        "NumWrong":   {"parents": ['o', 'f', 't', 'g', 'e', 'n'],
               "title":"NumWrong"},
        "Size":   {"parents": ['p', 't', 'f', 'o', 'g', 'v', 'e', 'n'],
               "title":"Size"},
        "Time":   {"parents": ["a"], # ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n', 'q'],
               "title":"Time"},
        "TotalLost":   {"parents": ['p', 'o', 'f', 't', 'g', 'v', 'r', 'e', 'n'],
               "title":"TotalLost"}
        }

    return competency_vars, observable_vars


def init_cpt(parents, curr_keys=None):
    """
    Given a list of parents, return a pomegranate ConditionalProbabilityTable
    with initial probabilities for the current node.

    curr_keys are the keys to the current node.
    All of parents of the current node have the same keys: h, m, l.
    """
    # All parents have High, Medium, Low keys
    pa_keys = ("h", "m", "l")
    n_pa = len(parents)

    if curr_keys is None:
        curr_keys = pa_keys

    init_prob = [1 / len(curr_keys) for k in curr_keys]
    init_prob = [random.random() for k in curr_keys]
    cpt = []
    for comb in itertools.product(*[pa_keys for i in range(n_pa)]):
        for k, p in zip(curr_keys, init_prob):
            cpt.append(list(comb) + [k, p / sum(init_prob)])

    pom = CPT(cpt, parents)

    return pom


def get_erebuild_bayesian_network():
    # Get the nodes
    comp_vars, obs_vars = get_nodes_relationships()

    # Merge the two dictionaries
    all_vars = {**comp_vars, **obs_vars}

    # Initialize CPTs for competency vars.
    needed_comp = "abcdefghijklmnopqrstuv"

    # First, the root node:
    all_cpts = {"a": DDist({"h": 0.2, "m": 0.5, "l": 0.3})}

    # The non-root nodes should be initialized in sequence.
    for v in needed_comp[1:]:
        parents = comp_vars[v]["parents"]
        all_cpts[v] = init_cpt([all_cpts[p] for p in parents])

    # Initialize CPTs for obs vars
    for v in obs_vars.keys():
        parents = obs_vars[v]["parents"]
        all_cpts[v] = init_cpt([all_cpts[p] for p in parents])

    # Initialize states
    states = dict()
    for v in all_cpts.keys():
        states[v] = State(all_cpts[v], name=v)

    # Initialize Bayesian Network
    network = BayesNet("Erebuild")

    # Add nodes by maintaining the order present in case files
    ordered_features = get_feature_sequence()
    network.add_nodes(*[states[k] for k in ordered_features])

    # Add edges
    for v in all_vars:
        for p in all_vars[v]["parents"]:
            network.add_edge(states[p], states[v])

    # Prepare network
    network.bake()


    return network


def visualize_network(network, filename):
    G = pygraphviz.AGraph(directed=True)

    # Get the titles for each competency var
    comp_vars, _ = get_nodes_relationships()
    comp_var_title = {var: comp_vars[var]["title"] for var in comp_vars}


    beliefs = network.predict_proba({})
    for state, belief in zip(network.states, beliefs):
        belief = json.loads(belief.to_json())["parameters"][0]

        # More descriptive labels for competency vars
        if state.name in comp_var_title:
            title = comp_var_title[state.name][:15]
        else:
            title = ""

        label_str = state.name + ":" + title +\
                    "\n" + "\n".join([f"{k}:{p:.3f}" for k, p in belief.items()])

        G.add_node(state.name, color='blue', shape="box", label=label_str)


    for parent, child in network.edges:
        G.add_edge(parent.name, child.name)

    G.draw(filename, format='pdf', prog='dot')


def load_cases(fname):
    """
    """
    mapping = {0: None, 1: "l", 2: "m", 3: "h"}
    with open(fname) as fp:
        var_names = fp.readline().strip("\n").split(",")

    cases = []
    for case in np.loadtxt(fname, delimiter=",", skiprows=1, dtype=np.int8):
        d = [mapping[val] for val in case]
        cases.append(d)

    return var_names, cases


def make_observation(case, var_names):
    mapping = {1: "l", 2: "m", 3: "h"}
    return {var: mapping[val] for var, val in zip(var_names, case) if val != 0}


def split_into_train_test(cases, stu_names):
    """
    70 % for training.
    """
    cases, stu_names = sklearn_shuffle(cases, stu_names)

    splt = int(0.7 * len(cases)) + 1

    return cases[:splt], stu_names[:splt], cases[splt:], stu_names[splt:]


def print_probabilities(model):
    beliefs = map( str, model.predict_proba({}))
    print("\n".join( "{}\t\t{}".format(state.name, belief) for state, belief in zip(model.states, beliefs)))


def run_train_test():
    data_fname = "data/categorical_cases_FallSpring16-17.csv"
    stu_names_fname = "data/level_student_names_cases_FallSpring16-17.csv"

    # Load cases
    var_names, cases = load_cases(data_fname)

    # Load student names corresponding to the cases
    stu_names = [line.split(",")[1].strip("\n") for line in open(stu_names_fname).read().split("\n")[1:-1]]
    assert len(cases) == len(stu_names)

    # Split into train/test
    tr_cases, tr_stu_names, te_cases, te_stu_names = split_into_train_test(cases, stu_names)

    # Get the model. If model doesn't already exist, train it.
    model_json_fname = "models/trained_erebuild_bayesian_net.json"
    if os.path.exists(model_json_fname):
        model = BayesNet.from_json(open(model_json_fname).read())
    else:
        # Get randomly initialized model
        model = get_erebuild_bayesian_network()

        visualize_network(model, "bayesnet_initial.pdf")

        train_iter = 2
        for t in range(train_iter):
            print(f"Iteration {t}")
            print("Imputing...")
            cases_imputed = model.predict(tr_cases)
            print("Fitting...")
            model.fit(cases_imputed)

        visualize_network(model, f"bayesnet_trained_{train_iter}.pdf")

        # Write learned model to a json file
        model_str = model.to_json()
        with open(model_json_fname, "w") as fp:
            fp.write(model_str)


if __name__ == "__main__":
    run_train_test()

# Meeting notes 8/1/2017:
# 1. based on row no. 34 in map_observables_to_levels, try to assign that many observables for the competency var
# 2. How to split? Make a bunch of assumptions:
#     (a) Assume all examples to be independent.
#     (b) Split based on two sets of students. 15 students for training at random
#     (b) Make the split dependent on level and student.
# 3. Look at the final marginals. Many nodes have the same values. It shouldn't be so.
#    Why is this happening?
# 4. Per student prediction.
# 5. Observables Time and LevelComplete shoud point to the root.
