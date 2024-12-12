"""
This file is used to plot the data from a pickle file. Modify the file_name variable to change the file to plot.
You can also pass a file name as an argument to the script.
Example:
    python plot_graph.py plot.pkl
"""

file_name = "BMP_raw.pkl"

import os
os.chdir(f"{__file__[:len(__file__) - len('/graphs/pkls/plot_graph.py')]}/")
try:
    import program_files.cansattools as cansattools
    logger = cansattools.logger_creator("plot_graph")
except ImportError:
    print("Error setting up logger. Cansattools can't be imported.Logging is disabled.")
try:
    import matplotlib.pyplot as plt
    import pickle
    import sys
except ImportError as e:
    logger.error(f"Error importing module: {e}")

def plot_graph(file: str = "plot.pkl") -> None:
    os.chdir(f"{__file__[:len(__file__) - len('plot_graph.py')]}/")
    fig: plt.Figure
    try:
        with open(file, 'rb') as f:
            fig = pickle.load(f)
        plt.show()
    except FileNotFoundError:
        logger.error(f"File {file} not found.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "":
        plot_graph(sys.argv[1])
    else:
        plot_graph(file_name)