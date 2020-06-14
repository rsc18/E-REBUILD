import os
import sys
sys.path.append(os.getcwd())

from lxml import etree
import json
from preprocessor.rules_for_nums_to_category import translate_to_category
from preprocessor.prepost_scores_loader import get_pre_post_scores


def get_ordered_logfiles_per_player():
    fname = "data/chronology_xmllog_per_player.json"
    return json.load(open(fname))

def get_feature_sequence():
    graph_nodes = 'abcdefghijklmnopqrstuv'
    competency_vars = list(graph_nodes)

    observable_vars = ['Angle', 'AssignmentComplete', 'BuildingComplete',
                       'Distance', 'LevelComplete', 'MaterialCredits',
                       'NumAssignments', 'NumBlocks', 'NumFailedAssignments',
                       'NumFamilyCollected', 'NumTrades', 'NumWrong',
                       'Size', 'Time', 'TotalLost']

    return competency_vars + observable_vars


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


def vectorize_xml_log(stu_name, level, xml_path, alpha):
    feature_seq = get_feature_sequence()
    stu_scores = get_pre_post_scores()

    # Initialize all features to empty strings
    hold_features = {feature: "" for feature in feature_seq}

    # Parse XML
    # Get an iterable and turn it into an iterator
    context = iter(etree.iterparse(xml_path, events=("start",)))

    # Get the root element
    event, root = next(context)

    # Convert XML data into a dictionary.
    # This is again for maintaining the order.
    xml_dict = {elem.tag: elem.text for event, elem in context}

    skip = False

    # Add observables
    for k in xml_dict:
        try:
            if xml_dict[k] == "true":
                hold_features[k] = 1
            elif xml_dict[k] == "false":
                hold_features[k] = 0
            else:
                hold_features[k] = xml_dict[k]
        except KeyError:
            if k == "PercentLost":
                hold_features["TotalLost"] = xml_dict[k]
            else:
                print(f"Unidentified Attribute {k} for XML file {xml_path}")
                skip = True

    # Extract pre, post test scores
    stu_math, stu_ratio, stu_geom = get_processed_scores(stu_scores[stu_name])

    hold_features = update_competency_vars(hold_features, stu_ratio, stu_geom, stu_math, update_scheme="top3")

    # Maintain the ordering and make vlaues categorical
    vector = []
    for k in feature_seq:
        if hold_features[k] == "":
            continue
        if len(k) == 1:    # Which means k is a competency variable
            if k in "abh":
                category = translate_to_category(float(hold_features[k]), "posttest", k)
        else:
            category = translate_to_category(float(hold_features[k]), k, level)

        vector.append(category)

    return vector


def get_processed_scores(scores, alpha):
    """
    Return weighted sums of the student scores.

    Args:
        scores: dict
        For dictionary structure, see "preprocessor/prepost_scores_loader.py"

        alpha: float
            Scale to determine how much of pre or post scores are needed.
            If a game was played at alpha position on the time scale,
            final score = alpha * pre + (1- alpha) * post
    """
    post_math = scores["post_math"][1]
    post_ratio = scores["post_ratio"][1]
    post_geom = scores["post_geom"][1]

    pre_math = scores["pre_math"][1]
    pre_ratio = scores["pre_ratio"][1]
    pre_geom = scores["pre_geom"][1]

    math = 0.1 * post_math + 0.9 * pre_math
    ratio = 0.1 * post_ratio + 0.9 * pre_ratio
    geom = 0.1 * post_geom + 0.9 * pre_geom

    return math, ratio, geom


def update_competency_vars(features, pre_ratio, pre_geom, pre_math, update_scheme):
    """
    Three schemes to update competency vars with pretest scores
        1. all: update all competency vars
        2. top3: update only the root and its two children
        3. rand: update all competency vars but at random
        4. none: leave all competency vars empty
    """
    if update_scheme not in ["all", "top3", "rand", "none"]:
        print(f"Incorrect scheme {update_scheme}")
        exit(0)

    if update_scheme == "none":
        return features

    if update_scheme in ["all", "top3", "rand"]:
        features["a"] = pre_math
        features["b"] = pre_ratio
        features["h"] = pre_geom

    if update_scheme == "all":
        for v in "bcdefg":
            features[v] = pre_ratio

        for v in "ijklmnopqrstuv":
            features[v] = pre_geom

    elif update_scheme == "rand":
        if random.random() > 0.7:
            for v in "bcdefg":
                features[v] = pre_ratio

            for v in "ijklmnopqrstuv":
                features[v] = pre_geom

    return features


def gen_train_test_netica_cases():
    ordered_xml_files = get_ordered_logfiles_per_player()

    tr_cases = []
    te_cases = []

    # Lists to keep track of
    tr_tracker = []
    te_tracker = []

    # For each student, keep 80% of their first game plays as training data
    for stu_name in ordered_xml_files:
        _, levels, xml_files = zip(*ordered_xml_files[stu_name])

        # Split gameplays of each student into train/test
        splt = int(0.8 * len(xml_files))
        tr_xml, te_xml = xml_files[:splt], xml_files[splt:]
        tr_lvls, te_lvls = levels[:splt], levels[splt:]

        for xml_path, level in zip(tr_xml, tr_lvls):
            tr_cases.append(vectorize_xml_log(stu_name, level, xml_path))
            tr_tracker.append([stu_name, lvl])

        for xml_path, level in zip(te_xml, te_lvls):
            te_cases.append(vectorize_xml_log(stu_name, xml_path))
            te_tracker.append([stu_name, lvl])

    print(len(tr_cases))

if __name__ == "__main__":
    gen_train_test_netica_cases()
