from erebuild import E_DB
from flask import g, session
import json
import os
from datetime import datetime
import glob
from erebuild.database_models import LatestBayesNet
from pomegranate import BayesianNetwork


def get_latest_user_bayesnet(user_email):
    """
    Query the database to retrieve the user's saved BayesNet model.
    If no such model exists, return the global Bayesian Network.

    A pemegranate Bayesian Network object is returned.
    """
    entry = LatestBayesNet.query.filter_by(user_email=user_email).first()
    if entry is None:
        #user_bnet = get_global_bayesnet()
        bnet_dir = "Models"
        global_f = glob.glob(f"{bnet_dir}{os.sep}global_bayesnet.json")[0]
        user_bnet = load_bayesnet(global_f)
    else:
        user_bnet = BayesianNetwork.from_json(entry.bayesnet)

    return user_bnet


def save_latest_user_bayesnet(user_email, user_bnet):
    """
    Save the given most recent bayesian Network for the user.
    """
    # jsonify the bayesnet
    user_bnet = user_bnet.to_json()
    user_bnet = user_bnet.replace(" ", "").replace("\n", "")

    entry = LatestBayesNet.query.filter_by(user_email=user_email).first()
    if entry is None:
        entry = LatestBayesNet(user_email=user_email, bayesnet=user_bnet)
        E_DB.session.add(entry)
    else:
        entry.bayesnet = user_bnet

    E_DB.session.commit()


def get_global_bayesnet():
    bnet_dir = "Models"
    #global_f = glob.glob(f"{bnet_dir}{os.sep}global_bayesnet_*.json")[0]
    global_f = glob.glob(f"{bnet_dir}{os.sep}global_bayesnet.json")[0]
    global_bnet = getattr(g, '_global_bayesnet', None)
    if global_bnet is None:
        global_bnet = g._global_bayesnet = load_bayesnet(global_f)

    return global_bnet


def load_bayesnet(model_fname):
    if os.path.exists(model_fname):
        print(f"{model_fname}: path is valid")

    jsn = json.loads(open(model_fname).read())

    bnet = BayesianNetwork.from_json(jsn)

    return bnet


def save_latest_bayesnet(pom_net, user):
    """
    Given a pomegranate Bayesnet object and a username,
    replace existing bayesnet for that user with the new one.
    """
    bnet_dir = "Models"

    # Remove existing bayesnet for the current user
    for fname in glob.glob(f"{bnet_dir}{os.sep}{user}_bayesnet_*.json"):
        os.remove(fname)

    # Prep for saving the new one
    stamp = str(datetime.now().timestamp()).split(".")[0]
    out_json = os.path.join(bnet_dir, f"{user}_bayesnet_{stamp}.json")

    # Save
    with open(out_json, "w") as jfp:
        json.dump(pom_net.to_json(), jfp)
