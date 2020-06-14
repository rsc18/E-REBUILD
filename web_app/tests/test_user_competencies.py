import os
import sys
sys.path.append(os.getcwd())

import pprint
from erebuild.database_helpers import get_latest_user_competency


def test_user_competency():
    emails = ["", "bk11h@my.fsu.edu", "kyle.reeves@fsus.fsu.edu"]

    comp_0 = get_latest_user_competency(emails[0])
    assert comp_0 == {}

    comp_1 = get_latest_user_competency(emails[1])
    comp_2 = get_latest_user_competency(emails[2])

    print("*" * 20)
    print(f"Competency for user: {emails[1]}")
    print("*" * 20)
    pprint.pprint(comp_1)

    print("*" * 20)
    print(f"Competency for user: {emails[2]}")
    print("*" * 20)
    pprint.pprint(comp_2)

    cc_keys = [k for k in comp_1.keys() if k[:2] == "cc"]

    print("competency nodes:")
    print(cc_keys)

    for k in comp_1:
        if k not in comp_2:
            print(f"Key {k} is not in both.")
            continue
        for k_cat in comp_1[k]:
            if abs(comp_1[k][k_cat] - comp_2[k][k_cat]) <= 0.000001:
                pass
            else:
                print(f"{k}: {k_cat} differ. {comp_1[k][k_cat]:.4} vs. {comp_2[k][k_cat]:.4}")



if __name__ == "__main__":
    test_user_competency()

