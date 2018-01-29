# -*- coding: utf-8 -*-

# Operating system
import os
import sys

import serial
import time

import threading

from PyQt5.Qt import *
from pyqtgraph.Qt import QtCore, QtGui

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

class SerialHandler():
    def __init__(self):

        self.device = 'COM10'
        self.baudrate = 115200
        self.running = False

        self.ser = serial.Serial(self.device, self.baudrate, timeout=0.1)

        self.thread = threading.Thread(target=self.serialHandlerThread)
        #self.startProcess()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stopProcess()

    def stopProcess(self):
        self.running = False

    def startProcess(self):
        self.running = True
        self.thread.start()

    def send_command(self,command):
        msg = "Send command: %s"%(command)
        print(msg)
        self.ser.write(bytes(command,'UTF-8'))

    def serialHandlerThread(self):

        while self.running is True:

            try:
                #print('Reading messages')
                msg = self.ser.readline()
            except Exception as e:
                print("reading error")

            if msg:
                print(msg)

        self.ser.close()


def main(args):
    app = QtGui.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

def main2():
    s = SerialHandler()
    #s.startProcess()

    #print(s.ser)

    #s.send_command('q\n')
    #s.send_command('i\n')
    
    #s.send_command('b\n')    
    time.sleep(1)
    #s.send_command('b\n')
    #s.send_command('s\n')
    #s.send_command('?2\n')    
    s.send_command('011-100\n')
    s.send_command('021-100\n')


    time.sleep(3)
    s.send_command('0110\n')
    s.send_command('0210\n')

if __name__ == "__main__":
    #main(sys.argv)
    main2()
    