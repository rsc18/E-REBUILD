import numpy as np
import matplotlib.pyplot as plt


def save_histogram(data, var_name):
    fig_fname = "figures/histogram_" + var_name + ".pdf"
    fig, ax = plt.subplots()
    ax.hist(data, 100)
    ax.set_title(var_name)
    fig.savefig(fig_fname)

def remove_furthest_from_median(data):
    # No. of outliers
    # Should be set to 20 for Distance
    num_out = 5
    for i in range(num_out):
        med = np.median(data)
        idx, d = max([(i, (v - med)**2) for i, v in enumerate(data)], key=lambda x: x[1])
        data = np.delete(data, idx)

    return data


def visualize_observable_histogram(in_csv):
    """
    Given a csv file containing real numbers, save histogram for each column.

    These histograms will later be used for assigning data to categories.
    """
    # Read the variable names
    with open(in_csv) as fp:
        var_names = fp.readline().strip("\n").split(",")

    # Load all cases
    cases = np.genfromtxt(in_csv, delimiter=",", skip_header=1)

    for col, var_name in enumerate(var_names):
        vals = cases[:, col:col+1]
        filtered = vals[~np.isnan(vals)].ravel().tolist()

        if filtered:
            # Remove outliers
            filtered = remove_furthest_from_median(filtered)

            # Save
            save_histogram(filtered, var_name)

if __name__ == "__main__":
    in_csv = "data/cases_FallSpring16-17.csv"
    visualize_observable_histogram(in_csv)
