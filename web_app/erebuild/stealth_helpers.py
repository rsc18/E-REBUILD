import random
import json
import os
from flask import g
from networkx.readwrite import json_graph
import networkx as nx

def translate_to_category(attr_val, attr_name, level=None):
    ranges = {
        "Angle": lambda x: 3 if x < 11.25 else 2 if 11.25 <= x < 33.75 else 1,
        "AssignmentComplete": lambda x: 3 if x == 1 else 1,
        "BuildingComplete": lambda x: 3 if x == 1 else 1,
        "Distance": lambda x: 3 if x < 5 else 2 if 5 <= x < 15 else 1,
        "LevelComplete": lambda x: 3 if x == 1 else 1,
        "MaterialsCredits": lambda x: 3 if x > 8000 else 2 if 2000 <= x <= 8000 else 1,
        "NumAssignments": lambda x: 3 if x <= 15 else 2 if 15 < x <= 22 else 1,
        "NumBlocks":
            {"43Stadium1": lambda x: 3 if 93.75 <= x < 106.25 else 2 if (106.25 <= x < 118.75) or (81.25 <= x < 93.75) else 1,
             "Stadium2": lambda x: 3 if 187.5 <= x < 212.5 else 2 if (212.5 <= x < 237.5) or (162.5 <= x < 187.5) else 1,
             "IslandBuild01": lambda x: 3 if x <= 5 else 1,
             "IslandBuild02": lambda x: 3 if x <= 5 else 1,
             "IslandBuild03": lambda x: 3 if x <= 5 else 1,
             "SchoolBuild": lambda x: 3 if x <= 5 else 1,
             "default": lambda x: 3 if x <= 5 else 1,
            },
        "NumFailedAssignments": lambda x: 3 if x <= 2 else 2 if 2 < x <= 4 else 1,
        "NumFamilyCollected": lambda x: 3 if x <= 2 else 2 if 2 < x <= 4 else 1,
        "NumTrades": lambda x: 3 if x <= 2 else 2 if 2 < x < 5 else 1,
        "NumWrong": lambda x: 3 if x <= 1 else 2 if 1 < x < 3 else 1,
        "Size": lambda x: 3 if x < 10 else 2 if 10 <= x < 20 else 1,
        "Time": lambda x: 3 if x < 200 else 2 if 200 <= x < 500 else 1,
        "TotalLost": lambda x: 3 if x > -10 else 2 if -150 <= x < -10 else 1,
        "pretest":
            {"pre_math": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "pre_ratio": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "pre_geom":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "defaut": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            },
        "posttest":
            {"post_math": lambda x: 3 if x >= 54.2 else 2 if 22.8 <= x < 54.2 else 1,
             "post_ratio": lambda x: 3 if x >= 69.4 else 2 if 31.8 <= x < 69.4 else 1,
             "post_geom":lambda x: 3 if x >= 41.47 else 2 if 3.53 <= x < 41.47 else 1,
             "defaut": lambda x: 3 if x >= 66.7 else 2 if 33.3 <= x < 66.7 else 1
            }
        }

    alpha_cat = {1: "Low", 2: "Medium", 3: "High"}

    try:
        cat = ranges[attr_name](attr_val)
    except:
        cat = ranges[attr_name][level](attr_val)

    return alpha_cat[cat]


