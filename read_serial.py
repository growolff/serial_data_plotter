# -*- coding: utf-8 -*

import serial, time

ser = serial.Serial('COM4', 115200)

while 1:
    serial_line = ser.readline().decode()

    print(serial_line) # If using Python 2.x use: print serial_line
    # Do some other work on the data

    # Loop restarts once the sleep is finished

ser.close() # Only executes once the loop exits
