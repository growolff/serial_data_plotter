from PyQt5.Qt import *
import threading
import serial
import time

"""
Class Serial handler

This class opens a serial device with the defined port and baudrate
and keeps emiting messages using pyqt signals

"""

class SerialHandler(QObject):
    bufferUpdated = pyqtSignal(str)

    sendMsg = pyqtSignal(str)
    sendCompoundMsg = pyqtSignal(str,float)
    setREF = pyqtSignal(str,int)
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
        self.device = 'COM10'
        self.baudrate = 115200
        self.rate = 1000000000000000000000

        # prepare connections with parent window
        self.startThread.connect(self.startProcess)
        self.stopThread.connect(self.stopProcess)
        self.pauseThread.connect(self.pauseProcess)
        self.resumeThread.connect(self.resumeProcess)
        self.flushSerial.connect(self.flush)
        self.sendMsg.connect(self.emitAlone)
        self.sendCompoundMsg.connect(self.emitCompound)

        self.alone = None
        self.compound = None
        self.refMsg = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.stopProcess()

    def setInterface(self, device, baudrate):
        self.device = device
        self.baudrate = baudrate

    def isRunning(self):
        return (self.running or not self.pause)

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

    @pyqtSlot(str)
    def emitAlone(self,command):
        self.alone = command
        time.sleep(0.1)
        #print ('tx callback: ', command,self.command, type(command), type(self.command))

    @pyqtSlot(str,float)
    def emitCompound(self,command,value):
        self.compound = "%s%d\n"%(command,value)
        time.sleep(0.1)

    # main thread
    def serialHandlerThread(self):
        self.ser = serial.Serial(self.device, self.baudrate, timeout=0.1)

        while self.running is True:

            if self.alone is not None:
                print(self.alone)
                self.ser.write(bytes(self.alone,'UTF-8'))
                self.alone = None

            if self.compound is not None:
                print(self.compound)
                self.ser.write(bytes(self.compound,'UTF-8'))
                self.compound = None

            # read messages
            try:
                #print('Reading messages')
                msg = self.ser.readline()
            except Exception as e:
                print("reading error")

            if msg:
                try:
                    #print(msg)
                    if not self.pause:
                        self.bufferUpdated.emit(str(msg, 'utf-8'))
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
