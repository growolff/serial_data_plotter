from PyQt5.Qt import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np

from pyqtgraph.dockarea import *
import random as r

# Sensor handler class
import datetime
import time
from datetime import datetime

from utils import *

class SensorPlot:
    def __init__(self, id, parentWidget):
        self.enableMenu = False

        self.id = id
        self.color = (255,0,255)
        self.name = str(self.id)
        self.maxDataSize = 500
        self.yData = np.zeros(self.maxDataSize)
        self.xData = np.zeros(self.maxDataSize)
        self.time = np.zeros(self.maxDataSize)

        self.xIdx = 0
        self.yIdx = 0
        self.timeIdx = 0

        self.isFirst = True
        self.initialTime = 0
        self.initialX = 0

        self.currentX = 0
        self.currentY = 0
        self.currentTime = 0
        self.xLabel = None
        self.yLabel = None
        self.xUnits = None
        self.yUnits = None

        # prepare dock widget
        self.dockWindow = Dock(self.name, size=(1, 1))

        # Layout
        self.layout = pg.LayoutWidget()
        self.layout.layout.setSpacing(0)

        # Current value label
        self.layoutHeader = pg.LayoutWidget()

        self.label = QtGui.QLabel("Valor actual: ")
        self.layoutHeader.addWidget(self.label, row=0, col=0)
        self.layout.addWidget(self.layoutHeader, row=0, col=0)

        # prepare plot
        self.widgetPlot = pg.PlotWidget(enableMenu=self.enableMenu, title="Gonza3")
        self.widgetPlot.showGrid(x=True, y=True, alpha=0.5)
        self.layout.addWidget(self.widgetPlot, row=1, col=0)

        self.penPlot = pg.mkPen(color=self.color, width=1)
        self.penPlot2 = pg.mkPen(color=(0,100,200), width=1)
        self.plot = self.widgetPlot.plot(pen=self.penPlot)
        self.plot2 = self.widgetPlot.plot(pen=self.penPlot2)

        # add everything to dock
        self.dockWindow.addWidget(self.layout)

    def __exit__(self, exc_type, exc_value, traceback):
        self.clearData()
        self.dockWindow.close()

    def update(self, measurement):

        currentTime = datetime.today().timestamp()

        if self.isFirst:
            self.isFirst = False

            self.initialTime = currentTime

            # configure labels
            self.widgetPlot.setLabel('bottom', text=self.xLabel, units=self.xUnits)
            self.widgetPlot.setLabel('left',   text=self.yLabel, units=self.yUnits)
            self.widgetPlot.setTitle(self.name)

        #self.currentX = measurement.xData - self.initialX
        # self.currentY = measurement["Actual:"]
        # self.refY = measurement["Ref:"]
        self.currentY = measurement[1]
        self.refY = measurement[2]
        self.val = measurement[3]
        self.currentTime = currentTime - self.initialTime

        #print(self.xIdx, self.currentX)
        #print(self.yIdx, self.currentY)

        self.yData[self.yIdx] = self.currentY # y current
        self.xData[self.xIdx] = self.refY # x ref
        self.time[self.timeIdx] = self.currentTime

        # Update current value label
        self.label.setText(self.name + " Actual: " + str(self.currentY))

        # increase counters
        self.yIdx = (self.yIdx + 1) % self.maxDataSize
        self.xIdx = (self.xIdx +1) % self.maxDataSize
        self.timeIdx = (self.timeIdx + 1) % self.maxDataSize

        # update plots
        xDataTmp = np.concatenate( (self.xData[self.xIdx:], self.xData[0:self.xIdx]), axis=0)
        yDataTmp = np.concatenate( (self.yData[self.yIdx:], self.yData[0:self.yIdx]), axis=0)
        timeDataTmp = np.concatenate( (self.time[self.timeIdx:], self.time[0:self.timeIdx]), axis=0)
        #print(xDataTmp)

        self.plot.setData(x=timeDataTmp, y=yDataTmp)
        self.plot2.setData(x=timeDataTmp, y=xDataTmp)

        return int(self.refY),int(self.currentY),float(self.currentTime),int(self.val)

    def clearData(self):
        currentTime = datetime.today().timestamp()

        #lastY = self.yData[self.yIdx-1]
        #lastX = self.xData[self.xIdx-1]
        #lastTime = self.time[self.timeIdx-1]

        self.yData = np.zeros(self.maxDataSize)
        self.xData = np.zeros(self.maxDataSize)
        self.time = np.zeros(self.maxDataSize)

        self.yIdx = 0
        self.xIdx = 0
        self.timeIdx = 0
        self.isFirst = True


    def savePlot(self, directory):
        exporter = pg.exporters.ImageExporter(self.widgetPlot.getPlotItem())
        # set export parameters if needed
        exporter.params['width'] = int(1000)
        #exporter.params['height'] = int(1000)
        # save to file
        #print('%s/%s.png' % (directory, self.name))
        exporter.export('%s/%s.png' % (directory, self.name))
