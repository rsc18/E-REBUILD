def rename_node(node):
    """
    Rename only the competency nodes, not the observables.
    Competency nodes start with a digit.

    This is required because Netica doesn't allow node names
    that either start with numbers or have '.' in them.

    """
    if node[0].isdigit():
        return "cc" + node.replace(".", "_")
    else:
        return node

def get_observable_vars():
    """
    Corresponds to the columns in table gameobservables in the erebuild database.
    """
    observable_vars = [
        "Angle",
        "AssignmentComplete",
        "BuildingComplete",
        "Collect",
        "Distance",
        "EmptyInventory",
        "FillArea2D",
        "FillVolume",
        "Fold3D",
        "LevelComplete",
        "LivingArea",
        "MaterialCredits",
        "NumAssignments",
        "NumBlocks",
        "NumFailedAssignments",
        "NumFamilyCollected",
        "NumTrades",
        "NumWrong",
        "Paint",
        "PercentLost",
        "PlaceItems",
        "ProtectFloor",
        "Size",
        "Time",
        "TotalLost"]

    return observable_vars


def get_competency_vars():
    # Standards for which game objectives have been defined in E-Rebuild
    # SQL query on the database "erebuild":
    #     select distinct lo_id from junc_lo_go
    identified_obj = ["6.g.a.1", "6.g.a.2", "6.g.a.4",
        '6.rp.a.3', "7.g.b.4", "7.g.b.5", "7.g.b.6",
        "7.rp.a.3", "8.g.a.1", "8.g.a.2",
        "8.g.a.3", "8.g.c.9"]

    identified_obj = [rename_node(v) for v in identified_obj]

    return identified_obj


def get_bayesnet_node_sequence():
    return get_observable_vars() + get_competency_vars()


def get_observable_edges():
    """
    Based on:

    mysql> select junc_lo_go.lo_id, tbl_game_objectives.name 
      from junc_lo_go 
      join tbl_game_objectives 
      on junc_lo_go.go_id=tbl_game_objectives.id;

    +----------+-----------------+
    | lo_id    | name            |
    +----------+-----------------+
    | 6.G.A.1  | Collect         |
    | 6.G.A.1  | Paint           |
    | 6.G.A.1  | ProtectFloor    |
    | 6.G.A.2  | EmptyInventory  |
    | 6.G.A.2  | FillVolume      |
    | 6.G.A.4  | Fold2D          |
    | 6.G.A.4  | Fold3D          |
    | 6.RP.A.3 | Collect         |
    | 6.RP.A.3 | LivingArea      |
    | 6.RP.A.3 | FillArea2D      |
    | 7.G.B.4  | EmptyInventory  |
    | 7.G.B.4  | LivingArea      |
    | 7.G.B.4  | Paint           |
    | 7.G.B.5  | Angle           |
    | 7.G.B.6  | FillArea2D      |
    | 7.RP.A.3 | Collect         |
    | 8.G.A.1  | PlaceItems      |
    | 8.G.A.1  | WithinTolerance |
    | 8.G.A.2  | PlaceItems      |
    | 8.G.A.3  | Angle           |
    | 8.G.A.3  | Distance        |
    | 8.G.A.3  | MinimumAmount   |
    | 8.G.C.9  | FillVolume      |
    +----------+-----------------+
    23 rows in set (0.05 sec)

    What to do with the observables from the past?
    Attach all to the root node 'math':
        NumBlocks, NumTrades, PercentLost, MaterialCredits, 
        Distance, Size, Angle, BuildingComplete, AssignmentComplete,
        NumAssignments, NumFailedAssignments, NumFamilyCollected, LevelComplete
    """
    edges = [('Collect', '6.g.a.1'),
        ('Paint', '6.g.a.1'),
        ('ProtectFloor', '6.g.a.1'),
        ('EmptyInventory', '6.g.a.2'),
        ('FillVolume', '6.g.a.2'),
        ('Fold2D', '6.g.a.4'),
        ('Fold3D', '6.g.a.4'),
        ('Collect', '6.rp.a.3'),
        ('LivingArea', '6.rp.a.3'),
        ('FillArea2D', '6.rp.a.3'),
        ('EmptyInventory', '7.g.b.4'),
        ('LivingArea', '7.g.b.4'),
        ('Paint', '7.g.b.4'),
        ('Angle', '7.g.b.5'),
        ('FillArea2D', '7.g.b.6'),
        ('Collect', '7.rp.a.3'),
        ('PlaceItems', '8.g.a.1'),
        ('WithinTolerance', '8.g.a.1'),
        ('PlaceItems', '8.g.a.2'),
        ('Angle', '8.g.a.3'),
        ('Distance', '8.g.a.3'),
        ('MinimumAmount', '8.g.a.3'),
        ('FillVolume', '8.g.c.9'),

        ('AssignmentComplete', 'math'),
        ('BuildingComplete', 'math'),
        ('LevelComplete', 'math'),
        ('MaterialCredits', 'math'),
        ('NumBlocks', 'math'),
        ('NumTrades', 'math'),
        ('NumWrong', 'math'),
        ('NumAssignments', 'math'),
        ('NumFailedAssignments', 'math'),
        ('NumFamilyCollected', 'math'),
        ('PercentLost', 'math'),
        ('Size', 'math'),
        ('Time', 'math'),
        ('TotalLost', 'math')
        ]


    return edges



