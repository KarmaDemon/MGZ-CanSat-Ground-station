"""
This module provides several funtions for managing data and logging.
It is designed specifically for the MGZ CanSat mission.
"""

__author__ = "KarmaDemon"

try:
    import logging
    from logging.handlers import RotatingFileHandler
except ImportError:
    print("Error importing logging module. Logging is disabled.")

def logger_creator(name: str = __name__) -> logging.Logger:
    """
    Sets up and returns a logger with a rotating file handler.

    This function creates a logger with the specified name and configures it
    to log messages to a rotating file named 'CanSat.log'. The log file has
    a maximum size of 5 MB and keeps up to 2 backup files. The logger is set
    to DEBUG level, and the handler is set to INFO level. The log messages
    are formatted to include the timestamp, logger name, log level, and
    message.

    Args:
        name (str): The name of the logger. Defaults to the name of the module.

    Returns:
        logging.Logger: The configured logger instance.
    """

    logging.info("Logging system test.")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(f"{__file__[:len(__file__) - len('cansattools.py')]}/CanSat.log", mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    return logger

def free_logger(logger: logging.Logger) -> None:
    """
    Remove all handlers from a logger.
    """
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

logger = logger_creator("cansattools")

try:
    import classes
except ImportError:
    try:
        import program_files.classes as classes
    except ImportError:
        logger.error("Error importing classes module")

try:
    import sqlite3
    from sqlite3 import Error
    import os
    import requests
    from bs4 import BeautifulSoup
    import numpy as np
    import random
except ImportError as e:
    logger.error(f"Error importing module: {e}")

def test_data_generator(current_data: int | float, upper_bound: int = 100, lower_bound: int = -100, dispersion: int = 10, is_time_data: bool = False, max_attempts: int = 100, default_value: int | float = 0) -> int | float | None:
    """
    Generates test data within specified bounds with optional dispersion.

    This function attempts to generate a modified version of `current_data` 
    within the range defined by `upper_bound` and `lower_bound`. If `is_time_data` 
    is True, the function ensures that the generated data is strictly increasing. 
    The function makes multiple attempts to generate a valid data point, up to 
    `max_attempts`. If it fails, it returns `default_value`.

    Args:
        current_data (int | float): The current data point to base the generated data on.
        upper_bound (int, optional): The upper bound for the generated data. Defaults to 100.
        lower_bound (int, optional): The lower bound for the generated data. Defaults to -100.
        dispersion (int, optional): The maximum change applied to `current_data` in each attempt. Defaults to 10.
        is_time_data (bool, optional): If True, ensures the generated data is strictly increasing. Defaults to False.
        max_attempts (int, optional): The maximum number of attempts to generate valid data. Defaults to 100.
        default_value (int | float, optional): The value returned if valid data cannot be generated. Defaults to 0.

    Returns:
        int | float | None: The generated data if successful, otherwise `default_value`.
    """
    logger = logger_creator("test_data_generator")

    if current_data is None:
        logger.warning("Current data is None")
        return default_value

    data_type = type(current_data)

    for _ in range(max_attempts):
        if is_time_data:
            # Make sure the values are constantly increasing
            current_data += random.randint(1, dispersion)
        elif data_type == int:
            current_data += random.randint(-dispersion, dispersion)
        elif data_type == float:
            current_data += random.uniform(-dispersion, dispersion)
        else:
            logger.warning("Invalid data type: {}".format(data_type))
            return default_value

        if lower_bound <= current_data and current_data <= upper_bound:
            free_logger(logger)
            return current_data

    logger.warning("Failed to generate a value within bounds after {} attempts for the current data: {}".format(max_attempts, current_data))
    free_logger(logger)
    return default_value

def create_db(database_name: str = "raw_data.db", replace_mode: bool = False) -> None:
    """
    Creates a SQLite database with the specified name.

    If the database already exists, it will not be overwritten.

    :param database_name: The name of the SQLite database to use. Defaults to "raw_data.db".
    :return: None
    """
    
    logger = logger_creator("create_db")

    if replace_mode:
        try:
            os.remove(f'datas/{database_name}')
        except OSError:
            try:
                os.remove(f'{database_name}')
            except OSError:
                logger.error(f"Error removing {database_name}")
                pass

    # Setup the database
    try:
        conn = sqlite3.connect(database_name)
    except Error as e:
        try:
            os.chdir(f"{__file__[:len(__file__) - len('program_files/cansattools.py')]}/")
            conn = sqlite3.connect(f'datas/{database_name}')

        except Error as e:
            try:
                conn = sqlite3.connect(f'{database_name}')
            except Error as e:
                logger.error(f"Error connecting to the database: {e}")
                #freeing up file handler
                free_logger(logger)
                return
        
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS BMP280 (
                    Id INTEGER PRIMARY KEY, 
                    Time INTEGER, 
                    Temperature REAL, 
                    Pressure REAL,
                    Height REAL,
                    MissingData BOOLEAN,
                    IsOutlier BOOLEAN)""")
        
    cursor.execute("""CREATE TABLE IF NOT EXISTS DHT11 (
                    Id INTEGER PRIMARY KEY, 
                    Time INTEGER, 
                    Humidity REAL,
                    MissingData BOOLEAN,
                    IsOutlier BOOLEAN)""")
        
    cursor.execute("""CREATE TABLE IF NOT EXISTS GPS (
                   Id INTEGER PRIMARY KEY, 
                   Time INTEGER, 
                   Latitude REAL, 
                   Longitude REAL,
                   Altitude REAL,
                   MissingData BOOLEAN,
                   IsOutlier BOOLEAN)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS MPU6050 (
                   Id INTEGER PRIMARY KEY, 
                   Time INTEGER, 
                   Acceleration REAL,
                   MissingData BOOLEAN,
                   IsOutlier BOOLEAN)""")
    try:
        conn.commit()
    except Error as e:
        logger.error(f"Error committing table creation to the database: {e}")
        #freeing up file handler
        free_logger(logger)
        return
    conn.close()

def txt_to_db(data: list, database_name: str = "raw_data.db", test_mode: bool = False, replace_mode: bool = False) -> None:
    """
    This function reads data from a text file and inserts it into a SQLite database.
    
    :param database_name: The name of the SQLite database to use. Defaults to "raw_data.db".
    :param txt_name: The name of the text file to read from. Defaults to "raw_data.txt".
    :return: None
    """

    logger = logger_creator("txt_to_db")

    if test_mode:
        os.chdir(f"{__file__[:len(__file__) - len('program_files/cansattools.py')]}/")
    
    create_db(database_name, replace_mode)

    try:
        conn = sqlite3.connect(f'datas/{database_name}')
        cursor = conn.cursor()
    except Error as e:
        logger.error(f"Error connecting to the database: {e}")
        #freeing up file handler
        free_logger(logger)
        return

    # Insert the data into the database
    for line in data:
        try:
            if "BMP280" in line:
                cursor.execute("INSERT INTO BMP280 (Time, Temperature, Pressure, Height) VALUES (?, ?, ?, ?)", line.split()[1:])
            elif "DHT11" in line:
                cursor.execute("INSERT INTO DHT11 (Time, Humidity) VALUES (?, ?)", line.split()[1:])
            elif "GPS" in line:
                cursor.execute("INSERT INTO GPS (Time, First_coordinate, Second_coordinate, Height) VALUES (?, ?, ?, ?)", line.split()[1:])
            elif "MPU6050" in line:
                cursor.execute("INSERT INTO MPU6050 (Time, Acceleration) VALUES (?, ?)", line.split()[1:])
        except Error as e:
            logger.error(f"Error inserting data into the database: {e}")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def get_official_data(website_link: str = "https://koponyeg.hu/elorejelzes/Tat%C3%A1rszentgy%C3%B6rgy", test_mode: bool = False) -> dict:
    """
    Fetches and extracts weather data from the specified website link.

    This function makes an HTTP request to the provided weather forecast website,
    parses the HTML content, and extracts temperature, time, rain probability, 
    and wind speed data. The extracted data is stored in a dictionary with keys
    "temperatures", "times", "rain_probabilities", and "wind_speed".

    Args:
        website_link (str): The URL of the weather forecast website to fetch data from.
            Defaults to "https://koponyeg.hu/elorejelzes/Tat%C3%A1rszentgy%C3%B6rgy".

    Returns:
        dict: A dictionary containing lists of extracted weather data.

    Raises:
        Exception: If the website cannot be requested or parsed, or if the data cannot be extracted.
    """
    logger = logger_creator("accuracy_requester")

    official_datas = {"temperatures": [], "times": [], "rain_probabilities": [], "wind_speed": []}
    try:
        website = requests.get(website_link)
    except Exception as e:
        logger.error(f"{website_link} can't be requested with the error message of: {e}")
    try:
        soup = BeautifulSoup(website.text, 'html.parser')
    except Exception as e:
        logger.error(f"{website_link} can't be parsed with the error message of: {e}")
    try:
        #get_text() function is compatible with div and span
        official_datas["temperatures"] = [div.get_text() for div in soup.find_all("div", {"class": "temperature ng-star-inserted"})]
        official_datas["times"] = [div.get_text() for div in soup.find_all("div", {"class": "time"})]
        official_datas["rain_probabilities"] = [div.get_text() for div in soup.find_all("div", {"class": "rain ng-star-inserted"})] #interaction on the website is required
        official_datas["wind_speed"] = [span.get_text() for span in soup.find_all("span", {"class": "data"})]
    except Exception as e:
        logger.error(f"Datas can't be extracted from {website_link} with the error message of: {e}")

    if test_mode:
        print(official_datas)

    #freeing up file handler
    free_logger(logger)
    return official_datas

def refine_data(objects: list[classes.BMP280 | classes.MPU6050 | classes.GPS | classes.DHT11], attribute_name: str, outlier_iqr_multiplier=1.5, lacking_data_threshold=10) -> tuple[list[float], list[int]]:
    """
    Refine data by removing outliers and detecting lacking data.

    This function takes a list of objects with a specific attribute name, and
    returns a tuple of two lists. The first list contains the refined data, and
    the second list contains the indices of the lacking data.

    The function first detects lacking data by identifying larger differences
    between timestamps. Then, it removes outliers using the IQR method.

    Args:
        objects (list[classes.BMP280 | classes.MPU6050 | classes.GPS | classes.DHT11]):
            The list of objects to refine.
        attribute_name (str):
            The name of the attribute to refine.
        outlier_iqr_multiplier (float, optional):
            The multiplier for the IQR method. Defaults to 1.5.
        lacking_data_threshold (int, optional):
            The threshold for detecting lacking data. Defaults to 10.

    Returns:
        tuple[list[float], list[int]]:
            A tuple of two lists. The first list contains the refined data, and
            the second list contains the indices of the lacking data.
    """

    if len(objects) == 0:
        #freeing up file handler
        free_logger(logger)
        return [], []
    
    timestamps = [obj.time for obj in objects]
    data = [getattr(obj, attribute_name) for obj in objects]

    # Detect lacking data by larger differences between timestamps
    lacking_data_indices = []
    for i in range(1, len(timestamps)):
        if timestamps[i] - timestamps[i-1] > lacking_data_threshold * np.mean(np.diff(timestamps)):
            lacking_data_indices.append(i)

    # Remove outliers using the IQR method
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - outlier_iqr_multiplier * iqr
    upper_bound = q3 + outlier_iqr_multiplier * iqr
    refined_data = [x for x in data if lower_bound < x < upper_bound]
    
    #freeing up file handler
    free_logger(logger)
    return refined_data, lacking_data_indices

if __name__ == "__main__":
    #txt_to_db(test_mode=True, replace_mode=True)
    #get_official_data(website_link="https://koponyeg.hu/elorejelzes/Budapest", test_mode=True)
    pass