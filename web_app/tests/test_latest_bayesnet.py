import os
import sys
sys.path.append(os.getcwd())

import json

from erebuild.bayesnet_helpers import get_latest_user_bayesnet, save_latest_user_bayesnet


def test_latest_bayesnet():
    bnet_a = get_latest_user_bayesnet(email_a)
    bnet_b = get_latest_user_bayesnet(email_b)

    mrgnl_a = bnet_a.marginal()
    mrgnl_b = bnet_b.marginal()
    
    are_same = True
    for st_a, st_b in zip(mrgnl_a, mrgnl_b):
        prob_a = json.loads(st_a.to_json())["parameters"][0]
        prob_b = json.loads(st_b.to_json())["parameters"][0]

        for k in prob_a:
            if abs(prob_a[k] - prob_b[k]) <= 0.0000001:
                continue
            else:
                are_same = False

    assert not are_same, f"Latest Bayesnet for {email_a} and {email_b} are the same!"


if __name__ == "__main__":
    email_a = input("Enter email of a user ..\n") 
    email_b = input("Enter email of another user ..\n") 

    compare_bayesnet(email_a, email_b)

