# -*- coding: utf-8 -*

# HandSerial class for multi motor control
#

from MotorCommand import MotorCommand
from collections import namedtuple
from threading import Lock, Thread
import serial
from array import array
from struct import *

from io import BytesIO

class HandSerial(object):

    def __init__(self,port='COM4',baudrate=115200):

        self.device = port
        self.baudrate = baudrate
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
        #print("Hex: {}".format(to_hex(data)))
        #print("BIN: {}".format(to_byte(data)))
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(data)

    def handle_data(self,data):
        print(data)

    def serialHandlerThread(self):

        #RxBuff = struct.Struct('<BhhB')
        struct_fmt = '<BBhhh' # B uchar, h short, 11222 = 8 bytes total
        struct_len = calcsize(struct_fmt)
        #rxCom = namedtuple('rxCom','xff com ref cur val')
        while self.running is True:
            #if self.ser.in_waiting > 0 :
            try:
                if self.ser.inWaiting():
                    msg = self.ser.read(struct_len)  # show the message as it is
                    print(msg) # b'a100000000'
                    rxCom = unpack(struct_fmt, msg)
                    cur = rxCom[3]
                    #print(rxCom)


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

    def sendCMD(self,id,cmd,pref=0,p=0,i=0,d=0):
        aux = self.CMD(id,cmd,pref,p,i,d)
        self.cmd.fromTuple(aux)
        self.send_command()
