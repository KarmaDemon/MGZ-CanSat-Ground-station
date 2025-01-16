"""
This module provides classes for CanSat data analyzis.
"""

__author__ = "KarmaDemon"

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
    def __init__(self, missing_data: bool = False) -> None:
        self.missing_data = missing_data # Flag to indicate if object is missing before this object

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

    def refine(self, previous_object, next_object, outlier_threshold: int = 10, lacking_data_threshold: int = None, attribute_name: str = None) -> None:
        
        if previous_object is None:
            logger.error("Previous object is not an instance of Data", exc_info=True)
            free_logger(logger)
            return
        if next_object is None:
            logger.error("Next object is not an instance of Data", exc_info=True)
            free_logger(logger)
            return
        try:
            if lacking_data_threshold is not None:
                timestamp = abs(self.time - previous_object.time)
                if timestamp > lacking_data_threshold:
                            self.missing_data = True
            if attribute_name is None:
                # Detect outliers by comparing the current data with the previous and next data
                for attribute_name, attribute_value in vars(self).items():
                    if attribute_name != "time":
                        previous_data = previous_object.__dict__[attribute_name]
                        next_data = next_object.__dict__[attribute_name] if next_object is not None else None
                        outlier_attribute_name = f"is_{attribute_name}_outlier"
                        if previous_data is not None and next_data is not None:
                            if attribute_value > previous_data and attribute_value > next_data:
                                if attribute_value > next_data + outlier_threshold or attribute_value > previous_data + outlier_threshold:
                                    setattr(self, outlier_attribute_name, True)
                            if attribute_value < previous_data and attribute_value < next_data:
                                if attribute_value < next_data - outlier_threshold or attribute_value < previous_data - outlier_threshold:
                                    setattr(self, outlier_attribute_name, True)
            else:
                attribute_value = self.__dict__[attribute_name]
                previous_data = previous_object.__dict__[attribute_name]
                next_data = next_object.__dict__[attribute_name] if next_object is not None else None
                outlier_attribute_name = f"is_{attribute_name}_outlier"
                if previous_data is not None and next_data is not None:
                    if attribute_value > previous_data and attribute_value > next_data:
                        if attribute_value > next_data + outlier_threshold or attribute_value > previous_data + outlier_threshold:
                            setattr(self, outlier_attribute_name, True)
                    if attribute_value < previous_data and attribute_value < next_data:
                        if attribute_value < next_data - outlier_threshold or attribute_value < previous_data - outlier_threshold:
                            setattr(self, outlier_attribute_name, True)
        except Exception as e:
            logger.error(f"Error during refinement: {e}", exc_info=True)
            free_logger(logger)

class BMP280(Data):
    def __init__(self, time: int, temperature: float, pressure: float, height: float, speed: float, acceleration: float, temperature_outlier: bool = False, pressure_outlier: bool = False, height_outlier: bool = False, speed_outlier: bool = False, acceleration_outlier: bool = False) -> None:
        self.time = time
        self.temperature = temperature
        self.pressure = pressure
        self.height = height
        self.speed = speed
        self.acceleration = acceleration
        self.is_temperature_outlier = temperature_outlier
        self.is_pressure_outlier = pressure_outlier
        self.is_height_outlier = height_outlier
        self.is_speed_outlier = speed_outlier
        self.is_acceleration_outlier = acceleration_outlier
        super().__init__()

    def calculate_speed(self, previous_object) -> None:
        """
        Calculate the speed of the object based on the height difference and time difference with the previous object.

        Args:
            previous_object (Data): The previous object with which the speed will be calculated.

        Raises:
            TypeError: If the previous object is not an instance of Data.
        """

        if previous_object is not None and self.time != previous_object.time:
            self.speed = abs(self.height - previous_object.height) / (self.time - previous_object.time)
        else:
            self.speed = 0
    
    def calculate_acceleration(self, previous_object) -> None:
        """
        Calculate the acceleration of the object based on the speed difference and time difference with the previous object.

        Args:
            previous_object (Data): The previous object with which the acceleration will be calculated.

        Raises:
            TypeError: If the previous object is not an instance of Data.
        """
        if previous_object is not None and self.time != previous_object.time:
            self.acceleration = abs(self.speed - previous_object.speed) / (self.time - previous_object.time)
        else:
            self.acceleration = 0

    def insert_into_db(self, table_name: str = "BMP280", c: sqlite3.Cursor = None) -> None:
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "BMP280".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Temperature, Pressure, Height, Speed, Acceleration, MissingData, IsTemperatureOutlier, IsPressureOutlier, IsHeightOutlier, IsSpeedOutlier, IsAccelerationOutlier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.time, self.temperature, self.pressure, self.height, self.speed, self.acceleration, 1 if self.missing_data else 0, 1 if self.is_temperature_outlier else 0, 1 if self.is_pressure_outlier else 0, 1 if self.is_height_outlier else 0, 1 if self.is_speed_outlier else 0, 1 if self.is_acceleration_outlier else 0))

class DHT11(Data):
    def __init__(self, time: int, humidity: float, temperature: float, humidity_outlier: bool = False, temperature_outlier: bool = False) -> None:
        self.time = time
        self.humidity = humidity
        self.temperature = temperature
        self.is_humidity_outlier = humidity_outlier
        self.is_temperature_outlier = temperature_outlier
        super().__init__()

    def insert_into_db(self, table_name: str = "DHT11", c: sqlite3.Cursor = None):
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "DHT11".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Humidity, Temperature, MissingData, IsHumidityOutlier, IsTemperatureOutlier) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.time, self.humidity, self.temperature, 1 if self.missing_data else 0, 1 if self.is_humidity_outlier else 0, 1 if self.is_temperature_outlier else 0))

class GPS(Data):
    def __init__(self, time: int, latitude: float, longitude: float, altitude: float, latitude_outlier: bool = False, longitude_outlier: bool = False, altitude_outlier: bool = False) -> None:
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.is_latitude_outlier = latitude_outlier
        self.is_longitude_outlier = longitude_outlier
        self.is_altitude_outlier = altitude_outlier
        super().__init__()

    def insert_into_db(self, table_name: str = "GPS", c: sqlite3.Cursor = None):
        """
        Inserts the data into the specified SQLite database.

        :param db_name: The name of the SQLite database to use.
        :param table_name: The name of the table to use. Defaults to "GPS".
        :return: None
        """
        c.execute(f"INSERT INTO {table_name} (Time, Latitude, Longitude, Altitude, MissingData, IsLatitudeOutlier, IsLongitudeOutlier, IsAltitudeOutlier) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.time, self.latitude, self.longitude, self.altitude, 1 if self.missing_data else 0, 1 if self.is_latitude_outlier else 0, 1 if self.is_longitude_outlier else 0, 1 if self.is_altitude_outlier else 0))
