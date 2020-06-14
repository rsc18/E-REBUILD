import json
import pprint
import sys
import networkx as nx


def build_cc_dependency_graph(edges, node_posx):
    """
    Args:
        edges: list of tuples
            Each tuple is an edge of a graph with src and dest fields.

        node_posx: dictionary
            x-coordinate of node given in the UCLA curtis mapper.
    """
    G = nx.DiGraph()

    for edge in edges:
        src, dest = edge
        G.add_edge(src, dest, weight=1)

    # nx.set_node_attributes(G, node_posx, "posx")
    # nx.set_node_attributes(G, "posx", node_posx)    # networkx version dependent

    return G

def write_edges_as_csv(edges, out_csv):
    #out_csv = f"data/ucla/cc_edges_ucla.csv"
    with open(out_csv, "w") as fp:
        for src_n, dst_n in edges:
            fp.write(f"{src_n},{dst_n}\n")


def extract_graph_from_ucla_json(needed_grades):
    ucla_fn = "data/ucla/4298.json"
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

        if dst_n[0] not in needed_grades:  # needed_grades example: ["6", "7", "8"]
            continue

        edges.append((src_n, dst_n))

    # Extract node position in x-direction
    node_posx = {node_ids_names[k]["name"]: node_ids_names[k]["posx"] for k in node_ids_names}
    #print(min(node_posx.values()), max(node_posx.values()))

    vals = node_posx.values()
    unq_vals = set(vals)
    #print(len(vals), len(unq_vals))
    #print(sorted(set(vals)))

    #print(node_posx)

    return edges, node_posx


def get_farthest_pair_difficulty(G):
    # Get all start nodes with no in-coming edges
    start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]

    sum_dists = dict()
    for dest in G.nodes():
        dists = []
        for src in start_nodes:
            try:
                dists.append(nx.shortest_path_length(G, source=src, target=dest))
            except nx.exception.NetworkXNoPath:
                continue

        sum_dists[dest] = sum(dists)

    return max(sum_dists.values())


def get_longest_path(G):
    start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]

    max_shortest = dict()
    for dest in G.nodes():
        dists = []
        for src in start_nodes:
            try:
                dists.append(nx.shortest_path_length(G, source=src, target=dest))
            except nx.exception.NetworkXNoPath:
                continue

        max_shortest[dest] = max(dists)

    return max(max_shortest.values())


def compute_node_difficulty(G, dest):
    # Most difficult grade
    max_grade = 12

    # Sum of all paths between the farthest two nodes
    # Computed by get_farthest_pair_difficulty()
    max_path_sum = 25

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

    # dest grade
    dest_g = int(dest[0])

    # Compute difficulty
    cost = 0.8 * dest_g / max_grade + 0.2 * sum(dists) / max_path_sum

    return cost


def compute_node_difficulty_ancestors(G, dest):
    """
      a---*b
      |   /
      |  /
      | /
      **       
      c *---- d

      Difficulty = no. of ancestors
    """
    # Get the length of the largest connected component
    max_ancestors = len(G)

    # Get all start nodes with no in-coming edges
    start_nodes = [nd for nd in G.nodes() if G.in_degree(nd) == 0]

    # Get all the unique nodes in all the paths from all sources to dest
    ancestors = set()
    for src in start_nodes:
        for pth in nx.all_simple_paths(G, source=src, target=dest):
            for nd in pth:
                ancestors.add(nd)

    # Filter ancestors which do not fall in the same grade level as dest.
    # The first character is the grade level.
    ancestors = {nd for nd in ancestors if nd[0] == dest[0]}

    grade = int(dest[0])

    return 0.8 * len(ancestors) / max_ancestors + 0.2 * grade / 8


def compute_node_difficulty_2(G, dest):
    """
        Difficulty = Grade, Length of Shortest path, In Degree
    """
    # Most difficult grade
    max_grade = 12

    # Max of all shortest paths in the graph.
    # Computed by get_longest_path()
    max_short_path = 8

    # max([G.in_degree(n) for n in G.nodes()])
    max_degree = 4

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

    dest_grade = int(dest[0])
    in_degree = G.in_degree(dest)
    short_path = min(dists)

    # Compute difficulty
    cost = 0.8 * dest_grade / max_grade + 0.1 * short_path / max_short_path + 0.1 * in_degree / max_degree

    return cost


def get_all_node_difficulty_pagerank(G):
    # Personalization is the grade of each node
    prsnl = {k: int(k[0]) for k in grph.nodes()}
    ranks = nx.pagerank(grph, personalization=prsnl, alpha=0.85)

    for nd, diff in sorted(ranks.items(), key=lambda x: x[1]):
        print(f"{nd},{diff}")


def draw_dependency_graph(G):
    out_fn = "cc_ucla_math_dependency.pdf"
    A = nx.nx_agraph.to_agraph(grph)
    A.layout()
    A.draw(out_fn, prog="dot")


if __name__ == "__main__":
    #full_graph_csv = "data/ucla/cc_edges_ucla.csv"
    needed_grades = ["6", "7", "8"]
    edges, node_posx = extract_graph_from_ucla_json(needed_grades)
    grph = build_cc_dependency_graph(edges, node_posx)

    track_diff = dict()
    for nd in grph.nodes():
        diff = compute_node_difficulty_ancestors(grph, nd)
        track_diff[nd] = diff

    for nd, diff in sorted(track_diff.items(), key=lambda x: x[1]):
        print(f"{nd},{diff}")
