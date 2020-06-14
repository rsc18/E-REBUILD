""" A Q-matrix relates game levels with competency vars.
    Need to relate attributes to competency vars.
"""
import pprint
from collections import defaultdict


def load_gamelevel_attributes(fname):
    level_attrs = dict()
    for line in open(fname):
        if "ercentLost" in line:
            continue

        level, _, _, *attrs = line.strip("\n").split(",")
        level_attrs[level] = attrs

    return level_attrs


def load_qmatrix(fname):
    """
    Comma separated with the first line as the following header:
        level,Level-alias,g,f,e,n,o,p,q,r,s,t,u,v
    """
    q_matrix = {}
    for i, line in enumerate(open(fname)):
        if not i:
            _, _, *var_names = line.strip("\n").split(",")
            continue

        _, level_aliases, *comp_vars = line.strip("\n").split(",")

        if len(level_aliases) > 0:
            if "-" in level_aliases:
                for lvl in level_aliases.split("-"):
                    q_matrix[lvl] = [v for v, val in zip(var_names, comp_vars) if val == "1"]
            else:
                q_matrix[level_aliases] = [v for v, val in zip(var_names, comp_vars) if val == "1"]

    return q_matrix


def get_competency_obs_relation(qmatrix, level_attrs):
    """
    Given qmatrix and the level attributes, return 
    parents for each observable.
    """
    relation = defaultdict(list)
    for lvl, attrs in level_attrs.items():
        for attr in attrs:
            relation[attr] += qmatrix[lvl]

    for k in relation:
        relation[k] = set(relation[k])

    pprint.pprint(dict(relation))


if __name__ == "__main__":
    attr_fname = "data/attributes_of_gamelevels.csv"
    q_fname = "data/qmatrix_level_competency_var.csv"
    lvl_attrs = load_gamelevel_attributes(attr_fname)
    q_matrix = load_qmatrix(q_fname)
    get_competency_obs_relation(q_matrix, lvl_attrs)
