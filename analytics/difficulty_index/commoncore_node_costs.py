"""
The map currently used by the program follows the csv file obtained from archivethecore.org:
    difficulty_index/coherence_map_edges_common_core_archivethecore.csv

Other resources for Common Core Standard dependency graph:
    0. http://curtismapper.pic.ucla.edu/MapApp/app/#/map
    1. http://curtismapper.pic.ucla.edu/MapApp/app/js/controllers.js
    2. http://curtismapper.pic.ucla.edu/MapApp/app/json/4298.json
    3. http://curtismapper.pic.ucla.edu/MapApp/app/json/k_pos.json
"""

import networkx as nx


def build_cc_dependency_graph(full_graph_csv, *grades):
    """
    Args:
        full_graph_csv: string with csv filename
            Header of the csv file is "EdgeDesc,Begin,End,Notes"

        grades: tuple with single character strings denoting grade level
            Used for filtering the nodes. E.g. if grades == ["6", "7"],
            we are only interested in nodes related to the 6th and the 7th
            grade.
    """
    G = nx.DiGraph()

    for line in open(full_graph_csv):
        arrow, src, dest, *rest = line.strip().split(",")

        # Skip if undirected arrow is present
        if arrow != "Arrow":
            continue

        # Skip those grades which are not what we are interested in
        if sum([src.startswith(g) for g in grades]) == 0:  # or sum([dest.startswith(g) for g in grades]):
            continue

        src, dest = [v.replace('"', "") for v in [src, dest]]
        G.add_edge(src, dest, weight=1)

    return G


def compute_node_cost(G, dest):
    # Get all start nodes with no in-coming edges
    start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]

    # Get the distance to dest from all the start nodes
    # Use the max length path.
    dists = []
    for src in start_nodes:
        try:
            dists.append(nx.shortest_path_length(G, source=src, target=dest))
        except nx.exception.NetworkXNoPath:
            continue

    print(dists)

    # Return the minimum distance or the sum?
    return sum(dists)



if __name__ == "__main__":
    grades = ["6", "7"]
    cc_math_csv = "difficulty_index/coherence_map_edges_common_core_archivethecore.csv"
    grph = build_cc_dependency_graph(cc_math_csv, *grades)
    cost = compute_node_cost(grph, "7.RP.2")
    print(cost)

    out_fn = "cc_math_dependency.pdf"
    A = nx.nx_agraph.to_agraph(grph)
    A.layout()
    A.draw(out_fn, prog="dot")

    """
    for node in grph.nodes():
        if grph.degree(node) == 1:
            print(node)
    """
