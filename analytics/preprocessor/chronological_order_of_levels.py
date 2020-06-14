import os
from lxml import etree
import pprint
import sys
import random
from datetime import datetime
from collections import defaultdict
import json

def get_correct_names():
    """
    Map erroneous names to the correct ones.
    """
    corrections = {
         'jonatinion':'jonathan norton',
         'jonathan':'jonathan norton',
         'isabel':'isabel cannella',
         'isabella':'isabel cannella',
         'drew':'drew johnson',
         'jojo':'jojo smith',
         'caleb':'caleb schaefer',
         'stryder':'stryder campbell',
         'delonaga':'delonaga madden',
         'josiah':'josiah miller',
         'sidnee':'sidnee moore',
         'jonah':'jonah bridges',
         'lexie':'alexandria glass',
         'tristan':'tristan carrasquilla',
         'paige':'paige campbell'}

    return corrections


def get_xml_files(src_dir):
    """
    Given a source directory, yield all XML file paths in the directory.
    """
    for rootdir, subdirs, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith('.xml'):
                yield os.path.join(rootdir, filename)


def get_stu_name_level_from_xml(xml_path):
    name_corrections = get_correct_names()

    # Parse XML
    # Get an iterable and turn it into an iterator
    context = iter(etree.iterparse(xml_path, events=("start",)))

    # Get the root element
    event, root = next(context)

    # Convert XML data into a dictionary.
    # This is again for maintaining the order.
    xml_dict = {elem.tag: elem.text for event, elem in context}

    # get correct student name
    stu_name = xml_dict["Name"].lower()
    try:
        stu_name = name_corrections[stu_name]
    except KeyError:
        pass

    level = xml_dict["Level"]

    return stu_name, level


def order_levels_per_player_chronology(src_dir):
    ordering = defaultdict(list)

    for xml_path in get_xml_files(src_dir):
        # Extract date and time from filename
        dt = "-".join(xml_path.split(".")[0].split("/")[-1].split("_")[-2:])
        time_units = [int(v) for v in dt.split("-")]

        # Extract student name and the level name
        stu_name, level = get_stu_name_level_from_xml(xml_path)

        ordering[stu_name].append((time_units, level))

    # Sort
    stu_names = ordering.keys()
    for stu in stu_names:
        ordering[stu] = sorted(ordering[stu], key=lambda x: datetime(*x[0]))

    return ordering


def order_logfile_per_player_chronology(src_dir):
    ordering = defaultdict(list)

    for xml_path in get_xml_files(src_dir):
        # Extract date and time from filename
        dt = "-".join(xml_path.split(".")[0].split("/")[-1].split("_")[-2:])
        time_units = [int(v) for v in dt.split("-")]

        # Extract student name and the level name
        stu_name, level = get_stu_name_level_from_xml(xml_path)

        ordering[stu_name].append((time_units, level, xml_path))

    # Sort
    stu_names = ordering.keys()
    for stu in stu_names:
        ordering[stu] = sorted(ordering[stu], key=lambda x: datetime(*x[0]))

    return ordering



def main():
    src_dir = "from_peyman/FallSpring16-17"
    #ordering = order_levels_per_player_chronology(src_dir)
    #out_json = f"data/chronology_per_player.json"
    #with open(out_json, 'w') as outfile:
    #    json.dump(ordering, outfile)

    ordering = order_logfile_per_player_chronology(src_dir)
    out_json = f"data/chronology_xmllog_per_player.json"
    with open(out_json, 'w') as outfile:
        json.dump(ordering, outfile)


if __name__ == "__main__":
    main()