def prepare_json_for_trajectory_plot(data):
    """
    Clean and augment the competency data.

    1. We used a, b, c, d, ..., n as node names in the bayesian network.
       Replace them with their corresponding common core standard names.

    2. Competency for each common core standard will have additional info:
       (a) x, y coordinates for displaying.
       (b) Summary of the competency.

       Example json:
       {
         "nodes":
         [
           {id: "6.rp.4", summary: "ratio proportion 4", competency: 0.8, objectives: [{id: "1"}, {id: "2"}],
            "x_": 0.1, "y_": 0.5
           },
           {id: "6.rp.5", summary: "ratio proportion 5", competency: 0.6, objectives: [{id: "1"}, {id: "2"}],
           "x_": 0.3, "y_": 0.1
           },
           {id: "6.g.5", summary: "geometry 5", competency: 0.4, objectives: [{id: "1"}, {id: "2"}],
           "x_": 0.3, "y_": 0.6
           },
           {id: "6.rp.7", summary: "ratio proportion 7", competency: 0.4, objectives: [{id: "1"}, {id: "2"}],
           "x_": 0.5, "y_": 0.5
           },
         ],
         "links":
         [
           {source: 0, target: 1},
           {source: 1, target: 2},
           {source: 0, target: 3},
           {source: 0, target: 2},
         ]
       }
    """

    nodes_list = [
        {"id": "6.g.a.1",
         "bayesnet_name": "",
         "summary": "Edit Test Find the area of right triangles, other triangles, " +\
                    "special quadrilaterals, and polygons by composing into rectangles " +\
                    "or decomposing into triangles and other shapes; " +\
                    "apply these techniques in the context of solving real-world and mathematicalproblems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.1,
         "y_": 0.1
        },
        {"id": "6.g.a.2",
         "bayesnet_name": "",
         "summary": "Find the volume of a right rectangular prism with fractional edge lengths " +\
                          "by packing it with unit cubes of the appropriate unit " +\
                          "fraction edge lengths, and show that the volume is the same " +\
                          "as would be found by multiplying the edge lengths of the prism. " +\
                          "Apply the formulas V = l w h and V = b h to find volumes of right rectangular " +\
                          "prisms with fractional edge lengths in the context of solving " +\
                          "real-world and mathematical problems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.1,
         "y_": 0.8
        },
        {"id": "6.g.a.4",
         "bayesnet_name": "",
         "summary": "Represent three-dimensional figures using nets made up of rectangles and triangles, " +\
                    "and use the nets to find the surface area of these figures. Apply these techniques " +\
                    "in the context of solving real-world and mathematical problems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.1,
         "y_": 0.5
        },
        {"id": "6.rp.a.3",
         "bayesnet_name": "",
         "summary": "Draw polygons in the coordinate plane given coordinates for the vertices; use coordinates " +\
                    "to find the length of a side joining points with the same first coordinate or the same " +\
                    "second coordinate. Apply these techniques in the context of solving real-world " +\
                    "and mathematical problems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.3,
         "y_": 0.5
        },
        {"id": "7.g.b.4",
         "bayesnet_name": "",
         "summary": "Know the formulas for the area and circumference of a circle and " +\
                    "use them to solve problems; give an informal derivation of the " +\
                    "relationship between the circumference and area of a circle.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.4,
         "y_": 0.1
        },
        {"id": "7.g.b.5",
         "bayesnet_name": "",
         "summary": "Use facts about supplementary, complementary, vertical, and adjacent angles " +\
                    "in a multi-step problem to write and solve simple equations for an unknown " +\
                    "angle in a figure.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.5,
         "y_": 0.5
        },
        {"id": "7.g.b.6",
         "bayesnet_name": "",
         "summary": "Solve real-world and mathematical problems involving area, " +\
                    "volume and surface area of two- and three-dimensional objects " +\
                    "composed of triangles, quadrilaterals, polygons, cubes, and right prisms.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.4,
         "y_": 0.8
        },
        {"id": "7.rp.a.1",
         "bayesnet_name": "",
         "summary": "Compute unit rates associated with ratios of fractions, including " +\
                    "ratios of lengths, areas and other quantities measured in like or " +\
                    "different units.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.6,
         "y_": 0.8
        },
        {"id": "7.rp.a.3",
         "bayesnet_name": "",
         "summary": "Use proportional relationships to solve multistep ratio and percent problems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.6,
         "y_": 0.3
        },
        {"id": "8.g.a.1",
         "bayesnet_name": "",
         "summary": "Verify experimentally the properties of rotations, reflections, and translations",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.8,
         "y_": 0.3
        },
        {"id": "8.g.a.2",
         "bayesnet_name": "",
         "summary": "Understand that a two-dimensional figure is congruent to another if the second can be obtained from the first by a sequence of rotations, reflections, and translations; given two congruent figures, describe a sequence that exhibits the congruence between them.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.8,
         "y_": 0.8
        },
        {"id": "8.g.a.3",
         "bayesnet_name": "",
         "summary": "Describe the effect of dilations, translations, rotations, and reflections on two-dimensional figures using coordinates.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.8,
         "y_": 0.5
        },
        {"id": "8.g.c.9",
         "bayesnet_name": "",
         "summary": "Know the formulas for the volumes of cones, cylinders, and spheres and use them to " +\
                    "solve real-world and mathematical problems.",
         "competency": random.random(),
         "objectives": [],
         "x_": 0.8,
         "y_": 0.1
        },
      ]

    # map node id with node index in the list
    nd_idx = {node["id"]: i for i, node in enumerate(nodes_list)}

    # Edges
    links_list = [
        {"source": nd_idx["8.g.a.1"], "target": nd_idx["8.g.a.3"]},
        {"source": nd_idx["8.g.a.3"], "target": nd_idx["8.g.a.2"]},
        {"source": nd_idx["6.g.a.1"], "target": nd_idx["6.g.a.4"]},
        {"source": nd_idx["6.g.a.1"], "target": nd_idx["7.g.b.4"]},
        {"source": nd_idx["6.g.a.2"], "target": nd_idx["7.g.b.6"]},
        {"source": nd_idx["6.g.a.4"], "target": nd_idx["7.g.b.6"]},
        {"source": nd_idx["7.g.b.4"], "target": nd_idx["8.g.c.9"]},
    ]

    # Json for the trajectory graph
    traj_json = {
      "nodes": nodes_list,
      "links": links_list
    }

    return json.dumps(traj_json)


