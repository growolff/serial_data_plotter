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

CMD_SEND_DATA_TRUE = 40
CMD_SEND_DATA_FALSE = 20
CMD_SET_POS_REF = 1
CMD_SET_FORCE_REF = 2
CMD_GET_PID_VALUES = 21
CMD_REQ_PID_VALUES = 22
CMD_SET_PID_VALUES = 23
CMD_SET_CONTROL_MODE = 24
CMD_DISABLE_MOTOR = 25
CMD_ENABLE_MOTOR = 26
CMD_DEBUG_VAR = 55
CMD_SOFTWARE_RESET = 99

FLOAT_TO_INT_SCALE = 4096

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
        self.device = 'COM4'
        self.baudrate = 115200

        # Prepare Serial handler
        self.serialHandler = SerialHandler(self)
        self.serialHandler.bufferUpdated.connect(self.updateData)

        # main window
        self.main = MainWindow(self)
        self.lastWindowClosed.connect(self.closeWindow)
        self.configureSlots()
        self.main.setWindowTitle('Motor GUI')
        self.main.show()

        # prepare variables
        self.isDeviceInit = False
        self.isFirstMessage = True

        self.showData = False
        self.isMoving = False

        self.selectedController = 'Position'

        self.selectedMotor = 0 #'M1'

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
        self.main.buttonStop.clicked.connect(self.actionStopButton)
        self.main.comboBoxMotors.currentIndexChanged.connect(self.changeMotor)
        self.main.buttonSelectController.clicked.connect(self.actionSelectController)
        self.main.pSlider.valueChanged.connect(self.setPValue)
        self.main.iSlider.valueChanged.connect(self.setIValue)
        self.main.dSlider.valueChanged.connect(self.setDValue)
        self.main.buttonSend.clicked.connect(self.actionSendButton)
        self.main.refSlider.valueChanged.connect(self.refSliderMoved)
        self.main.refSlider.sliderReleased.connect(self.refSliderReleased)

    def actionRefreshButton(self):
        print("[button] REFRESH")
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
        print("[button] SELECT")
        self.device = self.main.comboBoxDevices.currentText()

        serialDevices = getSerialDevices()

        if self.device in serialDevices:
            self.baudrate = self.main.comboBoxBaudrates.currentText()
        else:
            self.actionRefreshButton()

        self.serialHandler.setInterface(self.device, self.baudrate)
        self.serialHandler.ser.open()
        self.isDeviceInit = True
        self.serialHandler.startThread.emit()
        print('[INFO] Connected to '+self.device+' at '+self.baudrate)

        self.controllers = ['Position','Speed','Tension']
        for cont in self.controllers:
            self.main.comboBoxController.addItem(cont)

        self.motors = ['M1','M2']
        for cont in self.motors:
            self.main.comboBoxMotors.addItem(cont)

        # update buttons availability
        self.main.buttonRefresh.setEnabled(False)
        self.main.buttonSelectController.setEnabled(True)
        self.main.buttonSelect.setEnabled(False)
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

        self.main.comboBoxController.setCurrentIndex(self.controllers.index('Position'))
        #self.actionSelectController()

        self.sendCMD(self.selectedMotor,CMD_SEND_DATA_FALSE,0,0,0,0) # stop data stream
        self.sendCMD(self.selectedMotor,CMD_DISABLE_MOTOR,0,0,0,0) # stop motor
        #self.sendCMD(1,CMD_SOFTWARE_RESET,0,0,0,0) # psoc software reset
        self.sendCMD(self.selectedMotor,CMD_REQ_PID_VALUES,0,0,0,0) # request pid values

        self.actionSelectController()
        time.sleep(0.1)
        self.sendCMD(self.selectedMotor,CMD_SOFTWARE_RESET,0,0,0,0) # psoc software reset
        time.sleep(0.1)

    def actionStartButton(self):
        print("[action] START")
        self.main.buttonStop.setEnabled(True)
        self.main.buttonSelectController.setEnabled(False)
        self.main.buttonStart.setEnabled(False)
        self.main.buttonSend.setEnabled(True)

        self.sendCMD(1,CMD_SEND_DATA_TRUE,0,0,0,0) # start data stream
        self.sendCMD(1,CMD_ENABLE_MOTOR,0,0,0,0) # enable motor

        self.showData = True

        if self.isMoving == False:
            self.move()

        # start logging
        self.isLogging = False

        # # check if there are temporal files before start again
        # if self.logFile:
        #     # close file
        #     self.logFile.close()
        #     # delete temporal
        #     print('borrando %s' % self.logFilename)
        #     os.remove(self.logFilename)


        if self.isLogging == True:
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

    def actionResetButton(self):
        print("[action] RESET")
        self.sendCMD(1,CMD_SEND_DATA_FALSE,0,0,0,0) # stop data stream
        self.sendCMD(1,CMD_DISABLE_MOTOR,0,0,0,0) # stop motor
        self.sendCMD(1,CMD_SOFTWARE_RESET,0,0,0,0) # psoc software reset
        self.main.mainPlot.clearData()

        self.actionSelectController()

        self.showData = False
        self.isMoving = False
        self.selectedController = None
        self.showData = False

        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(False)
        self.main.buttonSend.setEnabled(False)

        time.sleep(1)
        self.main.buttonStart.setEnabled(True)
        self.main.buttonStop.setEnabled(False)
        self.main.buttonReset.setEnabled(True)
        self.main.buttonSend.setEnabled(True)

    def changeMotor(self):
        self.selectedMotor = self.main.comboBoxMotors.currentIndex()
        print(self.selectedMotor)

    def brake(self):
        self.sendCMD(self.selectedMotor,CMD_SEND_DATA_FALSE,0,0,0,0) # stop sending data
        self.sendCMD(self.selectedMotor,CMD_DISABLE_MOTOR,0,0,0,0) # toggle enable 0
        self.isMoving = False

    def move(self):
        self.sendCMD(self.selectedMotor,CMD_SEND_DATA_TRUE,0,0,0,0) # resume sending data
        self.sendCMD(self.selectedMotor,CMD_ENABLE_MOTOR,0,0,0,0) # resume enable
        self.isMoving = True


    def actionStopButton(self):
        if self.isMoving == True:
            print("[action] STOP")
            self.main.buttonStop.setText("RESUME")
            self.main.buttonStop.setStyleSheet('QPushButton {color: green;}')
            self.main.buttonSelectController.setEnabled(True)
            self.showData = False
            self.brake()
        else:
            print("[action] RESUME")
            self.main.buttonStop.setText("STOP")
            self.main.buttonStop.setStyleSheet('QPushButton {color: red ;}')
            self.main.buttonSelectController.setEnabled(False)
            self.showData = True
            self.move()

        # self.isLogging = False
        # self.logFile.close()

    def actionSelectController(self):
        print("[action] CONTROL SELECTION")

        if self.main.comboBoxController.currentText() != self.selectedController:
            self.selectedController = self.main.comboBoxController.currentText()
            self.main.refSliderLabel.setText(self.selectedController)
            if self.selectedController == 'Position':
                self.sendCMD(self.selectedMotor,CMD_SET_CONTROL_MODE,1,0,0,0) # set position control mode
                self.sendCMD(self.selectedMotor,CMD_REQ_PID_VALUES,0,0,0,0)  # request PID values
                self.selectPositionController()
            elif self.selectedController == 'Speed':
                self.sendCMD(self.selectedMotor,23,0,0,0,0) # set speed control mode
                self.sendCMD(self.selectedMotor,22,0,0,0,0)  # request PID values
                self.selectSpeedController()
            elif self.selectedController == 'Tension':
                controlSelectCMD = self.CMD(self.selectedMotor,23,0,-1,0,0) # set tension control mode
                self.cmd.fromTuple(controlSelectCMD)
                self.serialHandler.send_command(self.cmd)

                askparams = self.CMD(self.selectedMotor,22,0,-1,0,0,0) # request PID values
                self.cmd.fromTuple(askparams)
                self.serialHandler.send_command(self.cmd)
                #self.serialHandler.sendCompoundMsg.emit('?',3)
                self.selectTensionController()

            self.main.mainPlot.clearData()

            # self.main.buttonBrake.setEnabled(False)
            #self.main.buttonStart.setEnabled(True)
        elif self.selectedController == 'Position':
            self.selectPositionController()
            self.sendCMD(self.selectedMotor,CMD_SET_CONTROL_MODE,1,0,0,0) # set position control mode
            self.sendCMD(self.selectedMotor,CMD_REQ_PID_VALUES,1,0,0,0)  # request PID values


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
        self.main.pValue.setText(str('%.2f'%(self.main.pSlider.value()/self.main.factor)))
        #self.serialHandler.sendCompoundMsg.emit('P',self.main.pSlider.value())

    def setIValue(self):
        self.main.iValue.setText(str('%.2f'%(self.main.iSlider.value()/self.main.factor)))
        #self.serialHandler.sendCompoundMsg.emit('I',self.main.iSlider.value())

    def setDValue(self):
        self.main.dValue.setText(str('%.2f'%(self.main.dSlider.value()/self.main.factor)))
        #self.serialHandler.sendCompoundMsg.emit('D',self.main.dSlider.value())

    def actionSendButton(self):
        P = self.main.pSlider.value()
        I = self.main.iSlider.value()
        D = self.main.dSlider.value()
        print(P/self.main.factor,I/self.main.factor,D/self.main.factor)
        self.sendCMD(self.selectedMotor,CMD_SET_PID_VALUES,0,P,I,D)
        self.main.mainPlot.clearData()

    def refSliderMoved(self):
        self.main.refSliderValue.setText(str(self.main.refSlider.value()))

    def refSliderReleased(self):
        value = self.main.refSlider.value()
        print("[action] slider: "+str('%d'%(value)))
        if self.selectedController == 'Position':
            self.sendCMD(self.selectedMotor,CMD_SET_POS_REF,value,0,0,0) # set position reference
        elif self.selectedController == 'Speed':
            self.sendCMD(self.selectedMotor,0,value,0,0,0) # set position reference
            #self.serialHandler.sendCompoundMsg.emit('#',self.main.refSlider.value())
        elif self.selectedController == 'Tension':
            self.serialHandler.sendCompoundMsg.emit('$',self.main.refSlider.value())

    def configurePyQtGraph(self):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

    # Methods to handle serial data input
    def updateData(self, msg):
        cmd = list()
        for i in range(1,5):
            cmd.append(msg[i])

        print(cmd)

        if self.showData == True:
            ref,actual,time,tens = self.main.mainPlot.update(msg)

        if self.isLogging:
            txt = "%f;%d;%d;%d" % (time,ref,actual,tens)
            row = []
            row.append(txt)
            self.logHandler.writerow(row)

        #if(data[0] == 1):   # for graphics
            # update plot
            #"Ref %s;Actual %s;Time" % (self.selectedController,self.selectedController)
            #print(sensorData)

        if(cmd[0] == CMD_GET_PID_VALUES):   # update pid parameters in main window
            self.main.pSlider.setValue(cmd[1])
            self.main.pValue.setText(str('%.2f'%(cmd[1]/self.main.factor)))
            self.main.iSlider.setValue(cmd[2])
            self.main.iValue.setText(str('%.2f'%(cmd[2]/self.main.factor)))
            self.main.dSlider.setValue(cmd[3])
            self.main.dValue.setText(str('%.2f'%(cmd[3]/self.main.factor)))

        self.processEvents()
