# -*- coding: utf-8 -*

# Operating system
import os
import sys, getopt

import serial
import time

from threading import Lock, Thread
from collections import namedtuple

#from PyQt5.Qt import *
#from pyqtgraph.Qt import QtCore, QtGui
from array import array

from HandSerial import HandSerial

from struct import *

SEND_DATA_TRUE = 40
SEND_DATA_FALSE = 20
SET_POS_REF = 1
SET_FORCE_REF = 2
REQ_PID_VALUES = 22
SET_PID_VALUES = 23
SET_CONTROL_MODE = 24
DISABLE_MOTOR = 25
ENABLE_MOTOR = 26
DEBUG_VAR = 55
SOFTWARE_RESET = 99

POSITION_CONTROL = 1

def receiveData(t):
    print("Receiving data from controller...")
    s.sendCMD(0,SEND_DATA_TRUE,0,0,0,0) # send data
    time.sleep(t)

    #s.sendCMD(0,SEND_DATA_FALSE,0,0,0,0) # send data


def main(argv):
    tsleep = int(argv[1])
    try:
        receiveData(tsleep)
        #moveTwoMotors()
        #pote_test(0)
        s.stopProcess()
    except Exception as e:
        print(e)
        s.stopProcess()


if __name__ == "__main__":

    s = HandSerial()
    s.startProcess()
    try:
        #test(s)
        main(sys.argv[0:])
    except Exception as e:
        print(e)
        s.stopProcess()
