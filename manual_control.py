# -*- coding: utf-8 -*

# Operating system
import os
import sys

import serial
import time

from threading import Lock, Thread
from collections import namedtuple

#from PyQt5.Qt import *
#from pyqtgraph.Qt import QtCore, QtGui
from array import array

from message import *

from io import BytesIO

class HandSerial(object):
    def __init__(self):

        self.device = 'COM4'
        self.baudrate = 115200
        self.running = False

        self.cmd = MotorCommand()

        self.serial_mutex = Lock()

        self.ser = serial.Serial(self.device, self.baudrate, timeout=0.1)

        self.thread = Thread(target=self.serialHandlerThread)
        #self.startProcess()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stopProcess()

    def close(self):
        """
        Close the serial port.
        """
        if self.ser:
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.close()

    def stopProcess(self):
        self.running = False

    def startProcess(self):
        self.running = True
        self.thread.start()

    def send_command_old(self,command):
        #msg = "Send command: %s"%(command)
        #print(msg)
        self.ser.write(bytes(command+'\n','UTF-8'))
        #self.ser.write(command)

    def send_command(self):

        buff = BytesIO()
        self.cmd.serialize(buff)

        #print(to_hex(buff.getvalue()))
        print(buff.getvalue())

        base_cmd_int = bytearray(buff.getvalue())
        #checksum = 255 - ( sum(base_cmd_int) % 256 )
        # Packet: FF  FF  BASE_CMD  CHECKSUM
        #packet = bytearray([0xFF, 0xFF]) + base_cmd_int + bytearray([checksum]) + bytearray([0x0D])

        packet = bytearray([0xFF,0xFF]) + base_cmd_int + bytearray([0x0D])
        packet_str = array('B', packet).tostring()
        with self.serial_mutex:
            self.write_serial(packet_str)

    def write_serial(self, data):
        """
        Write in the serial port.
        """
        #print(self.cmd)
        #print("Hex: {}".format(to_hex(data)))
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(data)

    def handle_data(self,data):
        print(data)

    def serialHandlerThread(self):

        while self.running is True:

            try:
                #print('Reading messages')
                #msg = self.ser.readline().decode()  # decode special characters from the message
                msg = self.ser.readline()          # show the message as it is
            except Exception as e:
                print("reading error: %s",e)

            if msg:
                self.handle_data(msg)

        self.ser.close()

def test(HandSerial):

    s.cmd.id = 0 # si es cero no funciona, pero se corrige con los dos \xff al comienzo
    s.cmd.cmd = 12
    s.cmd.pref = 0
    s.cmd.tref = 255
    s.cmd.P = 1500
    s.cmd.I = 0
    s.cmd.D = 0
    #s.send_command()

    comm = namedtuple('comm', 'id cmd pref tref P I D')
    #iniciar = definedCommand(ord('i'),1,ord('0'),1,ord('0'),valstr=255)
    #print(iniciar)

    moverLeft = comm(0,1,-100,0,0,0,0)

    moverRight = comm(0,1,100,0,0,0,0)

    getData = comm(0,12,0,0,0,0,0)
    #s.cmd.fromTuple(getData)
    #s.send_command()

    time.sleep(2)
    s.cmd.fromTuple(moverLeft)
    s.send_command()
    #print(moverLeft)

    time.sleep(2)
    s.cmd.fromTuple(moverRight)
    s.send_command()


    '''
    turnOnRed = definedCommand(ord('W'),1,ord('E'),1,ord('S'),valstr=255)
    turnOffRed = definedCommand(ord('W'),1,ord('E'),0,ord('S'),valstr=255)
    turnOnBlue = definedCommand(ord('W'),1,ord('B'),1,ord('S'),valstr=255)
    turnOffBlue = definedCommand(ord('W'),1,ord('B'),0,ord('S'),valstr=255)
    turnOnGreen = definedCommand(ord('W'),1,ord('D'),1,ord('S'),valstr=255)
    turnOffGreen = definedCommand(ord('W'),1,ord('D'),0,ord('S'),valstr=255)

    s.cmd.fromTuple(iniciar)
    s.send_command()
    time.sleep(1)

    s.cmd.fromTuple(turnOnRed)
    s.send_command()
    time.sleep(1)

    s.cmd.fromTuple(turnOffRed)
    s.send_command()
    s.cmd.fromTuple(turnOnBlue)
    s.send_command()
    time.sleep(1)

    s.cmd.fromTuple(turnOffBlue)
    s.send_command()
    s.cmd.fromTuple(turnOnGreen)
    s.send_command()
    time.sleep(1)

    s.cmd.fromTuple(turnOffGreen)
    s.send_command()
    time.sleep(1)
    '''

    time.sleep(1)
    s.stopProcess()

if __name__ == "__main__":

    s = HandSerial()
    s.startProcess()
    try:
        test(s)
    except Exception:
        print('Chaito')
        s.stopProcess()
