import pygraphviz


def visualize_network(network, filename):
    G = pygraphviz.AGraph(directed=True)

    # Get the titles for each competency var
    #comp_vars, _ = get_nodes_relationships()
    #comp_var_title = {var: comp_vars[var]["title"] for var in comp_vars}


    #beliefs = network.predict_proba({})
    #for state, belief in zip(network.states, beliefs):
    for state in network.states:
        #belief = json.loads(belief.to_json())["parameters"][0]

        # More descriptive labels for competency vars
        #if state.name in comp_var_title:
        #    title = comp_var_title[state.name][:15]
        #else:
        #    title = ""

        #label_str = state.name + ":" + title +\
        #            "\n" + "\n".join([f"{k}:{p:.3f}" for k, p in belief.items()])

        #G.add_node(state.name, color='blue', shape="box", label=label_str)
        G.add_node(state.name, color='blue', shape="box", label=state.name)


    for parent, child in network.edges:
        G.add_edge(parent.name, child.name)

    G.draw(filename, format='pdf', prog='dot')

