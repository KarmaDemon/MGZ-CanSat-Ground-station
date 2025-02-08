"""
This file is used to plot the data from a serial port and save it to a text file. Do not open Arduino IDE while executing this file.
"""

__author__ = 'KarmaDemon'

TEST_MODE = False

try:
    from program_files.cansattools import logger_creator as logger_creator
    from program_files.cansattools import test_data_generator as test_data_generator
    logger = logger_creator("CanSat_real_time")
except ImportError:
    print("Error setting up logger. Cansattools can't be imported. Logging is disabled.")
    logger = None

try:
    import serial
    import random
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import mplleaflet
except ImportError as e:
    logger.error("Error importing module: {e}")

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
FILE_NAME = "datas/raw_data.txt"

fig = plt.figure()
fig_manager = plt.get_current_fig_manager()
fig_manager.set_window_title('Real time data visualization')
if not TEST_MODE:
    try:
        ser = serial.Serial(SERIAL_PORT,BAUD_RATE)
    except serial.SerialException as e:
        logger.error(f"Error opening serial port: {e}", exc_info=True)
try:
    file = open("datas/raw_realtime_data.txt",'w')
except IOError as e:
    logger.error(f"Error opening file: {e}", exc_info=True)
    file = None

time: list[int] = []
temperature: list[float] = []
altitude: list[float] = []
time2: list[int] = []
longitude: list[float] = []
latitude: list[float] = []

def animate(frame) -> None:
    """
    This function is called periodically from FuncAnimation
    :param frame: int
    :return: None
    """
    if not TEST_MODE:
        try:
            message: bytes = ser.readline()
        except serial.SerialException as e:
            logger.error(f"Error reading serial port: {e}")
            return
        # message has the following format: time temperature altitude\n
        line_str = message.decode()  
        line = line_str.split()  # decode bytes to string and split by whitespace
        print(line)
        if len(line) == 5:  # check if the message has the correct format
            sensor_name, alt, pressure, temp, i = line
            if not sensor_name == 'ERROR':
                time.append(int(i))
                temperature.append(float(temp))
                altitude.append(float(alt))
        elif len(line) == 7:
            sensor_name, long, lat, altitude2, speed, sat_number, i = line
            if not sensor_name == 'ERROR':
                time2.append(int(i))
                longitude.append(float(long))
                latitude.append(float(lat))
        file.write(line_str)
        file.write("\n")
    else:
        if random.randint(0, 100)==0:
            time.append(test_data_generator(time[:-1], 3000000, 0, 20, True))
            temperature.append(test_data_generator(temperature[:-1], 100, -100, 5))
            altitude.append(test_data_generator(altitude[:-1], 1000, 20, 20))
        if random.randint(0, 1000)==0:
            time2.append(test_data_generator(time2[:-1], 3000000, 0, 20, True))
            longitude.append(test_data_generator(longitude[:-1], 90, -90, 20))
            latitude.append(test_data_generator(latitude[:-1], 1000, 20, 20))

    plt.subplot(3, 1, 1)
    plt.plot(time, temperature, 'yo-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Temperature(deg C)')

    plt.subplot(3, 1, 2)
    plt.plot(time, altitude, 'go-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Altitude(m)')

    """plt.subplot(3, 1, 3)
    plt.scatter(longitude, latitude, c='blue', marker='o')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    mplleaflet.display(fig=fig)"""

ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
plt.show()
if not TEST_MODE:
    ser.close()
file.close()