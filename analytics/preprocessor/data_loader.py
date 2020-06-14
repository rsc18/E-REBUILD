import os

def get_prepost_scores(fname):
    d = dict()
    for line in open(fname):
        if line[0] == "#":
            continue

        name, *vals = line.strip("\n").split(",")
        d[name] = vals

    return d



def consolidate_user_data(fname, pre_post_fname, need_levels):
    """
    Reorganize and consolidate data for each name.

    Args:
        fname:
            The input csv file contains data in the following format:

            name1,level_k,f1,f2,f3,..fk
            name2,level_m,f1,f2,f3,..fm

        need_levels:
            list of levels that we are interested. It also maintains
            the final feature ordering 
    """
    *base, tail = fname.split(os.sep)
    out_fname = os.sep.join(base + [ "consolidated_" + tail])
    out_fp = open(out_fname, "w")

    pre_post = get_prepost_scores(pre_post_fname)

    d = dict()
    for line in open(fname):
        name, level, *features = line.strip("\n").split(",")
        try:
            d[name][level].append(features)
        except KeyError:
            try:
                d[name][level] = [features]
            except:
                d[name] = {level: [features]}

    for name in d:
        skip = False
        vector = [name]
        # maintain order here
        for l in need_levels:
            if l not in d[name]:
                skip = True
                break

            #print(name, l)
            # If there are more entries for a level by a student:
            # Take the average.
            averaged = get_average(d[name][l])
            for v in averaged:
                vector.append(v)

        # Include pre and post scores
        for v in pre_post[name][2:]:
            vector.append(v)

        # write to file
        if not skip:
            out_fp.write(",".join(vector) + "\n")


def get_average(vals_list):
    #print(vals_list)
    n = len(vals_list)
    if n == 1:
        return vals_list[0]

    return [str(sum(float(v) for v in vals) / n) for vals in zip(*vals_list)]


def run_consolidate():
    top_9_levels = [
                    "21ContainerCollect", "22FamilyCollect", "23PlacementTest",
                    "DesertPlacement01", "SchoolPlacement01", "IslandBuild01",
                    "IslandBuildTraining01", "IslandCollect02", "IslandCollect01"
                   ]

    in_csv = "data/data_top_9_levels.txt"
    in_csv = "data/data_top_4_levels.txt"
    prepost_fname = "data/pre_post_test.csv"
    d = get_prepost_scores(prepost_fname)
    consolidate_user_data(in_csv, prepost_fname, top_9_levels[:4])


if __name__ == "__main__":
    run_consolidate()
