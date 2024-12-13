"""
This file is used to plot the data from a serial port and save it to a text file.
"""

__author__ = 'KarmaDemon'

try:
    import program_files.cansattools as cansattools
    logger = cansattools.logger_creator("CanSat_real_time")
except ImportError:
    print("Error setting up logger. Cansattools can't be imported. Logging is disabled.")
    logger = None

try:
    import serial
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
except ImportError as e:
    logger.error("Error importing module: {e}")

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
FILE_NAME = "datas/raw_data.txt"
HEADER_ROW = ["Time", "Temperature", "Altitude"]

fig = plt.figure()
fig.canvas.set_window_title('REALTIME DATA PLOTTING')

try:
    ser = serial.Serial(SERIAL_PORT,BAUD_RATE)
except serial.SerialException as e:
    logger.error(f"Error opening serial port: {e}")
try:
    file = open("datas/raw_realtime_data.txt",'w')
except IOError as e:
    logger.error(f"Error opening file: {e}")
    file = None
file.write(" ".join(HEADER_ROW))
file.write("\n")

i = 0
time: list[int] = []
temperature: list[float] = []
altitude: list[float] = []
def animate() -> None:
    """
    Reads a line from the serial port, decodes it and splits it by whitespace.
    If the message has the correct format, it writes it to a file and appends the
    values to the time, temperature and altitude lists. It then plots the data
    in two subplots.

    :return: None
    """
    global i, time, temperature, altitude
    try:
        message: bytes = ser.readline()
    except serial.SerialException as e:
        logger.error(f"Error reading serial port: {e}")
        return
    # message has the following format: time temperature altitude\n
    if len(message) > 5:
        l = message.decode().split()  # decode bytes to string and split by whitespace
        print(l)
        if len(l) == 3:  # check if the message has the correct format
            time, temp, alt = l
            file.write(" ".join(l))
            file.write("\n")
            time.append(int(i))
            altitude.append(float(alt))
            temperature.append(float(temp))
            i = i+1

    plt.subplot(2, 1, 1)
    plt.plot(time,temperature,'yo-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Temperature(deg C)')

    plt.subplot(2, 1, 2)
    plt.plot(time,altitude,'go-')
    plt.xlabel('Time(ms)')
    plt.ylabel('Altitude(m)')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

ser.close()
file.close()