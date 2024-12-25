# MGZ Ground station program

## Version
The program is currently under developement. There might be missing parts, unfinished scetches, bugs and inconsistencies.

## Introduction
This program is part of the MGZ CanSat mission, which is designed for the CanSat verseny 2024 competition. For more information about the competition, visit the official website: https://www.cansatverseny.hu/
The program was created by the MákosGubaZabálók team.

The program makes basic analyzis and refinement on the measured datas of our CanSat when our data sources are updated and our IPython Notebook is restarted. Due to the fact that our mission is a one time flight, this technique is a bit overcomplicated and unnescessarily robust. However, this method of data analyzis makes reusability a possibility and testing less time consuming. Our scripts are designed to be easily readable and usable on other windows computers as well. This makes collaboration accessible and less problematic. These are crucial aspects on an offical mission, which we aim to replicate to the best of our ability.

## Execution
In order to execute the analyzis, open the Visualization.ipynb and run it's scripts. The IPython Notebook requires the installation of Python 3.12.7 and an up to date environment for working with Jupiter Notebooks. For furter information, visit the official website: https://code.visualstudio.com/docs/datascience/jupyter-notebooks

## Required python libraries and modules:
- sqlite3 (required for communicating with databases)
- BeautifulSoup (required for scraping weather forecast datas from the web)
- numpy (essencial)
- matplotlib (essencial)
- requests (required for scraping weather forecast datas from the web)
- pandas (essencial)
- nbconvert (required for generating the PDF files. For more information, visit: https://medium.com/@6unpnp/install-pandoc-for-jupyter-notebook-885becbf6a14)

Note: The program was created and tested inside Visual Studio Code. If you have a different environment for working with Jupyter Notebooks, you might encounter errors.

## Alternative use cases
Due to the complexity of the environmental necessities, the setup process can be tricky and difficult. If setting up the environment is not a possibility, a converted version of the code is generated named Visualization.pdf. The PDF file contains the analyzis and the code for read-only purposes.

The graphs inside Visualization.ipynb are static images. If you would like to open the graphs in an interactive environment, you will need to run graphs/pkls/plot_graph.py. You can find more information in the graphs/pkls/README.md file.

The generated SQLite database is accesible inside the datas folder. It can be used for further analyzes.