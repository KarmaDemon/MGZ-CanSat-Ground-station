"""
This module provides classes for CanSat data analyzis.
"""
try:
    from cansattools import logger_creator, free_logger
except ImportError:
    from program_files.cansattools import logger_creator, free_logger
logger = logger_creator("classes")
try:
    import sqlite3
    from sqlite3 import Error
    import numpy as np
except ImportError as e:
    logger.error(f"Error importing module: {e}")

class Data:
    def __init__(self, missing_data: bool = False, is_outlier: bool = False) -> None:
        self.missing_data = missing_data # Flag to indicate if object is missing before this object
        self.is_outlier = is_outlier

    @staticmethod
    def read_from_db_all(db_name: str, table_name: str, index: int = None) -> list[tuple]:
        if index is None and c is None:
            try:
                conn = sqlite3.connect(db_name)
            except Error as e:
                logger.error(f"Error connecting to the database: {e}")
                free_logger(logger)
                return
            c = conn.cursor()
            if index is not None:
                c.execute(f"SELECT * FROM {table_name} WHERE Id = ?", (index,))
                row: list = c.fetchall()
                conn.close()
                return row
            elif index is None:
                c.execute(f"SELECT * FROM {table_name}")
                rows: list[tuple] = c.fetchall()
                conn.close()
                return rows
    
    def read_from_db(self, table_name: str, index: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
        try:
            c.execute(f"SELECT * FROM {table_name} WHERE Id = ?", (index,))
            conn.commit()
            row = c.fetchone()
            if row is None:
                logger.error(f"No row found for index {index} in table {table_name}")
                return
            column_index = 1  # Start from the second column (index 1)
            for attribute_name in vars(self).keys():
                if attribute_name != 'missing_data' and attribute_name != 'is_outlier':
                    attribute_value = row[column_index]  # Use the current column index
                    self.__dict__[attribute_name] = attribute_value
                    column_index += 1  # Increment the column index for the next attribute
                if attribute_name == 'missing_data' or attribute_name == 'is_outlier':
                    attribute_value = row[column_index]  # Use the current column index
                    attribute_value = True if attribute_value == 1 else False
                    self.__dict__[attribute_name] = attribute_value
                    column_index += 1  # Increment the column index for the next attribute
        except Error as e:
            logger.error(f"Error fetching data: {e}")

    def refine(self, previous_object, outlier_iqr_multiplier: float = 1.5, outlier_step_threshold: int = 10, lacking_data_threshold: int = 10) -> None:
        """
        Refines data by removing outliers and detecting lacking data.

        This function takes a Data object and the previous Data object as arguments.
        It checks for lacking data by identifying larger differences between timestamps.
        Then, it removes outliers using the IQR method.

        :param previous_object: The previous Data object.
        :param outlier_iqr_multiplier: The multiplier for the IQR method. Defaults to 1.5.
        :param lacking_data_threshold: The threshold for detecting lacking data. Defaults to 10.
        :return: None
        """
        if previous_object is None:
            logger.error("Previous object is None")
            free_logger(logger)
            return
        try:
            for attribute_name, attribute_value in vars(self).items():
                if attribute_name != "time":
                    timestamp = abs(self.time ^ previous_object.time)
                    data = attribute_value
                    previous_data = previous_object.__dict__[attribute_name]

                    # Detect lacking data by larger differences between timestamps
                    if timestamp > lacking_data_threshold:
                        self.missing_data = True

                    # Remove outliers statically
                    if not self.missing_data:
                        if data is not None and data < previous_data-outlier_step_threshold or data > previous_data+outlier_step_threshold:
                            self.is_outlier = True

                    # Remove outliers using the IQR method
                    if attribute_name in previous_object.__dict__:
                        lower_bound = min(data, previous_data)
                        upper_bound = max(data, previous_data)
                        iqr = upper_bound - lower_bound
                        if data is not None and data < lower_bound - outlier_iqr_multiplier * iqr or data > upper_bound + outlier_iqr_multiplier * iqr:
                            self.is_outlier = True
        except Exception as e:
            logger.error(f"Error during refinement: {e}")
            free_logger(logger)
            return

class BMP280(Data):
    def __init__(self, time: int, temperature: int, pressure: float, height: float):
        self.time = time
        self.temperature = temperature
        self.pressure = pressure
        self.height = height
        super().__init__()

    def insert_into_db(self, table_name: str = "BMP280", c: sqlite3.Cursor = None) -> None:
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "BMP280".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Temperature, Pressure, Height, MissingData, IsOutlier) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.time, self.temperature, self.pressure, self.height, 1 if self.missing_data else 0, 1 if self.is_outlier else 0)) # (self.missing_data, self.is_outlier))

class DHT11(Data):
    def __init__(self, time: int, humidity: float):
        self.time = time
        self.humidity = humidity
        super().__init__()

    def insert_into_db(self, table_name: str = "DHT11", c: sqlite3.Cursor = None):
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "DHT11".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Humidity, MissingData, IsOutlier) VALUES (?, ?, ?, ?)",
                    (self.time, self.humidity, 1 if self.missing_data else 0, 1 if self.is_outlier else 0)) # (self.missing_data, self.is_outlier))

class GPS(Data):
    def __init__(self, time: int, latitude: float, longitude: float, altitude: float) -> None:
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        super().__init__()

    def insert_into_db(self, table_name: str = "GPS", c: sqlite3.Cursor = None):
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "GPS".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Latitude, Longitude, Altitude, MissingData, IsOutlier) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.time, self.latitude, self.longitude, self.altitude, 1 if self.missing_data else 0, 1 if self.is_outlier else 0)) # (self.missing_data, self.is_outlier))

class MPU6050(Data):
    def __init__(self, time: int, accelerometer_x: float, accelerometer_y: float, accelerometer_z: float, gyroscope_x: float, gyroscope_y: float, gyroscope_z: float) -> None:
        self.time = time
        self.accelerometer_x = accelerometer_x
        self.accelerometer_y = accelerometer_y
        self.accelerometer_z = accelerometer_z
        self.gyroscope_x = gyroscope_x
        self.gyroscope_y = gyroscope_y
        self.gyroscope_z = gyroscope_z
        super().__init__()

    def insert_into_db(self, table_name: str = "MPU6050", c: sqlite3.Cursor = None):
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "MPU6050".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Accelerometer_X, Accelerometer_Y, Accelerometer_Z, Gyroscope_X, Gyroscope_Y, Gyroscope_Z, MissingData, IsOutlier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.time, self.accelerometer_x, self.accelerometer_y, self.accelerometer_z, self.gyroscope_x, self.gyroscope_y, self.gyroscope_z, 1 if self.missing_data else 0, 1 if self.is_outlier else 0)) # (self.missing_data, self.is_outlier))