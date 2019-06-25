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

from struct import *

class HandSerial(object):
    def __init__(self):

        self.device = 'COM4'
        self.baudrate = 115200
        self.running = False

        self.cmd = MotorCommand()
        self.CMD = namedtuple('CMD', 'id cmd pref P I D')

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
        #print(buff.getvalue())

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
        print("Hex: {}".format(to_hex(data)))
        #print("BIN: {}".format(to_byte(data)))
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(data)

    def handle_data(self,data):
        print(data)

    def serialHandlerThread(self):

        #RxBuff = struct.Struct('<BhhB')
        struct_fmt = '<BBhhh'
        struct_len = calcsize(struct_fmt)
        #rxCom = namedtuple('rxCom','xff com ref cur val')
        while self.running is True:
            #if self.ser.in_waiting > 0 :
            try:
                msg = self.ser.read(struct_len)  # show the message as it is
                #print(msg) # b'a100000000'
                ##MSG._make(unpack_from('<BBii', msg))
                rxCom = unpack(struct_fmt, msg)
                cur = rxCom[3]
                print(cur)
                #print(MSG.meas)

                #self.handle_data(MSG.reference)

            except Exception as e:
                print("reading error: ",e)

            '''
            try:
                #print('Reading messages')
                #msg = self.ser.readline().decode()  # decode special characters from the message
                msg = self.ser.readline()          # show the message as it is
                #com,ref,cur = unpack('=Bhh',self.ser.readline())

            except Exception as e:
                print("reading error: %s",e)

            if msg:

                #print(calcsize('=Bhh'))
            '''
        self.ser.close()

    def sendCMD(self,id,cm,pref,p,i,d):
        asd = self.CMD(id,cm,pref,p,i,d)
        self.cmd.fromTuple(asd)
        self.send_command()

def test(HandSerial):

    s.cmd.id = 0 # si es cero no funciona, pero se corrige con los dos \xff al comienzo
    s.cmd.cmd = 12
    s.cmd.pref = 0
    s.cmd.P = 1500
    s.cmd.I = 0
    s.cmd.D = 0
    #s.send_command()

    s.sendCMD(0,40,0,0,0,0) # send data
    time.sleep(1)

    s.sendCMD(0,23,0,0,0,0) # set control mode speed
    time.sleep(1)
    s.sendCMD(0,44,0,0,0,0) # enable motor
    time.sleep(1)

    s.sendCMD(0,0,4000,0,0,0) # set speed ref
    time.sleep(1)

    s.sendCMD(0,0,8000,0,0,0) # set speed ref
    time.sleep(1)

    s.sendCMD(0,0,4000,0,0,0) # set speed ref
    time.sleep(1)

    s.sendCMD(0,0,0,0,0,0) # set speed ref
    time.sleep(1)

    #s.sendCMD(0,1,100,0,0,0) # set reference
    #time.sleep(1)

    #s.sendCMD(0,25,0,200,0,0) # change pid
    #time.sleep(1)

    #s.sendCMD(0,1,-100,0,0,0) # set reference
    #time.sleep(1)

    #s.sendCMD(0,55,0,0,0,0)
    #time.sleep(1)
    '''
    s.sendCMD(0,25,0,200,10,0) # change pid
    time.sleep(1)


    #s.send_command
    time.sleep(5)

    setpid = comm(0,25,0,150,0,0) # change pid
    s.cmd.fromTuple(setpid)
    #s.send_command()
    time.sleep(1)

    moverRight = comm(0,1,100,0,0,0)
    s.cmd.fromTuple(moverRight)
    #s.send_command()
    time.sleep(5)

    iniciar = comm(0,24,0,0,0,0) # disable motor
    s.cmd.fromTuple(iniciar)
    s.send_command()


    time.sleep(1)

    '''
    s.stopProcess()

if __name__ == "__main__":

    s = HandSerial()
    s.startProcess()
    try:
        test(s)
    except Exception:
        print('Chaito')
        s.stopProcess()
