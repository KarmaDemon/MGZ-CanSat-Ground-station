"""
This file is used to plot the data from a serial port and save it to a text file. Do not open Arduino IDE while executing this file.
"""

__author__ = 'KarmaDemon'

try:
    from program_files.cansattools import logger_creator as logger_creator
    logger = logger_creator("CanSat_real_time")
except ImportError:
    print("Error setting up logger. Cansattools can't be imported. Logging is disabled.")
    logger = None

try:
    import serial
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
except ImportError as e:
    logger.error("Error importing module: {e}")

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
FILE_NAME = "datas/raw_data.txt"
HEADER_ROW = ["Time", "Temperature", "Altitude"]

fig = plt.figure()
fig_manager = plt.get_current_fig_manager()
fig_manager.set_window_title('Real time data visualization')

try:
    ser = serial.Serial(SERIAL_PORT,BAUD_RATE)
except serial.SerialException as e:
    logger.error(f"Error opening serial port: {e}", exc_info=True)
try:
    file = open("datas/raw_realtime_data.txt",'w')
except IOError as e:
    logger.error(f"Error opening file: {e}", exc_info=True)
    file = None
file.write(" ".join(HEADER_ROW))
file.write("\n")

sensor_name: list[str] = []
time: list[int] = []
temperature: list[float] = []
altitude: list[float] = []
def animate(frame) -> None:
    """
    This function is called periodically from FuncAnimation
    :param frame: int
    :return: None
    """
    global sensor_name, time, temperature, altitude
    try:
        message: bytes = ser.readline()
    except serial.SerialException as e:
        logger.error(f"Error reading serial port: {e}")
        return
    # message has the following format: time temperature altitude\n
    if len(message) > 5:
        l = message.decode().split()  # decode bytes to string and split by whitespace
        print(l)
        if len(l) == 5:  # check if the message has the correct format
            sensor_name, temp, pres, alt, i = l
            file.write("\t".join(l))
            file.write("\n")
            time.append(int(i))
            altitude.append(float(alt))
            temperature.append(float(temp))

    plt.subplot(2, 1, 1)
    plt.plot(time, temperature, 'yo-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Temperature(deg C)')

    plt.subplot(2, 1, 2)
    plt.plot(time, altitude, 'go-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Altitude(m)')

ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
plt.show()

ser.close()
file.close()