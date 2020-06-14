import pprint

def count_levels_per_student():
    fname = "data/FallSpring16-17_xml_gamelog_data.csv"
    d = dict()
    for line in open(fname):
        name, level, *scores = line.split(",")
        try:
            d[name].append(level)
        except:
            d[name] = [level]

    #for n in d:
    #    print(f"{n} played {len(set(d[n]))} games {len(d[n])} times")

    count_d = {k:len(set(d[k])) for k in d}
    pprint.pprint(sorted(count_d.items(), key=lambda x: x[1], reverse=True)[:])

    #pprint.pprint(sorted(d.items(), key=lambda x: len(set(x[1])), reverse=True)[:4])

def count_students_per_level():
    """
    Top 4 levels:
    [('21ContainerCollect', 21),
     ('22FamilyCollect', 21),
     ('23PlacementTest', 20),
     ('DesertPlacement01', 20)]

    """
    fname = "data/FallSpring16-17_xml_gamelog_data.csv"
    d = dict()
    for line in open(fname):
        name, level, *scores = line.split(",")
        try:
            d[level].append(name)
        except:
            d[level] = [name]

    #for l in d:
    #    print(f"{l} was played by {len(set(d[l]))} students {len(d[l])} times")

    count_d = {k:len(set(d[k])) for k in d}
    pprint.pprint(sorted(count_d.items(), key=lambda x: x[1], reverse=True)[:])

    #print(set(d["21ContainerCollect"]) - set(d['23PlacementTest']))
    #pprint.pprint(sorted(d.items(), key=lambda x: len(set(x[1])), reverse=True)[:4])


if __name__ == "__main__":
    count_levels_per_student()
    print("="*6)
    count_students_per_level()
