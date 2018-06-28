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
'''
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        #QMainWindow.__init__(self)

        self.s = SerialHandler()
        self.s.send_command('q\n')

        #self.button = QtGui.QPushButton('Test', self)
        self.textbox = QLineEdit(self)
        self.textbox.move(10, 20)
        self.textbox.resize(100,20)

        #self.button.clicked.connect(self.on_click)
        self.textbox.returnPressed.connect(self.on_click)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.textbox,0,0)
        #self.grid.addWidget(self.button,1,0)

        #self.setLayout(self.grid)

        self.destroyed.connect(self.closeEvent)
        self.show()

    def closeEvent(self, event):
        self.s.stopProcess()
        event.accept()

    def __exit__(self, exc_type, exc_value, traceback):
        self.s.stopProcess()

    @pyqtSlot()
    def on_click(self):
        #textboxValue = self.textbox.text()
        msg = "%s\n"%(self.textbox.text())
        self.s.send_command(msg)
        self.textbox.setText("")
'''
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

        print(to_hex(buff.getvalue()))

        base_cmd_int = bytearray(buff.getvalue())
        #checksum = 255 - ( sum(base_cmd_int) % 256 )
        # Packet: FF  FF  BASE_CMD  CHECKSUM
        #packet = bytearray([0xFF, 0xFF]) + base_cmd_int + bytearray([checksum]) + bytearray([0x0D])
        packet = bytearray([0xFF, 0xFF]) + base_cmd_int + bytearray([0x0D])
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
                s.handle_data(msg)

        self.ser.close()


def main(HandSerial):
    #s.send_command('n') # needed to ask for PID params
    s.send_command('i') # needed for finishing starting loop

    s.send_command('W1E1')
    time.sleep(1)
    s.send_command('W1E0')
    #time.sleep(0.001)
    s.send_command('W1B1')
    time.sleep(1)
    s.send_command('W1B0')
    #time.sleep(0.001)
    s.send_command('W1D1')
    time.sleep(1)
    s.send_command('W1D0')
    #s.send_command('b\n')
    #time.sleep(1)

    # Mensaje para cambiar controlador
    #s.send_command('CXXXS0100') # P/S/T: pos/speed/tens | 0/1: neg/pos | 100: value

    s.send_command('CXXXS0100')

    #s.send_command('b\n')
    #s.send_command('s\n')
    #s.send_command('?2\n')
    #s.send_command('0211000\n')  # 0 - MOTOR - CONTROL - REF ; ej: 021-20 -> motor 2, control position, -20
    #s.send_command('013500\n')


    #time.sleep(3)
    #s.send_command('021-0\n')
    #s.send_command('0210\n')

    #s.send_command('013100\n')
    #s.send_command('013100\n')

    s.stopProcess()

def test(HandSerial):

    definedCommand = namedtuple('definedCommand',['cmd','motor','dpin','onoff','ctrl','valstr'])
    iniciar = definedCommand(ord('i'),1,ord('0'),1,ord('0'),valstr=255)
    print(iniciar)

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

    s.cmd.cmd = ord('C')#C
    s.cmd.motor = 1
    s.cmd.dpin = ord('E')#E
    s.cmd.onoff = 1
    s.cmd.ctrl = ord('S')#S
    s.cmd.valstr = 256
    s.send_command()

    time.sleep(1)
    s.stopProcess()

if __name__ == "__main__":
    #main(sys.argv)
    s = HandSerial()
    s.startProcess()

    test(s)
        #main(s)
    #except Exception:
     #   print('Chaito')
      #  s.stopProcess()
