from PyQt5.Qt import *
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui

from SensorPlot import *

# Operating system
import os

class MainWindow(QMainWindow):
    # Constructor
    def __init__(self, parent):
        QMainWindow.__init__(self)

        self.parent = parent

        # prepare dock area for plots
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # Window configuration
        self.mainPlot = SensorPlot('Plot', self)

        # Configure Window
        self.configureWindow()

    def __exit__(self, exc_type, exc_value, traceback):
        self.buttonsDock.close()
        self.area.clear()

    # Configure full window
    def configureWindow(self):
        # Status Bar
        self.statusBar = QStatusBar()
        self.statusBarMessage = "Started"
        self.statusBar.showMessage(self.statusBarMessage)

        # grid layout for buttons
        self.leftDockSize = 280
        self.buttonsUI = pg.LayoutWidget()
        self.slidersUI = pg.LayoutWidget()

        # combo boxes for serial options
        self.labelDevices = QLabel("Puerto", self)
        self.buttonsUI.addWidget(self.labelDevices, row=0, col=0)
        self.comboBoxDevices = QComboBox(self)
        self.buttonsUI.addWidget(self.comboBoxDevices, row=1, col=0)

        self.labelBaudrates = QLabel("Baudrate", self)
        self.buttonsUI.addWidget(self.labelBaudrates, row=0, col=1)
        self.comboBoxBaudrates = QComboBox(self)
        self.buttonsUI.addWidget(self.comboBoxBaudrates, row=1, col=1)
        self.hasDevices = False

        # initialize buttons
        self.buttonSelect = QPushButton("Select", self)
        self.buttonsUI.addWidget(self.buttonSelect, row=2, col=0)

        self.buttonRefresh = QPushButton("Refresh", self)
        self.buttonsUI.addWidget(self.buttonRefresh, row=2, col=1)

        # start button
        self.buttonStart = QPushButton("Start")
        self.buttonsUI.addWidget(self.buttonStart, row=3, col=0)
        self.buttonStart.setShortcut('i')
        # reset button
        self.buttonReset = QPushButton("Reset")
        self.buttonsUI.addWidget(self.buttonReset, row=3, col=1)
        self.buttonStart.setShortcut('q')

        # Start visualization plots button
        self.buttonStop = QPushButton("Stop")
        self.buttonsUI.addWidget(self.buttonStop, row=4, col=0)
        self.buttonStop.setShortcut('s')

        # Motor HandBrake button
        self.buttonBrake = QPushButton("BRAKEn")
        self.buttonsUI.addWidget(self.buttonBrake, row=4, col=1)
        self.buttonBrake.setShortcut('b')
        self.buttonBrake.setStyleSheet('QPushButton {color: red;}')

        # 
        self.labelControl = QLabel("Controlador", self)
        self.buttonsUI.addWidget(self.labelControl, row=5, col=0)
        self.comboBoxController = QComboBox(self)
        self.buttonsUI.addWidget(self.comboBoxController, row=6, col=0)

        self.buttonSelectController = QPushButton("Select Controller", self)
        self.buttonsUI.addWidget(self.buttonSelectController, row=6, col=1)

        # controller reference slider
        self.refSliderLabel = QLabel("Controller Ref",self)
        self.refSliderValue = QLabel("0",self)
        self.refSlider = QSlider(Qt.Horizontal)
        self.refSlider.setMinimum(-50)
        self.refSlider.setMaximum(50)
        self.refSlider.setTickPosition(QSlider.TicksBelow)
        self.refSlider.setTickInterval(10)
        self.buttonsUI.addWidget(self.refSliderLabel, row=7,col=0)
        self.buttonsUI.addWidget(self.refSlider, row=7,col=1)
        self.buttonsUI.addWidget(self.refSliderValue, row=7,col=2)

        # P slider
        self.pLabel = QLabel("kP",self)
        self.pValue = QLabel("0",self)
        self.pSlider = QSlider(Qt.Horizontal)
        self.pSlider.setMinimum(0)
        self.pSlider.setMaximum(200)
        self.slidersUI.addWidget(self.pLabel, row=0,col=0)
        self.slidersUI.addWidget(self.pSlider, row=0,col=1)
        self.slidersUI.addWidget(self.pValue, row=0,col=2)
        self.pSlider.setTickPosition(QSlider.TicksBelow)
        self.pSlider.setTickInterval(10)

        # I slider
        self.iLabel = QLabel("kI",self)
        self.iValue = QLabel("0",self)
        self.iSlider = QSlider(Qt.Horizontal)
        self.iSlider.setMinimum(0)
        self.iSlider.setMaximum(200)
        self.slidersUI.addWidget(self.iLabel, row=1,col=0)
        self.slidersUI.addWidget(self.iSlider, row=1,col=1)
        self.slidersUI.addWidget(self.iValue, row=1,col=2)
        self.iSlider.setTickPosition(QSlider.TicksBelow)
        self.iSlider.setTickInterval(10)

        # D slider
        self.dLabel = QLabel("kD",self)
        self.dValue = QLabel("0",self)
        self.dSlider = QSlider(Qt.Horizontal)
        self.dSlider.setMinimum(0)
        self.dSlider.setMaximum(200)
        self.slidersUI.addWidget(self.dLabel, row=2,col=0)
        self.slidersUI.addWidget(self.dSlider, row=2,col=1)
        self.slidersUI.addWidget(self.dValue, row=2,col=2)
        self.dSlider.setTickPosition(QSlider.TicksBelow)
        self.dSlider.setTickInterval(10)

        # Send button
        self.buttonSend = QPushButton("Send")
        self.slidersUI.addWidget(self.buttonSend, row=3, col=1)
        self.slidersDock = Dock("Params", size=(1,1))
        self.slidersDock.addWidget(self.slidersUI)
        self.slidersDock.layout.setContentsMargins(10, 10, 10, 20)
        self.slidersDock.setFixedWidth(self.leftDockSize)

        # prepare widget for buttons
        self.buttonsDock = Dock("Options", size=(1, 1))
        #self.buttonsDock.setFixedWidth(self.buttonsBarSize)

        # add buttons to dock
        self.buttonsDock.addWidget(self.buttonsUI)
        self.buttonsDock.layout.setContentsMargins(10, 10, 10, 20)

        # add to main area
        self.area.addDock(self.buttonsDock, 'top')
        self.area.addDock(self.slidersDock, 'bottom')

        # add plot
        self.area.addDock(self.mainPlot.dockWindow, 'right')
