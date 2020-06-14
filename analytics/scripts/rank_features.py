from sklearn.svm import SVR
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.feature_selection import VarianceThreshold
import numpy as np
from sklearn.preprocessing import normalize

def attr_name_sequence():
    s = """21ContainerCollect,Name,Level,Time,NumWrong,MaterialCredits
22FamilyCollect,Name,Level,Time,NumWrong,MaterialCredits
23PlacementTest,Name,Level,Time,NumWrong,NumBlocks,NumTrades,PercentLost,Distance,Size,Angle,BuildingComplete,MaterialCredits
DesertPlacement01,Name,Level,Time,LevelComplete
SchoolPlacement01,Name,Level,Time,NumBlocks,NumTrades,TotalLost,MaterialCredits,LevelComplete
IslandBuild01,Name,Level,Time,NumBlocks,NumTrades,TotalLost,MaterialCredits,Distance,Size,Angle,BuildingComplete,LevelComplete
IslandBuildTraining01,Name,Level,Time,NumBlocks,NumTrades,TotalLost,MaterialCredits,Distance,Size,Angle,BuildingComplete,LevelComplete
IslandCollect02,Name,Level,Time,NumWrong,LevelComplete
IslandCollect01,Name,Level,Time,NumWrong,LevelComplete
"""
    attr_seq = []
    for i, l in enumerate(s.split("\n")[:-1]):
        lvl, t1, t2, *attrs = l.split(",")
        for attr in attrs:
            attr_seq.append("_".join([str(i), lvl, attr]))

    return attr_seq


def top_9_regress():
    fname = "data/consolidated_data_top_9_levels.txt"
    needed_cols = tuple(range(1, 55))
    full_data = np.loadtxt(fname, usecols=needed_cols, delimiter=",")
    stu_names = np.loadtxt(fname, usecols=(0), dtype=str, delimiter=",")
    #print(len(full_data[0]))
    # last 4 cols in full_data:
    #   50: premath,51: prespatial, 52: postmath, 53:postspatial
    X = full_data[:, :50]

    # normalize each featyre
    norm_X = normalize(X, axis=0)
    norm_X = X

    # Select pre-spatial
    y = full_data[:, 50:51]

    #print(y)
    #i = 8
    #print(stu_names[i], X[i], y[i])

    #print(data[0])
    estimator = SVR(kernel="linear")
    selector = RFECV(estimator, step=1, cv=5, verbose=1)

    selector = selector.fit(norm_X, y.ravel())

    f_ranks = selector.ranking_.ravel().tolist()

    attr_seq = attr_name_sequence()

    for i, r in enumerate(f_ranks):
        if r < 10:
            print(attr_seq[i], r)


def top_4_regress():
    """
    Rank features of top 4 levels played by most number of students.
    """
    fname = "data/consolidated_data_top_4_levels.txt"
    needed_cols = tuple(range(1, 23))
    full_data = np.loadtxt(fname, usecols=needed_cols, delimiter=",")
    stu_names = np.loadtxt(fname, usecols=(0), dtype=str, delimiter=",")

    X = full_data[:, :18]

    # Pre-math
    y = full_data[:, 18:19]
    y = full_data[:, 20:21]

    for i in range(len(y)):
        if y[i] == -1:
            y[i] = full_data[i, 18]

    print(y)

    estimator = SVR(kernel="linear")
    selector = RFECV(estimator, step=1, cv=5, verbose=0)

    selector = selector.fit(X, y.ravel())
    f_ranks = selector.ranking_.ravel().tolist()

    attr_seq = attr_name_sequence()

    for i, r in enumerate(f_ranks):
        if r < 10:
            print(attr_seq[i], r)


def top_4_classification():
    """
    Rank features of top 4 levels played by most number of students
    with different classifiers.
    """
    fname = "data/consolidated_data_top_4_levels.txt"
    needed_cols = tuple(range(1, 23))
    full_data = np.loadtxt(fname, usecols=needed_cols, delimiter=",")
    stu_names = np.loadtxt(fname, usecols=(0), dtype=str, delimiter=",")

    X = full_data[:, :18]

    # Pre-math
    #yy = full_data[:, 18:19].ravel().tolist()
    yy = full_data[:, 19:20].ravel().tolist()

    # Categorize pre-math scores
    y = categorize_scores(yy)

    # Prepare a list of estimators
    estimators = [RandomForestClassifier(n_estimators=10), SVC(kernel="linear")]

    for est in estimators[:]:
        selector = RFECV(est, step=1, cv=5, verbose=0)
        selector = selector.fit(X, y.ravel())
        f_ranks = selector.ranking_.ravel().tolist()

        print(f_ranks)

def top_4_remove_low_variance():
    """
    Remove features with low variance.
    """
    fname = "data/consolidated_data_top_4_levels.txt"
    needed_cols = tuple(range(1, 23))
    full_data = np.loadtxt(fname, usecols=needed_cols, delimiter=",")
    stu_names = np.loadtxt(fname, usecols=(0), dtype=str, delimiter=",")

    X = full_data[:, :18]
    print(X.shape)

    # Pre-math
    #yy = full_data[:, 18:19].ravel().tolist()
    yy = full_data[:, 19:20].ravel().tolist()

    # Categorize pre-math scores
    y = categorize_scores(yy)

    selector = VarianceThreshold()

    #X_new = selector.fit_transform(X, y.ravel())
    X_new = selector.fit_transform(X)
    f_support = selector.get_support()

    attr_seq = attr_name_sequence()
    for i, v in enumerate(f_support):
        print(v, attr_seq[i])


def categorize_scores(scores):
    y = np.empty((len(scores)))
    for i, v in enumerate(scores):
        if v > 66.6:
            category = 2
        elif v > 33.3:
            category = 1
        else:
            category = 0

        y[i] = category

    return y


if __name__ == "__main__":
    top_4_regress()
    #top_4_classification()
    #top_4_remove_low_variance()
