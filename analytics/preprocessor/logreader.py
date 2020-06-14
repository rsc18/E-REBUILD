import os
from lxml import etree
import pprint

LEVELS_FALL_SPRING_16_17 = [
          '21ContainerCollect', '22FamilyCollect', '23PlacementTest',
          '24BuildPlacement', '26FamilyPlacement', '25FamilyTest',
          '31aCopy', '31bJoin', '41BuildingPlacement',
          '42StudentPlacement', '31cRoof', '43Stadium1',
          '51aAngle', '51Surrond', '52Area',
          'DesertPlacement01', 'SchoolPlacement02', 'SchoolPlacement01',
          'SchoolAssignment01', 'DesertCopy02', 'DesertBuild01',
          'DesertBuild02', 'SchoolBuild01', 'IslandCollect04',
          'IslandBuild02', 'IslandCollect03', 'IslandFill01',
          'DesertCopy01', 'FarmAngle01', 'FarmPerimeter01',
          'FarmVolume01', 'SchoolBuild02', 'IslandBuild01',
          'IslandBuildTraining01', 'IslandFillTraining01', 'IslandCollect02',
          'IslandCollect01']


#because players are using different names every time, we have to unify all variations of names
#to a standard form.
STUDENT_NAMES = {'julia lehman':'julia lehman',
         'jonathan norton':'jonathan norton',
         'jonatinion':'jonathan norton',
         'jonathan':'jonathan norton',
         'isabel cannella':'isabel cannella',
         'isabel':'isabel cannella',
         'isabella':'isabel cannella',
         'drew johnson':'drew johnson',
         'drew':'drew johnson',
         'jojo':'jojo smith',
         'aidan mcarthur':'aidan mcarthur',
         'ashley roorda':'ashley roorda',
         'jonathan anzalone':'jonathan anzalone',
         'caleb schaefer':'caleb schaefer',
         'caleb':'caleb schaefer',
         'stryder campbell':'stryder campbell',
         'stryder':'stryder campbell',
         'wes taylor':'wes taylor',
         'jackson lee':'jackson lee',
         'delonaga madden':'delonaga madden',
         'delonaga':'delonaga madden',
         'josiah miller':'josiah miller',
         'josiah':'josiah miller',
         'sidnee moore':'sidnee moore',
         'sidnee':'sidnee moore',
         'michael roorda':'michael roorda',
         'jonah bridges':'jonah bridges',
         'jonah':'jonah bridges',
         'alexandria glass':'alexandria glass',
         'lexie':'alexandria glass',
         'adah layerd':'adah layerd',
         'tristan carrasquilla':'tristan carrasquilla',
         'tristan':'tristan carrasquilla',
         'paige':'paige campbell'}


def get_xml_files(src_dir):
    for rootdir, subdirs, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith('.xml'):
                yield os.path.join(rootdir, filename)


def get_level_attributes(logdir):
    """
    Given a base directory, parse all the xml files present in it
    and return a dictionary which holds all the XML attribute
    names for a game level.
    """
    level_keys = dict()

    # Debugging purpose: BEGIN
    # To look for mismatches in XML attributes for a single level
    #all_levels = LEVELS_FALL_SPRING_16_17
    #lvl_interest = all_levels[20]
    #prcnt_c = 0
    #total_c = 0

    for xml_path in get_xml_files(logdir):

        # Get an iterable and turn it into an iterator
        context = iter(etree.iterparse(xml_path, events=("start",)))

        # Get the root element
        event, root = next(context)

        # Extract level
        level = root.xpath("Level")[0].text

        # Extract attribute names
        keys_str = ",".join([elem.tag for event, elem in context])

        try:
            level_keys[level].add(keys_str)
        except KeyError:
            level_keys[level] = set([keys_str])

        # Debugging purpose: END
        # To look for mismatches in XML attributes for a single level
        #if level == lvl_interest:
        #    if "PercentLost" in keys_str:
        #        print("PercentLost: ",root.xpath("PercentLost")[0].text)
        #        prcnt_c += 1
        #    elif "TotalLost" in keys_str:
        #        print("TotalLost: ", root.xpath("TotalLost")[0].text)
        #        #print(xml_path)
        #        total_c += 1
            

    #print("\nLevel: %s\nPercentLost count: %d\nTotalLost count: %d\n" %(lvl_interest, prcnt_c, total_c))

    return level_keys


def print_level_xml_attrs(level_keys):
    # Print level followed by the attribute names in that level
    for k, s in level_keys.items():
        for keys_str in s:
            print(k + "," + keys_str)

def load_level_attributes():
    """
    Read a csv file and return a dictionary of level attributes
    indexed by the level name.

    Exceptions:
        1. In case of multiple sets of keys, choose the one with TotalLost
        instead of PercentLost

        2. In case of level SchoolBuild01, choose the one with fewer attributes
    """
    exception_levels = ["SchoolPlacement02", "SchoolPlacement01", "DesertCopy02",
                        "SchoolBuild01", "DesertCopy01", "IslandBuild01",
                        "IslandBuildTraining01"]

    feature_order = dict()
    for line in open("data/attributes_of_gamelevels.csv"):
        level, *attr_names = line.strip("\n").split(",")
        if level in exception_levels:
            if level == "SchoolBuild01" and len(attr_names) == 16:
                continue
            if "PercentLost" in attr_names:
                continue

        feature_order[level] = attr_names

    return feature_order


def parse_gamelogs(logdir, out_fname):
    """
    Given a root directory, recursively find and parse all xml
    files which store the game stats for each student.

    In the meantime, write the parsed content to the given output file.
    """
    *base, tail = logdir.split(os.sep)
    out_fp = open(out_fname, "w")

    # Some levels have different keys for the same
    replacements = {"TotalLost": "PercentLost"}

    # While creating feature vectors, the order of the
    # features should be standardized.
    # Thus, maintain order based on the following file.
    feature_order = load_level_attributes()

    for xml_path in get_xml_files(logdir):
        #print(xml_path)
        # Get an iterable and turn it into an iterator
        context = iter(etree.iterparse(xml_path, events=("start",)))

        # Get the root element
        event, root = next(context)

        # Convert XML data into a dictionary.
        # This is again for maintaining the order.
        xml_dict = {elem.tag: elem.text for event, elem in context}

        # Standardize student name
        xml_dict["Name"] = STUDENT_NAMES[xml_dict["Name"].lower()]
        #print(xml_dict)

        to_write = []
        for attr in feature_order[xml_dict["Level"]]:
            try:
                to_write.append(xml_dict[attr])
            except KeyError:
                to_write.append(xml_dict[replacements[attr]])

        out_fp.write(",".join(to_write) + "\n")

    out_fp.close()


def print_attrs_for_levels():
    d = "from_peyman/FallSpring16-17"
    lvl_attrs = get_level_attributes(d)

    top_9_levels = [
                    "21ContainerCollect", "22FamilyCollect", "23PlacementTest",
                    "DesertPlacement01", "SchoolPlacement01", "IslandBuild01",
                    "IslandBuildTraining01", "IslandCollect02", "IslandCollect01"
                   ]


    for l in top_9_levels:
        print(lvl_attrs[l])



if __name__ == "__main__":
    d = "from_peyman/FallSpring16-17"
    out_f = "data/FallSpring16-17_xml_gamelog_data.csv"
    #parse_gamelogs(d, out_f)

    print_attrs_for_levels()

    """
    lvl_attrs = get_level_attributes(d)
    #print(len(lvl_attrs.keys()))
    print_level_xml_attrs(lvl_attrs)

    k = "IslandBuildTraining01"
    #print(lvl_attrs[k])
    """
