"""
    Module to prepare Learning Trajectory for a student.

    Needed data, files, database tables:
        1. junc_level_go.json
            Maps game level id with the game objective id.
            Each node in the trajectory should list the game levels.

        2. junc_lo_go.json
            Maps Common Core Standard with its corresponding game objectives.

        3. layout_trajectory_empty.json
           Bayesian Network given by the following program which is saved as a json file
           with only the edges connecting competency nodes.

               Program: ../bayesnet_trajectory_from_ucla_cc_map.py

            To run the program:
            1. change directory to erebuild_stealth.
            2. python bayesnet_trajectory_from_ucla_cc_map.py --type trajectory --out_file learning_trajectory/db_jsons/layout_trajectory_empty.json

           Note: take care of how the nodes have been named in bayesnet_node_info.py


    Method to draw learning trajectory
        1. Trajectory layout comes from the Bayesian Network.
        2. Since junc_lo_go.json maps CC standards with game objectives:
            (a) Use predictions from trained Bayesian Network to evaluate
                competency for each node (i.e. CC standard).

            (b) Compute color code for the node to denote competency pass (or fail)
                Pass only when category = High with probability >= 0.5.

        3. 
            # Return data in node-link format
            # 1. suitable for JSON serialization
            # 2. can be used in Javascript documents
            nx.node_link_data(graph)
"""

import os
import numpy as np
import networkx as nx
from networkx.readwrite import json_graph
import json
from collections import defaultdict
import itertools


# Use networkx version 1.11
# Comes packaged with pomegranate
assert nx.__version__ == '1.11', f"networkx: pomegranate needs 1.11 but found {nx.__version__}"


def get_pygraphviz_pos(grph):
    # Get a graphviz graph and add ranks to nodes
    agrph = nx.nx_agraph.to_agraph(grph)
    #print([nd for nd in grph.nodes() if nd[0] == "6"])

    #a = agrph.add_subgraph([nd for nd in grph.nodes() if nd[0] == "6"], rank='same')
    #b = agrph.add_subgraph([nd for nd in grph.nodes() if nd[0] == "7"], rank='same')
    #c = agrph.add_subgraph([nd for nd in grph.nodes() if nd[0] == "8"], rank='same')

    # give the same rank to all nodes that don't have any incoming edges
    level_1st = [nd for nd in grph.nodes() if grph.in_degree(nd) == 0]
    level_last = [nd for nd in grph.nodes() if grph.out_degree(nd) == 0]
    level_mid = [nd for nd in grph.nodes() if nd not in level_1st + level_last]

    print("1st level: ", level_1st)
    print("mid level: ", level_mid)
    print("last level: ", level_last)

    a = agrph.add_subgraph(level_1st, rank='same')
    b = agrph.add_subgraph(level_mid, rank='same')
    c = agrph.add_subgraph(level_last, rank='same')

    # Convert it back to networkx graph
    grph = nx.nx_agraph.from_agraph(agrph)

    # For arguments, see: https://www.graphviz.org/doc/info/attrs.html
    arg_string = "-Gorientation=landscape \
                  -Goverlap=prism \
                  -Gnodesep=0.0 \
                  -Grankdir=LR"


    pos = nx.nx_agraph.pygraphviz_layout(grph, prog="dot", args=arg_string)
    #pos = nx.nx_agraph.pygraphviz_layout(grph)

    return pos


def hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5,
                  pos = None, parent = None):
    '''
    If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch.

    Source: https://stackoverflow.com/a/29597209
    '''
    if pos == None:
        pos = {root:(xcenter,vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    neighbors = list(G.neighbors(root)) 
    #print(root, neighbors)
    #if parent != None:   #this should be removed for directed graphs.
    #    print(parent)
    #    neighbors.remove(parent)  #if directed, then parent not in neighbors.
    if len(neighbors)!=0:
        dx = width/len(neighbors) 
        nextx = xcenter - width/2 - dx/2
        for neighbor in neighbors:
            nextx += dx
            pos = hierarchy_pos(G,neighbor, width = dx, vert_gap = vert_gap, 
                                vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                parent = root)
    return pos


def get_game_levels_for_cc():
    """
    Return the game levels associated with each Common Core Standard.
    """
    # Load json that maps Common Core Standard with its game objectives.
    jsn_cc_fn = os.path.join("db_jsons", "junc_lo_go.json")
    with open(jsn_cc_fn) as fp:
        cc_to_obj = defaultdict(list)
        for row in json.load(fp)[2]["data"]:
            cc_to_obj[row["lo_id"]].append(row["go_id"])

    # Load json that maps game level id with game objectives.
    jsn_lvl_fn = os.path.join("db_jsons", "junc_level_go.json")
    with open(jsn_lvl_fn) as fp:
        obj_to_level = defaultdict(list)
        for row in json.load(fp)[2]["data"]:
            obj_to_level[row["go_id"]].append(row["level_id"])

    # Map CC standard with game levels
    cc_to_level = defaultdict(list)
    for cc in cc_to_obj:
        for obj in cc_to_obj[cc]:
            cc_to_level[cc.lower()] += obj_to_level[obj]

    # Add a dummy level to the final node
    cc_to_level["math"] = ["1000"]

    for k in cc_to_level:
        print(k, cc_to_level[k])

    return cc_to_level


def get_summary_for_cc():
    fn = os.path.join("db_jsons", "tbl_learning_objectives.json")
    with open(fn) as fp:
        summary = defaultdict(str)
        for row in json.load(fp)[2]["data"]:
            summary[row["id"].lower()] = row["description"]

    return summary


def normalize_pos(pos):
    """
    Given a dictionary of positions for each node in the graph,
    normalize x, y coordinate positions to be between 0 and 1.
    """
    # Extract all pos
    n = len(pos.keys())
    all_pos = np.zeros((n, 2))
    for i, k in enumerate(pos):
        all_pos[i] = pos[k]

    xy_min = np.min(all_pos, axis=0)
    xy_max = np.max(all_pos, axis=0)

    # Normalize each
    for k in pos:
        pos[k] = (pos[k] - xy_min) / (xy_max - xy_min)

    return pos


def drop_incomplete_competencies(grph, game_levels):
    # If a node doesn't have any game levels assigned to it,
    # delete it and join it's ancestor with its successors.
    nodes = list(grph.nodes())
    for k in nodes:
        if len(game_levels[k]) == 0 and k in grph.nodes():
            parents = grph.predecessors(k)
            chldrn = grph.successors(k)

            for u, v in itertools.product(parents, chldrn):
                grph.add_edge(u, v)

            grph.remove_node(k)

    return grph


def drop_redundant_edges(grph):
    target = "math"
    for nd in grph.nodes():
        if grph.has_edge(nd, target):
            paths = list(nx.all_simple_paths(grph, nd, target))
            if len(paths) >= 2 and len(max(paths, key=lambda x: len(x))) > 2:
                grph.remove_edge(nd, target)

    return grph


def get_trajectory_layout():
    # Load graph from json that holds the Bayesnet.
    # It has no observables.
    fn = os.path.join("db_jsons", "layout_trajectory_empty.json")
    with open(fn) as fp:
        grph_data = json.load(fp)

    grph = json_graph.node_link_graph(grph_data)
    #grph = nx.node_link_graph(grph_data)
    print(list(grph.nodes()))

    # Get game level information
    game_levels = get_game_levels_for_cc()

    # Clean the graph.
    grph = drop_incomplete_competencies(grph, game_levels)
    grph = drop_redundant_edges(grph)

    # Get 2D coordinates for each node. It is needed during display.
    pos = get_pygraphviz_pos(grph)
    pos = normalize_pos(pos)

    # Get summary
    summary = get_summary_for_cc()

    for k in grph.nodes():
        grph.node[k]["x_"], grph.node[k]["y_"] = pos[k].ravel().tolist()
        grph.node[k]["game_levels"] = game_levels[k]
        grph.node[k]["summary"] = summary[k]
        #print(k, grph.nodes[k])

    return grph


if __name__ == "__main__":
    grph = get_trajectory_layout()


    grph_jsn = json_graph.node_link_data(grph)

    fn = os.path.join("db_jsons", "layout_trajectory_partial.json")
    with open(fn, "w") as write_file:
        json.dump(grph_jsn, write_file)

    print("*" * 5)
    print("To use this json file in the web app, copy to erebuild_stealth/web_app/db_jsons")
    print("*" * 5)
