
Bayesnet model preparation
==========================

1. Handle XML game logs and convert to CSV file.

    Program: game_xml_logs_to_csv.py
    Depends on: associated imports

2. Categorization rules.

    Program: categorization_rules.py

3. Translate to category.

    Program: translate_to_category.py


4. Split dataset into train and test


5. Populate unseen competency variables in the training split

    Program: implant_competency_var_distribution.py


6. Prepare Bayesian Network for training

    (a) bayesnet_trajectory_from_ucla_cc_map.py
         Output Netica .dne file based on UCLA common core map and our constraints

    The .dne Netica file thus created is only for graph structure purposes.
    It is independent of any training data.

7. Use .dne created in 6 and train/test data created in 4 to train a new bayesnet model with Netica.

8. Train a Bayesian network model with output from 6 and 7.

9. Save the conditional probability tables (per node) into a txt file with Netica.
   The information about how to do that is documented in the first few lines of
   `bayesnet_from_netica_cpts.py`.

10. Load CPTs from 9 into a pomegranate Bayesian Network with the help of `bayesnet_from_netica_cpts.py`.

11. After this, follow code inside web_app since that's where the actual real-time assessment server resides.


Serving Real Time Assessment
============================

12. Copy model created in 10 into web_app/Models. Name it as global_bayesnet.json.
    It's a pomegranate bayesianNetwork saved as a json file.

13. The server loads global_bayesnet.json for assessment.

14. Check web_app/erebuild/stealth_assessment.py. When a player finishes a game level of Erebuild (the actual game),
    the C# Unity3D code makes a post request at the endpoint '/assessment/game'.


Extras
======

1. copy mysql database from windows to linux
    https://gist.github.com/bparaj/955a7a3e10c2711b22458658d215d4c4

2. Snapshot of the database exists in Google Drive. Directory is database\_backup.
