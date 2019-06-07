from PyQt5.Qt import *
import threading
import serial
import time

from collections import namedtuple
from message import MotorCommand

from array import array

from io import BytesIO

import struct

"""
Class Serial handler

This class opens a serial device with the defined port and baudrate
and keeps emiting messages using pyqt signals

"""

class SerialHandler(QObject):

    bufferUpdated = pyqtSignal(bytes,str)
    #sendMsg = pyqtSignal(str)
    #sendCompoundMsg = pyqtSignal(str,float)
    #setREF = pyqtSignal(str,int)
    startThread = pyqtSignal()
    stopThread  = pyqtSignal()
    pauseThread = pyqtSignal()
    resumeThread  = pyqtSignal()
    flushSerial = pyqtSignal()

    def __init__(self, parent):
        super(SerialHandler, self).__init__()
        self.running = False
        self.pause = False
        self.thread = threading.Thread(target=self.serialHandlerThread)
        self.device = 'COM4'
        self.baudrate = 115200
        self.rate = 1000000000000000000000

        # prepare connections with parent window
        self.startThread.connect(self.startProcess)
        self.stopThread.connect(self.stopProcess)
        self.pauseThread.connect(self.pauseProcess)
        self.resumeThread.connect(self.resumeProcess)
        self.flushSerial.connect(self.flush)
        #self.sendMsg.connect(self.emitAlone)
        #self.sendCompoundMsg.connect(self.emitCompound)

        self.alone = None
        self.compound = None
        self.refMsg = None

        self.cmd = MotorCommand()
        self.serial_mutex = threading.Lock()

        self.ser = serial.Serial(self.device, self.baudrate, timeout=0.1)

        self.struct_fmt = '<BBhhh'
        self.struct_len = struct.calcsize(self.struct_fmt)

    def __exit__(self, exc_type, exc_value, traceback):
        self.stopProcess()

    def setInterface(self, device, baudrate):
        self.device = device
        self.baudrate = baudrate

    def isRunning(self):
        return (self.running or not self.pause)

    def to_hex(self,data):
        return ":".join("{:02x}".format(c) for c in data)

    def send_command(self,command):

        self.set_command(command)

        buff = BytesIO()
        self.cmd.serialize(buff)

        print(self.to_hex(buff.getvalue()))
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
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(data)

    def set_command(self,command):

        self.cmd.id = command.id
        self.cmd.cmd = command.cmd
        self.cmd.pref = command.pref
        self.cmd.P = command.P
        self.cmd.I = command.I
        self.cmd.D = command.D

    @pyqtSlot()
    def flush(self):
        #self.ser.reset_input_buffer()
        print(self.ser.readline())

    @pyqtSlot()
    def startProcess(self):
        self.running = True
        self.thread.start()

    @pyqtSlot()
    def stopProcess(self):
        self.running = False

    @pyqtSlot()
    def pauseProcess(self):
        self.pause = True

    @pyqtSlot()
    def resumeProcess(self):
        self.pause = False

    @pyqtSlot(int)
    def setRate(self, rate):
        self.rate = rate

    # main thread
    def serialHandlerThread(self):

        while self.running is True:
            '''
            if self.alone is not None:
                print(self.alone)
                self.ser.write(bytes(self.alone,'UTF-8'))
                self.alone = None

            if self.compound is not None:
                print(self.compound)
                self.ser.write(bytes(self.compound,'UTF-8'))
                self.compound = None
            '''
            # read messages
            try:
                #print('Reading messages')
                msg = self.ser.read(self.struct_len)
            except Exception as e:
                print("reading error")

            if msg:
                try:
                    #print("> %s"%(msg))
                    if not self.pause:
                        self.bufferUpdated.emit(msg,self.struct_fmt)
                except ValueError as e:
                    print('Wrong data')
                    print(e)
            #else:
            #    pass

            # handle sampling rate
            #time.sleep(1/self.rate)

        self.ser.write(bytes('q\n','UTF-8'))
        self.ser.close()
        return 0
