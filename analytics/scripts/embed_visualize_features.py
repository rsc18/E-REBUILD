import numpy as np
from sklearn.manifold import TSNE, MDS
import matplotlib.pyplot as plt

def top_4_visualize():
    """
    Embed in a lower dimensional (2D) and visualize samples for top 4 levels.

    t-SNE paper:
        https://lvdmaaten.github.io/publications/papers/JMLR_2008.pdf
    """
    fname = "data/consolidated_data_top_4_levels.txt"
    needed_cols = tuple(range(1, 23))
    full_data = np.loadtxt(fname, usecols=needed_cols, delimiter=",")
    stu_names = np.loadtxt(fname, usecols=(0), dtype=str, delimiter=",")

    X = full_data[:, :18]

    # Pre-math
    yy = full_data[:, 19:20].ravel().tolist()
    #yy = full_data[:, 18:19].ravel().tolist()

    # Categorize pre-math scores
    y = categorize_scores(yy)

    fig = plt.figure(figsize=(15, 8))
    colors = ["r", "g", "b"]

    # Perform 2D embedding using tsne
    dim = 2
    tsne = TSNE(n_components=dim, init='pca', random_state=0)
    XX = tsne.fit_transform(X)

    # Plot
    ax = fig.add_subplot(1, 2, 1)
    for i, point in enumerate(XX):
        category = int(y[i])
        plt.scatter(point[0], point[1], c=colors[category])
    plt.title("tsne")
    plt.axis('tight')

    # Perform 2D embedding using MDS
    mds = MDS(n_components=dim, max_iter=100, n_init=1)
    XX = mds.fit_transform(X)

    # Plot
    ax = fig.add_subplot(1, 2, 2)
    for i, point in enumerate(XX):
        category = int(y[i])
        plt.scatter(point[0], point[1], c=colors[category])
    plt.title("mds")
    plt.axis('tight')


    plt.show()


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
    top_4_visualize()
