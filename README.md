# MGZ CanSat mission program files

## Status
The repository is currently under developement. There might be missing parts, unfinished scetches, bugs and inconsistencies.

## Introduction
This repository is part of the MGZ CanSat mission, which is designed for the CanSat verseny 2024 competition. For more information about the competition, visit the official website: https://www.cansatverseny.hu/
The repository was created by the MákosGubaZabálók team.

The only official source for the program is the following GitHub repository: https://github.com/KarmaDemon/MGZ-CanSat-Ground-station Do NOT download the program from any other source for your own safety!

## Arduino files
The repository contains both the Arduino scripts of the cansat and the ground station. These were developed using Visual Studio Code and Arduino IDE. The scripts can be uploaded to the device using the Arduino IDE.

### Arduino_onboard.ino
It is a simple script for recieving telemetry data using the WLR089-CANSAT module. It prints the recieved data on the Serial Monitor and therefore, can be saved and plotted on the computer.

#### Required libraries and dependencies
The script doesn't require any library or dependency which is not installed with the Arduino IDE.

#### Execution
The script can be used on any Arduino boards which support software serial communication.

### Arduino_ground_station.ino
This script is responsible for powering modules and communicating with them. It collects data from the following devices: DHT11, BMP280 and GY-GPS6MV2. The microcontroller saves the collected measurements on a MicroSD card and transmits telemetry via the WLR089-CANSAT module. 

#### Required libraries and dependencies
- SD (https://docs.arduino.cc/libraries/sd/)
- DHT11 (https://github.com/dhrubasaha08/DHT11)
- TinyGPSPlus (https://github.com/mikalhart/TinyGPSPlus)
- I2C (https://github.com/Wh1teRabbitHU/Arduino-I2C)
- I2C-Sensor-Lib (iLib) (https://github.com/orgua/iLib)

#### Execution
The script can be used without changing it using an Arduino Nano or Uno. With other devices, changing the wiring is nescessary.

## CanSat_real_time.py
This file collects the data provided by the Arduino of ground station. It is responsible for plotting the collected data using matplotlib and saves it inside a text file. The text file, which gets created, can be analized by the automatic data analyzer.

### Required libraries and dependencies
- matplotlib

### Execution
You can run the script from an IDE or from the terminal if the Python Interpreter is installed. The script was developed with Python 3.12.7. It is not recommended to use it with an older version of python because unexpected behaviour might occure.

## Visualization.ipynb
The IPython Notebook makes basic analyzis and refinement on the measured datas of our CanSat when our data sources are updated and our notebook is restarted. Due to the fact that our mission is a one time flight, this technique is a bit overcomplicated and unnescessarily robust. However, this method of data analyzis makes reusability a possibility and testing less time consuming. Our scripts are designed to be easily readable and usable on other windows computers as well. This makes collaboration accessible and less problematic. These are crucial aspects on an offical mission, which we aim to replicate to the best of our ability.

### Required libraries and dependencies
- sqlite3 (required for communicating with databases)
- BeautifulSoup (required for scraping weather forecast datas from the web)
- numpy (essencial)
- matplotlib (essencial)
- requests (required for scraping weather forecast datas from the web)
- pandas (essencial)
- nbconvert (required for generating the PDF files. For more information, visit: https://medium.com/@6unpnp/install-pandoc-for-jupyter-notebook-885becbf6a14)

Note: The program was created and tested inside Visual Studio Code. If you have a different environment for working with Jupyter Notebooks, you might encounter errors.

### Execution
In order to execute the analyzis, open the Visualization.ipynb and run it's scripts. The IPython Notebook requires the installation of Python 3.12.7 and an up to date environment for working with Jupiter Notebooks. For furter information, visit the official website: https://code.visualstudio.com/docs/datascience/jupyter-notebooks

### Alternative use cases
Due to the complexity of the environmental necessities, the setup process can be tricky and difficult. If setting up the environment is not a possibility, a converted version of the code is generated named Visualization.pdf. The PDF file contains the analyzis and the code for read-only purposes.

The graphs inside Visualization.ipynb are static images. If you would like to open the graphs in an interactive environment, you will need to run graphs/pkls/plot_graph.py. You can find more information in the graphs/pkls/README.md file.

The generated SQLite database is accesible inside the datas folder. It can be used for further analyzes.