# Dependencies
from MainWindow import MainWindow
from PyQt5.Qt import *

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
from pyqtgraph.dockarea import *

# numpy
import numpy as np

# Dates
from datetime import datetime
import time

# CSV files
import csv

from message import MotorCommand

# Operating system
import os
import sys

# custom imports
from utils import *
from SerialParser import *
from SerialHandler import *

# color palettes
import seaborn as sns

class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)

        self.firstOpen = True

        # main objects in window
        self.serialSelector = None
        self.serialHandler = None
        self.main = None

        # configure general pyqtgraph options
        self.configurePyQtGraph()

        # Serial configurator
        self.device = 'COM3'
        self.baudrate = 115200

        # Prepare Serial handler
        self.serialHandler = SerialHandler(self)
        self.serialHandler.bufferUpdated.connect(self.updateData)

        # main window
        self.main = MainWindow(self)
        self.lastWindowClosed.connect(self.closeWindow)
        self.configureSlots()
        self.main.setWindowTitle('Control Viewer')
        self.main.show()

        # prepare variables
        self.isDeviceInit = False
        self.isFirstMessage = True

        self.showData = False
        self.isMoving = False

        self.selectedController = 'Position'

        # data logging
        self.isLogging = False
        self.wasDataSaved = False
        self.logFile = None
        self.logHandler = None
        self.logFilename = None

        # set initial buttons states
        # # self.main.buttonBrake.setEnabled(False)
        self.main.buttonStart.setEnabled(False)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(False)
        self.main.buttonSend.setEnabled(False)
        self.main.buttonSelectController.setEnabled(False)

        self.cmd = MotorCommand()
        self.CMD = namedtuple('CMD', 'id cmd pref P I D')

    def sendCMD(self,id,cmd,pref,p,i,d):
        cmd = self.CMD(id,cmd,pref,p,i,d) # request PID values
        self.cmd.fromTuple(cmd)
        self.serialHandler.send_command(self.cmd)

    def closeWindow( self ):
        if self.isDeviceInit:
            self.serialHandler.stopThread.emit()
            self.isDeviceInit = False

        # # check if there are temporal files before start again
        # if self.logFile:
        #     # close file
        #     self.logFile.close()
        #     # delete temporal
        #     print('borrando todos los temporales')
        #     os.remove(self.logFilename)

        self.exit(0)

    # configuration of actions executed by the MainWIndow
    def configureSlots(self):
        self.main.buttonSelect.clicked.connect(self.actionSelectButton)
        self.main.buttonRefresh.clicked.connect(self.actionRefreshButton)
        self.main.buttonReset.clicked.connect(self.actionResetButton)
        self.main.buttonStart.clicked.connect(self.actionStartButton)
        # self.main.buttonBrake.clicked.connect(self.actionBrakeButton)
        self.main.buttonStop.clicked.connect(self.actionStopButton)
        self.main.buttonSelectController.clicked.connect(self.actionSelectController)
        self.main.pSlider.valueChanged.connect(self.setPValue)
        self.main.iSlider.valueChanged.connect(self.setIValue)
        self.main.dSlider.valueChanged.connect(self.setDValue)
        self.main.buttonSend.clicked.connect(self.actionSendButton)
        self.main.refSlider.valueChanged.connect(self.refSliderMoved)
        self.main.refSlider.sliderReleased.connect(self.refSliderReleased)

    def actionRefreshButton(self):
        # read available interes
        serialDevices   = getSerialDevices()
        serialBaudrates = getSerialBaudrates()

        self.main.comboBoxDevices.clear()

        for dev in serialDevices:
            self.main.comboBoxDevices.addItem(dev)
            self.main.comboBoxDevices.setCurrentIndex(serialDevices.index(self.device))

        if serialDevices:
            for baud in serialBaudrates:
                self.main.comboBoxBaudrates.addItem(str(baud))
                self.main.comboBoxBaudrates.setCurrentIndex(serialBaudrates.index(self.baudrate))

    def actionSelectButton(self):
        #self.sendCMD(0,99,0,0,0,0);
        self.device = self.main.comboBoxDevices.currentText()

        serialDevices = getSerialDevices()
        serialBaudrates = getSerialBaudrates()

        if self.device in serialDevices:
            self.baudrate = self.main.comboBoxBaudrates.currentText()
        else:
            self.actionRefreshButton()

        print('[INFO] Connected to '+self.device+' at '+self.baudrate)
        self.serialHandler.setInterface(self.device, self.baudrate)
        self.isDeviceInit = True
        self.serialHandler.startThread.emit()

        self.controllers = ['Position','Speed','Tension']
        for cont in self.controllers:
            self.main.comboBoxController.addItem(cont)

        self.main.buttonRefresh.setEnabled(False)
        self.main.buttonSelectController.setEnabled(True)
        self.main.buttonSelect.setEnabled(False)
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        #self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

        self.main.comboBoxController.setCurrentIndex(self.controllers.index('Speed'))
        self.actionSelectController()

        self.sendCMD(0,20,0,0,0,0) # stop data stream

        time.sleep(0.5)

    def actionResetButton(self):
        self.sendCMD(0,20,0,0,0,0) # stop data stream
        self.sendCMD(0,99,0,0,0,0) # psoc software reset
        self.showData = False
        self.isMoving = False
        self.selectedController = None

        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(False)
        self.main.buttonSend.setEnabled(False)

        time.sleep(1)
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

        self.actionSelectController()
        time.sleep(0.1)

    def actionStartButton(self):
        self.main.buttonStop.setEnabled(True)
        # self.main.buttonBrake.setEnabled(True)
        self.main.buttonSelectController.setEnabled(False)
        self.main.buttonStart.setEnabled(False)
        self.main.buttonSend.setEnabled(True)

        self.showData = True

        if self.isMoving == False:
            self.move()

        # self.sendCMD(0,40,0,0,0,0) # continuously send data
        # self.serialHandler.sendMsg.emit('s\n')

        # start logging
        self.isLogging = True

        # # check if there are temporal files before start again
        # if self.logFile:
        #     # close file
        #     self.logFile.close()
        #     # delete temporal
        #     print('borrando %s' % self.logFilename)
        #     os.remove(self.logFilename)

        now = datetime.now()
        self.logFilename = "datos_%s_%s_%s_%s_%s_%s_%s.csv" % (self.selectedController,now.year, now.month, now.day, now.hour, now.minute, now.second)

        # prepare header
        #header = []
        #headerText = "Ref %s;Actual %s;Time" % (self.selectedController,self.selectedController)
        #header.append(headerText)

        # open file
        self.logFile = open(self.logFilename, 'w', newline='')
        self.logHandler = csv.writer(self.logFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #self.logHandler.writerow(header)
        print('created %s' % self.logFilename)

        '''
    def actionBrakeButton(self):
        if self.isMoving == True:
            self.brake()
        else:
            self.move()
        '''

    def brake(self):
        self.sendCMD(0,20,0,0,0,0) # stop sending data
        self.sendCMD(0,24,0,0,0,0) # toggle enable 0

        #self.serialHandler.sendMsg.emit('b\n')
        self.changeBrakenButton()
        self.isMoving = False

    def move(self):
        self.sendCMD(0,40,0,0,0,0) # resume sending data
        self.sendCMD(0,44,0,0,0,0) # resume enable
        self.changeBrakenButton()
        self.isMoving = True


    def actionStopButton(self):
        self.main.buttonStart.setEnabled(False)
        self.main.buttonStop.setEnabled(True)
        # self.main.buttonBrake.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)
        self.main.buttonSelectController.setEnabled(True)

        if self.isMoving == True:
            self.brake()
        else:
            self.move()

        #self.isLogging = False
        #self.logFile.close()


    def changeBrakenButton(self):
        if self.isMoving == True:
            self.main.buttonStop.setText("RESUME")
            self.main.buttonStop.setStyleSheet('QPushButton {color: green;}')
        else:
            self.main.buttonStop.setText("STOP")
            self.main.buttonStop.setStyleSheet('QPushButton {color: red ;}')


    def actionSelectController(self):

        if self.main.comboBoxController.currentText() != self.selectedController:
            self.selectedController = self.main.comboBoxController.currentText()
            self.main.refSliderLabel.setText(self.selectedController)
            if self.selectedController == 'Position':
                self.sendCMD(0,23,1,0,0,0) # set position control mode
                self.sendCMD(0,22,1,0,0,0)  # request PID values
                self.selectPositionController()
            elif self.selectedController == 'Speed':
                self.sendCMD(0,23,0,0,0,0) # set speed control mode
                self.sendCMD(0,22,0,0,0,0)  # request PID values
                self.selectSpeedController()
            elif self.selectedController == 'Tension':
                controlSelectCMD = self.CMD(0,23,0,-1,0,0) # set tension control mode
                self.cmd.fromTuple(controlSelectCMD)
                self.serialHandler.send_command(self.cmd)

                askparams = self.CMD(0,22,0,-1,0,0,0) # request PID values
                self.cmd.fromTuple(askparams)
                self.serialHandler.send_command(self.cmd)
                #self.serialHandler.sendCompoundMsg.emit('?',3)
                self.selectTensionController()

            self.main.mainPlot.clearData()

            # self.main.buttonBrake.setEnabled(False)
            #self.main.buttonStart.setEnabled(True)
        elif self.selectedController == 'Position':
            self.selectPositionController()
            self.sendCMD(0,23,1,0,0,0) # set position control mode
            self.sendCMD(0,22,1,0,0,0)  # request PID values


    def selectPositionController(self):
        self.main.refSliderLabel.setText('Position Ref')
        self.main.refSlider.setMinimum(-500)
        self.main.refSlider.setMaximum(500)
        self.main.refSlider.setTickInterval(10)
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')

    def selectSpeedController(self):
        self.main.refSliderLabel.setText('Speed Ref')
        self.main.refSlider.setMinimum(0)
        self.main.refSlider.setMaximum(9000)
        self.main.refSlider.setTickInterval(500)
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')

    def selectTensionController(self):
        self.main.refSliderLabel.setText('Tension Ref')
        self.main.refSlider.setMinimum(0)
        self.main.refSlider.setMaximum(1200)
        self.main.refSlider.setTickInterval(100)
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')


    def setPValue(self):
        self.main.pValue.setText(str('%.4f'%(self.main.pSlider.value()/4096)))
        #self.serialHandler.sendCompoundMsg.emit('P',self.main.pSlider.value())

    def setIValue(self):
        self.main.iValue.setText(str('%.4f'%(self.main.iSlider.value()/4096)))
        #self.serialHandler.sendCompoundMsg.emit('I',self.main.iSlider.value())

    def setDValue(self):
        self.main.dValue.setText(str('%.4f'%(self.main.dSlider.value()/4096)))
        #self.serialHandler.sendCompoundMsg.emit('D',self.main.dSlider.value())
    def actionSendButton(self):
        P = self.main.pSlider.value()
        I = self.main.iSlider.value()
        D = self.main.dSlider.value()
        print(P,I,D)
        self.sendCMD(0,25,0,P,I,D)
        self.main.mainPlot.clearData()

    def refSliderMoved(self):
        self.main.refSliderValue.setText(str(self.main.refSlider.value()))

    def refSliderReleased(self):
        value = self.main.refSlider.value()
        # print(value)
        if self.selectedController == 'Position':
            self.sendCMD(0,1,value,0,0,0) # set position reference
            # self.serialHandler.sendCompoundMsg.emit('!',self.main.refSlider.value())
        elif self.selectedController == 'Speed':
            self.sendCMD(0,0,value,0,0,0) # set position reference
            #self.serialHandler.sendCompoundMsg.emit('#',self.main.refSlider.value())
        elif self.selectedController == 'Tension':
            self.serialHandler.sendCompoundMsg.emit('$',self.main.refSlider.value())

    # Methods to handle serial data
    def updateData(self, msg, fmt):

        data = serialParser(msg,fmt)
        #print(sensorData)
        if(data[0] == 1):   # for graphics
            # update plot
            #"Ref %s;Actual %s;Time" % (self.selectedController,self.selectedController)
            #print(sensorData)
            ref,actual,time,tens = self.main.mainPlot.update(data)
            if self.isLogging:
                txt = "%f;%d;%d;%d" % (time,ref,actual,tens)
                row = []
                row.append(txt)
                self.logHandler.writerow(row)

        if(data[0] == 5):   # update pid parameters in main
            self.main.pSlider.setValue(data[1])
            self.main.pValue.setText(str('%.4f'%(data[1]/4096)))
            self.main.iSlider.setValue(data[2])
            self.main.iValue.setText(str('%.4f'%(data[2]/4096)))
            self.main.dSlider.setValue(data[3])
            self.main.dValue.setText(str('%.4f'%(data[3]/4096)))

        if isinstance(data,str):
            print(data)
            #pass

        elif isinstance(data,dict):
            # update plot
            #"Ref %s;Actual %s;Time" % (self.selectedController,self.selectedController)
            #print(sensorData)
            ref,actual,time,tens = self.main.mainPlot.update(data)
            if self.isLogging:
                txt = "%f;%d;%d;%d" % (time,ref,actual,tens)
                row = []
                row.append(txt)
                self.logHandler.writerow(row)

        elif isinstance(data,int):
            #print(sensorData)
            if(data == 1):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Position'))
                self.selectedController = 'Position'
                self.selectPositionController()
            elif(data == 2):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Speed'))
                self.selectedController = 'Speed'
                self.selectSpeedController()
            elif(data == 3):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Tension'))
                self.selectedController = 'Tension'
                self.selectTensionController()


        self.processEvents()

    def configurePyQtGraph(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
