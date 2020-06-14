"""
    Script to create either the learning trajectory layout or
    the Bayesian Network.

    The learning trajectory is saved as node_link json format.
    The Bayesian Network is saved as Netica .dne file.
"""


import json
import networkx as nx
from networkx.readwrite import json_graph
import itertools
import random
import os
import argparse
from bayesnet_node_info import rename_node, get_competency_vars, get_observable_edges


# Use networkx version 1.11
# Comes packaged with pomegranate
assert nx.__version__ == '1.11', f"networkx: pomegranate needs 1.11 but found {nx.__version__}"


def get_cmd_args():
    """
    Parse commandline arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process UCLA Curtis Center's Common Core Map to generate trajectory or Bayesian Net."
        )

    parser.add_argument("--type",
        choices=["bayesnet", "trajectory"],
        help="What should be created? learning trajectory layout or Bayesian Network",
        required=True
        )

    parser.add_argument("--out_file",
        help="Output file",
        required=True
        )

    return parser.parse_args()


def extract_edges_from_ucla_json(ucla_fn, needed_cc):
    with open(ucla_fn) as fp:
        data = json.load(fp)

    # Extract edges
    edges = []
    node_ids_names = data["children"]["containers"]
    for k in data["links"]:
        edge = data["links"][k]
        src = str(edge["from_cai_id"])
        dest = str(edge["to_cai_id"])

        src_n = node_ids_names[src]["name"]
        dst_n = node_ids_names[dest]["name"]

        if dst_n not in needed_cc:
            continue

        edges.append((src_n, dst_n))

    # Extract node position in x-direction
    # node_posx = {node_ids_names[k]["name"]: node_ids_names[k]["posx"] for k in node_ids_names}
    # print(min(node_posx.values()), max(node_posx.values()))
    # vals = node_posx.values()
    # unq_vals = set(vals)

    return edges


def construct_graph(edges):
    """
    Return a directed graph constructed based on the given edges.
    Attach all nodes that do not have out-going edges to a dummy
    node called 'math'.
    """
    graph = nx.DiGraph(edges)

    # delete nodes which are not in 6, 7 or 8 grades
    #node_list = list(graph.nodes())
    #for nd in node_list:
    #    if nd[0].isdigit() and nd[0] not in ["6", "7", "8"]:
    #        graph.remove_node(nd)

    # connect all nodes that have no outgoing edges to an extra node.
    # exclude the observable nodes.
    final_node = "math"
    for nd in list(graph.nodes()):
        #if nd[0].isdigit() and graph.out_degree(nd) == 0:
        if graph.out_degree(nd) == 0 and nd != final_node:
            graph.add_edge(nd, final_node)

    # Return after reversing the graph edges.
    # This is for maintaining compatibility with the previous Bayesian Network.
    return graph


def convert_graph_to_netica(graph, out_f):
    """
    Given a directed graph with parent-child relationships among nodes,
    save a Netica Bayesian Network with randomly initialized CPTs.

    """
    all_nodes = []
    for nd in graph.nodes():
        # find parents
        parents = graph.predecessors(nd)

        # cpt
        node_cpt = get_random_cpt(nd, parents)

        all_nodes.append(node_cpt)

    with open(out_f, "w") as fp:
        fp.write("\n\n".join(all_nodes))


def convert_graph_to_netica_dne(graph, net_name, out_f):
    """
    Given a directed graph with parent-child relationships among nodes,
    save a Netica Bayesian Network as a dne file with randomly initialized CPTs.

    Args:
        graph: networkx graph

        net_name: Name of the network as a string
            It should not have whitespaces or special characters.
    """
    assert " " not in net_name, "Netica forbids white spaces in the Network Name"

    dne_content = [get_dne_header(net_name)]
    for node in graph.nodes():
        # find parents
        parents = [p for p in graph.predecessors(node)]

        # cpt
        node_cpt = get_netica_dne_node(node, parents, title=node)

        dne_content.append(node_cpt)

    dne_content.append(get_dne_footer())

    with open(out_f, "w") as fp:
        fp.write("\n\n".join(dne_content))



def get_random_cpt(node, parents):
    """
    Example nodes:

    asia:
    True False
    0.5 0.5


    tuberculosis_or_cancer:
    True False tuberculosis lung
    1.0  0.0   True         True
    1.0  0.0   True         False
    1.0  0.0   False        True
    0.0  1.0   False        False
    """
    categories = ["High", "Medium", "Low"]

    content = [f"{node}:"]
    content.append("\t".join(categories + parents))

    # CPT
    if len(parents):
        for tup in itertools.product(*[categories for i in range(len(parents))]):
            prob = [random.random() for i in range(len(categories))]
            total = sum(prob)
            prob_s = [str(v / total) for v in prob]

            content.append("\t".join(prob_s + list(tup)))
    else:
        prob = [random.random() for i in range(len(categories))]
        total = sum(prob)
        prob_s = [str(v / total) for v in prob]

        content.append("\t".join(prob_s))


    return "\n".join(content)


def get_random_cpt_dne(node, parents):
    """
    Example nodes:

    // High         Medium       Low         // a   
    (0.6134453,   0.3865546,   2.80112e-8,   // High  
     0.01464437,  0.8472803,   0.1380753,    // Medium 
     5.050504e-8, 0.3282828,   0.6717172);   // Low    

    """
    categories = ["High", "Medium", "Low"]

    content = ["\t".join(["//"] + categories + ["//"] + parents)]

    # CPT
    if len(parents):
        cpt_size = int(len(categories)**len(parents))
        for j, tup in enumerate(itertools.product(*[categories for i in range(len(parents))])):
            prob = [random.random() for i in range(len(categories))]
            total = sum(prob)

            # probability string
            prob_s = ",\t".join([str(v / total) for v in prob])

            # parent string
            paren_s = "\t".join(list(tup))

            # Check if it's the starting or ending CPT entry
            if j == 0:
                line = f"({prob_s},\t//\t{paren_s}"
            elif j == (cpt_size - 1):
                line = f"{prob_s});\t//\t{paren_s};"
            else:
                line = f"{prob_s},\t//\t{paren_s}"

            content.append(line)
    else:
        prob = [random.random() for i in range(len(categories))]
        total = sum(prob)

        # probability string
        prob_s = ",\t".join([str(v / total) for v in prob])

        line = f"({prob_s});"

        content.append(line)


    return "\n".join(content)


def get_dne_header(net_name):
    header = """
