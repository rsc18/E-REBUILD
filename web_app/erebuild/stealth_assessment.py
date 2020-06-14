from flask import Flask, Blueprint, request, session, g, redirect, url_for, abort, \
    render_template, flash, send_from_directory, jsonify, make_response

import json
import random
from datetime import datetime
import pandas as pd

from erebuild.database_helpers import insert_observables
from erebuild.database_helpers import insert_competencies
from erebuild.database_helpers import get_latest_user_competency
from erebuild.bayesnet_helpers import save_latest_user_bayesnet
from erebuild.bayesnet_helpers import get_latest_user_bayesnet
from erebuild.database_helpers import get_data_level_go
from erebuild.database_helpers import get_data_level
from erebuild.database_helpers import get_go_details

from erebuild.stealth_helpers import translate_to_category
from erebuild.stealth_helpers import load_partial_learning_trajectory
from erebuild.stealth_helpers import insert_competency_into_trajectory

flag = 0

erebuild_stealth = Blueprint("erebuild_stealth", __name__)

data_level = get_data_level()
data_go_detail = get_go_details()
data_level_go = get_data_level_go()

if flag == 1:
    print("inside stealth assessment\n")
    print(data_level)
    print(data_go_detail)
    print(data_level_go)

dict_level_id_name = dict(zip(data_level.level_id, data_level.name))
dict_go_id_name = dict(zip(data_go_detail.id, data_go_detail.name))
data_level_go['level_name'] = data_level_go['level_id'].apply(lambda x: dict_level_id_name[x])
data_level_go['go_name'] = data_level_go['go_id'].apply(lambda x: dict_go_id_name[x])


def level_go(level):
    return list(data_level_go.loc[data_level_go['level_name'] == level].go_name)


@erebuild_stealth.route('/assessment/game', methods=['POST'])
def process_observables():
    # if not(session["logged_in"] and session["is_user"]):
    #    return redirect(url_for("erebuild_land.landing_page"))

    # Extract form data as a dictionary
    obs = request.form.to_dict(flat=True)

    # In case it was sent as a json
    if len(obs) == 0:
        obs = request.get_json()

    # Extract the time sent by client. If not, consider the current time
    dtime = obs.get("play_time", datetime.utcnow())
    userid = obs["user_email"]
    request_type = obs["request_type"]

    # Check if the request is to simply get the progress map
    # or it's to get predictions after the game level ends.
    # Progress map is for in-game display only.
    if request_type == "progress_map":
        # Simply load the competency from the database
        competency = get_latest_user_competency(userid)

        # nodes that are supposed to be always unlocked since they don't have
        # any pre-requisites.
        unlocked_nodes = ["cc8_g_1", "cc6_g_1", "cc6_g_2", "cc7_g_5", "cc7_rp_3"]

    # Otherwise, the player has finished a game level and the post request
    # contains game observables for that level. So, we need to assess the student
    # competency based on this set of game observables.
    else:
        levelid = obs["game_level"]

        # Remove unwanted key from observations
        obs.pop('game_level', None)
        obs.pop('user_email', None)
        obs.pop('request_type', None)

        # Insert observables to database
        insert_observables(userid, levelid, obs)

        # Translate real observables to catgorical
        cat = {k: translate_to_category(float(val), k, levelid) for k, val in obs.items()}

        for k, v in cat.items():
            if (v == "High"):
                v = 'H'
            elif (v == 'Low'):
                v = 'L'
            else:
                v = 'M'
            cat[k] = v

        # Obtain the trained bayesnet for the user
        bayesnet = get_latest_user_bayesnet(userid)



        aa = []
        for k in bayesnet.states:
            if ('_obs' in k.name):
                aa.append(k.name)
        print(aa)
        newcat = {}
        level_name = dict_level_id_name[int(levelid)]
        go_name = level_go(level_name)

        for k, v in cat.items():
            for gn in go_name:
                ## ## There are some game levels where we have game objectives not mentioned in bayesian network
                ## ## in that case only take game objective that are defined in network
                if ('go_' + gn + '_obs_' + k) not in aa:
                    continue
                newcat['go_' + gn + '_obs_' + k] = v
                print(newcat)

        competency = dict()
        print("\n")
        print(newcat)
        print("\n")
        if (newcat != {}):
            # Perform prediction
            beliefs = bayesnet.predict_proba(newcat)

            # Extract marginals for each competency variable

            for st, bel in zip(bayesnet.states, beliefs):
                # Skip if it's not a competency variable
                try:
                    competency[st.name] = json.loads(bel.to_json())["parameters"][0]
                except AttributeError:
                    continue

            # insert competency to database
            insert_competencies(userid, levelid, dtime, competency)

            # Update the user's bayesian network model
            # First, prepare the data. Replace unknowns with None.
            data = [newcat[k.name] if k.name in newcat else None for k in bayesnet.states]

            # Fill in the missing data since only a subset of observables are known.
            data = bayesnet.predict([data])

            # Finally, fit the network to the data
            bayesnet = bayesnet.fit(data, inertia=0.1)

            # Save bayesnet for the user

            save_latest_user_bayesnet(userid, bayesnet)
            # Trajectory presented to the teachers should show competencies of
            # all the nodes even though they don't have any pre-requisite.
        unlocked_nodes = []

    # Send Competency JSON to Unity to update the "My Progress" graph
    # Partial learning trajectory
    trj_part = load_partial_learning_trajectory()

    # Populate the partial learning trajectory with competency data
    trj = insert_competency_into_trajectory(trj_part, competency, unlocked_nodes)

    return trj
    # return jsonify(competency)


@erebuild_stealth.route('/assessment/game/<level>')
def offer_gamelevel(level):
    return render_template("game_offer.html", user="user_email", gamelevel=level)

    # if session["logged_in"] and session["is_user"]:
    #    return render_template("game_offer.html", user=session["user_email"], gamelevel=level)
    # else:
    #    return redirect(url_for("erebuild_land.landing_page"))
