"""
Create control file for Netica based on the nodes of EreBuild Bayesian Network.

Format of control file:
IDnum()
bel (Color, red)
bel (Color, blue)
bel (Color, green)
expval (Cost)

For more, visit: https://www.norsys.com/WebHelp/NETICA/X_Process_Cases.htm
"""
from itertools import product

def create_control_file():
    out_f = "data/erebuild_netica_control_file.txt"
    latent = list('abcdefghijklmnopqrstuv')
    states = ["High", "Medium", "Low"]
    with open(out_f, "w") as fp:
        fp.write("IDnum()\n")
        fp.write("\n".join([f"bel ({v}, {st})" for v, st in product(latent, states)]))

if __name__ == "__main__":
    create_control_file()

