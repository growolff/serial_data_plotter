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
        self.device = 'COM10'
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

        self.selectedController = None

        # data logging
        self.isLogging = False
        self.wasDataSaved = False
        self.logFile = None
        self.logHandler = None
        self.logFilename = None

        # set initial buttons states
        self.main.buttonBrake.setEnabled(False)
        self.main.buttonStart.setEnabled(False)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(False)
        self.main.buttonSend.setEnabled(False)
        self.main.buttonSelectController.setEnabled(False)


    def closeWindow( self ):
        if self.isDeviceInit:
            self.serialHandler.stopThread.emit()
            self.isDeviceInit = False

        # check if there are temporal files before start again
        if self.logFile:
            # close file
            self.logFile.close()
            # delete temporal
            print('borrando todos los temporales')
            os.remove(self.logFilename)

        self.exit(0)

    # configuration of actions executed by the MainWIndow
    def configureSlots(self):
        self.main.buttonSelect.clicked.connect(self.actionSelectButton)
        self.main.buttonRefresh.clicked.connect(self.actionRefreshButton)
        self.main.buttonReset.clicked.connect(self.actionResetButton)
        self.main.buttonStart.clicked.connect(self.actionStartButton)
        self.main.buttonBrake.clicked.connect(self.actionBrakeButton)
        self.main.buttonStop.clicked.connect(self.actionStopButton)
        self.main.buttonSelectController.clicked.connect(self.actionSelectController)        
        self.main.pSlider.valueChanged.connect(self.setPValue)
        self.main.iSlider.valueChanged.connect(self.setIValue)
        self.main.dSlider.valueChanged.connect(self.setDValue)
        self.main.buttonSend.clicked.connect(self.actionSendButton)
        self.main.refSlider.valueChanged.connect(self.refSliderMoved)
        self.main.refSlider.sliderReleased.connect(self.refSliderReleased)

    def actionSelectButton(self):
        self.device = self.main.comboBoxDevices.currentText()

        serialDevices = getSerialDevices()
        serialBaudrates = getSerialBaudrates()

        if self.device in serialDevices:
            self.baudrate = self.main.comboBoxBaudrates.currentText()
        else:
            self.actionRefreshButton()

        #print('[INFO] Preparing Serial Handler')
        self.serialHandler.setInterface(self.device, self.baudrate)
        self.isDeviceInit = True
        self.serialHandler.startThread.emit()

        self.controllers = ['Position','Speed','Tension']
        for cont in self.controllers:
            self.main.comboBoxController.addItem(cont)

        self.main.buttonRefresh.setEnabled(False)
        self.main.buttonSelect.setEnabled(False)
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonBrake.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

    def actionRefreshButton(self):
        # read available interfaces
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

    def actionResetButton(self):
        self.serialHandler.sendMsg.emit('q\n')
        self.showData = False
        self.isMoving = False
        self.selectedController = None

        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonBrake.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

        
    def actionStartButton(self):
        self.main.buttonStop.setEnabled(True)
        self.main.buttonBrake.setEnabled(True)
        self.main.buttonSelectController.setEnabled(False)
        self.main.buttonStart.setEnabled(False)

        self.serialHandler.sendMsg.emit('n\n') # receive controller type
        self.actionSelectController()
        self.serialHandler.sendMsg.emit('i\n')
        time.sleep(0.1)
        self.showData = True
        self.move();
        self.serialHandler.sendMsg.emit('s\n')

        # start logging
        self.isLogging = True

        # check if there are temporal files before start again
        if self.logFile:
            # close file
            self.logFile.close()
            # delete temporal
            print('borrando %s' % self.logFilename)
            os.remove(self.logFilename)

        now = datetime.now()
        self.logFilename = "datos_%s_%s_%s_%s_%s_%s_%s.csv" % (self.selectedController,now.year, now.month, now.day, now.hour, now.minute, now.second)

        # prepare header
        header = []
        headerText = "Ref %s;Actual %s;Time" % (self.selectedController,self.selectedController)
        header.append(headerText)
        # wasTimeIncluded = False
        # for key in self.sensors:
        #     # include time columns
        #     if not wasTimeIncluded:
        #         header.append(self.sensors[key].xLabel)
        #         wasTimeIncluded = True
        #     # include data column
        #     header.append(self.sensors[key].yLabel)

        # open file
        self.logFile = open(self.logFilename, 'w', newline='')
        self.logHandler = csv.writer(self.logFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        self.logHandler.writerow(header)
        print('created %s' % self.logFilename)

    def actionBrakeButton(self):
        if self.isMoving == True:
            self.brake()
        else:
            self.move()
            

    def brake(self):
        self.serialHandler.sendMsg.emit('b\n')
        self.changeBrakenButton()
        self.isMoving = False

    def move(self):
        self.serialHandler.sendMsg.emit('b\n')
        self.changeBrakenButton()
        self.isMoving = True


    def actionStopButton(self):
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonBrake.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(False)
        self.main.buttonSelectController.setEnabled(True)

        self.actionBrakeButton();
        
        self.isLogging = False
        self.logFile.close()
 

    def changeBrakenButton(self):
        if self.isMoving == True:
            self.main.buttonBrake.setText("BRAKEn")
            self.main.buttonBrake.setStyleSheet('QPushButton {color: red;}')
        else:
            self.main.buttonBrake.setText("Running")
            self.main.buttonBrake.setStyleSheet('QPushButton {color: green;}')

    def actionSelectController(self):

        if self.main.comboBoxController.currentText() != self.selectedController:
            self.selectedController = self.main.comboBoxController.currentText()
            self.main.refSliderLabel.setText(self.selectedController)
            if self.selectedController == 'Position':
                self.serialHandler.sendCompoundMsg.emit('?',1)
                self.selectPositionController()
            elif self.selectedController == 'Speed':
                self.serialHandler.sendCompoundMsg.emit('?',2)
                self.selectSpeedController()
            elif self.selectedController == 'Tension':
                self.serialHandler.sendCompoundMsg.emit('?',3)
                self.selectTensionController()

            self.main.mainPlot.clearData()

            self.main.buttonBrake.setEnabled(False)
            #self.main.buttonStart.setEnabled(True)

    def selectPositionController(self):
        self.main.refSliderLabel.setText('Position Ref')  
        self.main.refSlider.setMinimum(-100)
        self.main.refSlider.setMaximum(100)
        self.main.refSlider.setTickInterval(10)
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')

    def selectSpeedController(self):
        self.main.refSliderLabel.setText('Speed Ref')  
        self.main.refSlider.setMinimum(0)
        self.main.refSlider.setMaximum(9500)
        self.main.refSlider.setTickInterval(500)   
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')

    def selectTensionController(self):
        self.main.refSliderLabel.setText('Tension Ref')  
        self.main.refSlider.setMinimum(0)
        self.main.refSlider.setMaximum(4000)
        self.main.refSlider.setTickInterval(500)
        self.main.refSlider.setValue(0)
        self.main.refSliderValue.setText('0')


    def setPValue(self):
        self.main.pValue.setText(str(self.main.pSlider.value()/100.0))
        #self.serialHandler.sendCompoundMsg.emit('P',self.main.pSlider.value())

    def setIValue(self):
        self.main.iValue.setText(str(self.main.iSlider.value()/100.0))
        #self.serialHandler.sendCompoundMsg.emit('I',self.main.iSlider.value())

    def setDValue(self):
        self.main.dValue.setText(str(self.main.dSlider.value()/100.0))
        #self.serialHandler.sendCompoundMsg.emit('D',self.main.dSlider.value())
    def actionSendButton(self):
        self.serialHandler.sendCompoundMsg.emit('P',self.main.pSlider.value())
        self.serialHandler.sendCompoundMsg.emit('I',self.main.iSlider.value())
        self.serialHandler.sendCompoundMsg.emit('D',self.main.dSlider.value())
        self.main.mainPlot.clearData()

    def refSliderMoved(self):
        self.main.refSliderValue.setText(str(self.main.refSlider.value()))

    def refSliderReleased(self):
        if self.selectedController == 'Position':
            self.serialHandler.sendCompoundMsg.emit('!',self.main.refSlider.value())
        elif self.selectedController == 'Speed':
            self.serialHandler.sendCompoundMsg.emit('#',self.main.refSlider.value())
        elif self.selectedController == 'Tension':
            self.serialHandler.sendCompoundMsg.emit('$',self.main.refSlider.value())

    # Methods to handle serial data
    def updateData(self, msg):
        sensorData = serialParser(msg)
        if isinstance(sensorData,str):
            print(sensorData)
        elif isinstance(sensorData,list):
            self.main.pSlider.setValue(sensorData[0])
            self.main.iSlider.setValue(sensorData[1])
            self.main.dSlider.setValue(sensorData[2])
            self.main.pValue.setText(str(sensorData[0]/100))
            self.main.iValue.setText(str(sensorData[1]/100))
            self.main.dValue.setText(str(sensorData[2]/100))
        elif isinstance(sensorData,dict):
            # update plot
            self.main.mainPlot.update(sensorData)
        elif isinstance(sensorData,int):
            #print(sensorData)
            if(sensorData == 1):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Position'))
                self.selectedController = 'Position'
                self.selectPositionController()
            elif(sensorData == 2):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Speed'))
                self.selectedController = 'Speed'
                self.selectSpeedController()
            elif(sensorData == 3):
                self.main.comboBoxController.setCurrentIndex(self.controllers.index('Tension'))
                self.selectedController = 'Tension'
                self.selectTensionController()


        self.processEvents()

    def configurePyQtGraph(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)