def load_partial_learning_trajectory():
    trj_part = getattr(g, '_trajectory_partial', None)
    if trj_part is None:
        json_dir = "db_jsons"
        jsn_fn = os.path.join(json_dir, "layout_trajectory_partial.json")

        with open(jsn_fn) as fp:
            grph_data = json.load(fp)

        trj_part = json_graph.node_link_graph(grph_data)
        #trj_part = nx.node_link_graph(grph_data)

        g._trajectory_partial = trj_part
        #print(trj_part)

    return trj_part


def insert_competency_into_trajectory(trj_part, competency, unlocked_nodes):
    """
    Given a trajectory layout as a networkx graph, add competency
    information to each node. data holds the competency info.

    Few cases to take care of:
        1. Always unlock the starting competencies
            Those grade 6 nodes which do not have any parents.

        2. If a user satisfies a competency once, always unlock it
            for them.

    Args:
        trj_part: networkx 1.11 DiGraph

        competency: either JSON string or a dictionary

        unlocked_nodes: list of competency node names
    """
    if isinstance(competency, str):
        competency = json.loads(competency)

    for k in trj_part.nodes():
        # Pull out probability and category from student's competency data
        #category = random.choice(["High", "Medium", "Low"])
        #prob = random.random()

        # competency can be empty if the user hasn't played any game yet
        if k not in competency:
            trj_part.node[k]["competency"] = -1
            trj_part.node[k]["competency_distribution"] = {"High": -1, "Medium": -1, "Low": -1}
        else:
            if k in unlocked_nodes:
                trj_part.node[k]["competency"] = 1
            else:
                trj_part.node[k]["competency"] = int(is_unlocked(k, competency[k]))

            trj_part.node[k]["competency_distribution"] = competency[k]

    # d3 format
    #trj_d3 = nx.node_link_data(trj_part)
    trj_d3 = json_graph.node_link_data(trj_part)

    # Since d3 takes index positions as source and target for the links,
    # replace the node ids with positions.
    #nd_idx = {k: i for i, k in enumerate(trj_part.nodes())}

    #for i, link in enumerate(trj_d3["links"]):
    #    link["source"] = nd_idx[link["source"]]
    #    link["target"] = nd_idx[link["target"]]

    # get json for the graph
    trj_d3_json = json.dumps(trj_d3)

    #with open("trajectory_json_spring_layout_node_pos.json", "w") as fp:
    #    fp.write(trj_d3_json)

    return trj_d3_json


def is_unlocked(node_name, node_competency):
    """
    Check if a player is competent in a Maths standard (competency node)
    based on the probability scores for each category (High, Medium and Low)
    given by the Bayesian Network.
    """
    if node_competency["High"] >= 0.5 or node_competency["Medium"] >= 0.5:
        return True

    return False