// ~->[DNET-1]->~

// File created by KeF at FSU_Education using Netica 6.04 on Aug 23, 2018 at 16:39:10 UTC.

bnet %s {
AutoCompile = TRUE;
autoupdate = TRUE;
whenchanged = 1535042350;

visual V1 {
        defdispform = BELIEFBARS;
        nodelabeling = TITLE;
        NodeMaxNumEntries = 50;
        nodefont = font {shape= "Arial"; size= 9;};
        linkfont = font {shape= "Arial"; size= 9;};
        ShowLinkStrengths = 1;
        windowposn = (78, 78, 1376, 597);
        scrollposn = (709, 0);
        resolution = 72;
        magnification = 0.707107;
        drawingbounds = (3114, 1310);
        showpagebreaks = FALSE;
        usegrid = TRUE;
        gridspace = (6, 6);
        NodeSet Node {BuiltIn = 1; Color = 0x00e1e1e1;};
        NodeSet Nature {BuiltIn = 1; Color = 0x00f8eed2;};
        NodeSet Deterministic {BuiltIn = 1; Color = 0x00d3caa6;};
        NodeSet Finding {BuiltIn = 1; Color = 0x00c8c8c8;};
        NodeSet Constant {BuiltIn = 1; Color = 0x00ffffff;};
        NodeSet ConstantValue {BuiltIn = 1; Color = 0x00ffffb4;};
        NodeSet Utility {BuiltIn = 1; Color = 0x00ffbdbd;};
        NodeSet Decision {BuiltIn = 1; Color = 0x00dee8ff;};
        NodeSet Documentation {BuiltIn = 1; Color = 0x00f0fafa;};
        NodeSet Title {BuiltIn = 1; Color = 0x00ffffff;};
        PrinterSetting A {
                margins = (1270, 1270, 1270, 1270);
                };
        };

    """ % (net_name)
    return header


def get_dne_footer():
    return "};"


def get_netica_dne_node(node, parents, title):
    """
    Example dne format node:

    node a {
        discrete = TRUE;
        states = (High, Medium, Low);
        kind = NATURE;
        chance = CHANCE;
        parents = ();
        probs =
                // High         Medium       Low        
                  (0.3455954,   0.4627299,   0.1916747);
        numcases = 1033;
        title = "a: Solving Mathematical problems involving ratio, proportion, angle, area, surface area and \
                volume";
        whenchanged = 1508264566;
        belief = (0.3455954, 0.4627299, 0.1916747);
        visual V1 {
                center = (1470, 36);
                height = 1;
                };
        };

    """
    paren_s = ",".join(parents)
    node_cpt = get_random_cpt_dne(node, parents)
    node_code = f"""
node {node} {{
        discrete = TRUE;
        states = (High, Medium, Low);
        kind = NATURE;
        chance = CHANCE;
        parents = ({paren_s});
        probs = \n{node_cpt}

        title = "{title}";

        visual V1 {{}};
    }};
    """

    return node_code


def main():
    cmd_args = get_cmd_args()
    out_type = cmd_args.type
    out_fn = cmd_args.out_file

    # JSON file holding the Curtis Mapper layout
    #ucla_fn = os.path.join("db_jsons", "4298.json")
    ucla_fn = os.path.join("analytics", "data", "ucla", "4298.json")

    # Filtered Common Core Standards
    needed_cc = get_competency_vars()

    # Get the edges
    comp_edges = extract_edges_from_ucla_json(ucla_fn, needed_cc)
    obs_edges = get_observable_edges()

    # Convert the node names in the edges for Netica compatibility
    comp_edges = [(rename_node(u), rename_node(v)) for u, v in comp_edges]
    obs_edges = [(rename_node(u), rename_node(v)) for u, v in obs_edges]


    if out_type == "trajectory":
        assert out_fn.split(".")[-1] == "json"

        # Build the graph from only competency edges
        graph = construct_graph(comp_edges)
        print([edg for edg in graph.edges() if "math" in edg])

        # Write the graph in d3 format
        grph_jsn = json_graph.node_link_data(graph)
        with open(out_fn, "w") as write_file:
            json.dump(grph_jsn, write_file)
    else:
        assert out_fn.split(".")[-1] == "dne"

        # Build the graph from needed edges.
        needed_edges = obs_edges + comp_edges
        graph = construct_graph(needed_edges)

        # Reverse the graph
        graph = graph.reverse()
        convert_graph_to_netica_dne(graph, "Bayesnet_CC_UCLA", out_fn)


if __name__ == "__main__":
    main()
