nodes = """solve_math
reason_ratio 
solve_real 
solve_ratio 
solve_multistep_ratio 
solve_area_vol_2d 
solve_area_vol_3d 
compute_angle 
compare_ratio 
solve_unit_rate 
recognize_prop 
represent_prop_table 
represent_prop_equation 
compute_area_2d 
compute_vol_prism 
compute_circle_area 
solve_unit_price 
convert_units 
compute_area_circum_triangle 
compute_volume_right_prism 
comprehend_ratio_rel 
calc_unit_rate 
solve_whole 
time_taken 
assignment_operation 
build_blocks_bought 
num_trades 
total_lost 
distance 
size 
angle 
build_complete 
assignment_complete
"""

comments = """# top: Solve all Maths problem
# left0: reason Math with ratio
# right0:  real world math
# left1a: solve real world maths with ratio
# left1b: solve multistep ratio
# right1a: solve area, volume
# right1b: solve area, volume 3D
# right1c: compute angle
# left2a: Compare ratios with whole numbers
# left2b: Solve unit rate
# left2c: Recognize proportional relationship
# left2d: Represent proportional relationship by table
# left2e: Represent proportional relationship by equation
# right2a: Compute area of triangles, quads
# right2b: Compute volume right rectangular prism
# right2c: Compute area, circumference of circle
# left3a: Solve problems involving unit price
# left3b: Convert measurement units using ratios
# right3a: Compute area circumference of triangles. Don't need!
# right3b: Compute volume of right rectangular prism. Don't need!
# left4a: Comprehend ratio relationship via numeric
# left4b: Calculate unit rate
# left4c: Solve problems involving finding the whole
# left5a: Time
# left5b: Assignment Operation
# left5c: No. of building blocks bought
# left5d: No. of trades
# left5e: total lost in trade
# right5a: distance
# right5b: size
# right5c: Angle
# right5d: Building completed
# right5d: Assignemnt completed
"""

nodes = nodes.split("\n")[:-1]
comments = comments.split("\n")[:-1]

for i, (node, comment) in enumerate(zip(nodes, comments)):
    node = node.strip()
    print(f"st_{node} = State( {node}, name=\"{node}\" )  {comment}")

print("\n\tPrinting States\n")
print(", ".join(["st_" + n for n in nodes]))


print("\n\tPrinting Edge assignments\n")
import re

assignments = """reason_ratio = init_cpt([solve_math])
solve_real = init_cpt([solve_math])
solve_ratio = init_cpt([reason_ratio])
solve_multistep_ratio = init_cpt([reason_ratio])
solve_area_vol_2d = init_cpt([solve_real])
solve_area_vol_3d = init_cpt([solve_real])
compute_angle = init_cpt([solve_real])
compare_ratio = init_cpt([solve_ratio])
solve_unit_rate = init_cpt([solve_ratio])
recognize_prop = init_cpt([solve_multistep_ratio])
represent_prop_table = init_cpt([solve_multistep_ratio])
represent_prop_equation = init_cpt([solve_multistep_ratio])
compute_area_2d = init_cpt([solve_area_vol_2d])
compute_vol_prism = init_cpt([solve_area_vol_2d])
compute_circle_area = init_cpt([solve_area_vol_3d])
solve_unit_price = init_cpt([solve_unit_rate])
convert_units = init_cpt([solve_unit_rate])
compute_area_circum_triangle = init_cpt([compute_area_2d])
compute_volume_right_prism = init_cpt([compute_vol_prism])
comprehend_ratio_rel = init_cpt([compare_ratio, solve_unit_rate])
calc_unit_rate = init_cpt([solve_unit_price, convert_units])
solve_whole = init_cpt([solve_unit_price])
time_taken = init_cpt([reason_ratio])
assignment_operation = init_cpt([comprehend_ratio_rel])
build_blocks_bought = init_cpt([comprehend_ratio_rel])
num_trades = init_cpt([comprehend_ratio_rel])
total_lost = init_cpt([calc_unit_rate, solve_whole])
distance = init_cpt([solve_math])
size = init_cpt([compute_area_circum_triangle, compute_circle_area])
angle = init_cpt([compute_angle])
build_complete = init_cpt([solve_math], ["True", "False"])
assignment_complete = init_cpt([compute_area_circum_triangle, compute_circle_area, compute_volume_right_prism], ["True", "False"])
"""

assignments = assignments.split("\n")[:-1]
patc = re.compile(r"\[(.*?)\]")  # to capture contents in the first list
for line in assignments:
    child, rest = line.split(" = ")
    parents = patc.search(rest).group(1).split(",")
    c = child.strip()
    for parent in parents:
        p = "st_" + parent.strip()
        print(f"network.add_edge({p}, {c})")
