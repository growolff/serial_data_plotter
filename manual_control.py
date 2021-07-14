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

def receiveData(motor):
    print("Enable data stream")
    s.sendCMD(motor,SEND_DATA_TRUE,0,0,0,0) # send data

def moveMotor(motor):
    origen = 0
    goal = 300

    print("Enable data stream")
    s.sendCMD(motor,SEND_DATA_TRUE,0,0,0,0) # send data

    print("Set control mode")
    s.sendCMD(motor,SET_CONTROL_MODE,POSITION_CONTROL,0,0,0) # set control mode position

    print("Enable motor")
    s.sendCMD(motor,ENABLE_MOTOR,0,0,0,0) # enable motor

    print("Set position reference")
    s.sendCMD(motor,SET_POS_REF,goal,0,0,0)
    time.sleep(2)

    print("Set position reference")
    s.sendCMD(motor,SET_POS_REF,origen,0,0,0)
    time.sleep(2)

    print("Disable motor")
    s.sendCMD(motor,DISABLE_MOTOR,0,0,0,0) # disable motor

def moveTwoMotors():
    origen = 0
    goal = 500

    s.sendCMD(1,SEND_DATA_TRUE,0,0,0,0) # send data
    s.sendCMD(1,SET_CONTROL_MODE,POSITION_CONTROL,0,0,0) # set control mode position
    s.sendCMD(0,SET_CONTROL_MODE,POSITION_CONTROL,0,0,0) # set control mode position

    s.sendCMD(0,ENABLE_MOTOR,0,0,0,0) # enable motor
    s.sendCMD(1,ENABLE_MOTOR,0,0,0,0) # enable motor

    s.sendCMD(0,SET_POS_REF,goal,0,0,0)
    time.sleep(0.1)
    s.sendCMD(1,SET_POS_REF,origen,0,0,0)

    time.sleep(2)
    s.sendCMD(0,SET_POS_REF,origen,0,0,0)
    time.sleep(0.1)
    s.sendCMD(1,SET_POS_REF,goal,0,0,0)
    time.sleep(2)
    #s.sendCMD(0,DISABLE_MOTOR,0,0,0,0) # disable motor
    #s.sendCMD(1,DISABLE_MOTOR,0,0,0,0) # disable motor

def pote_test(motor):
    print("Enable data stream")
    s.sendCMD(motor,40,0,0,0,0) # send data
    time.sleep(1)

    print("Set control mode")
    s.sendCMD(motor,SET_CONTROL_MODE,0,0,0,0) # set control mode speed
    time.sleep(1)

    print("Enable motor")
    s.sendCMD(motor,44,0,0,0,0) # enable motor
    time.sleep(1)


def test(HandSerial):

    s.cmd.id = 0 # si es cero no funciona, pero se corrige con los dos \xff al comienzo
    s.cmd.cmd = 12
    s.cmd.pref = 0
    s.cmd.P = 1500
    s.cmd.I = 0
    s.cmd.D = 0
    #s.send_command()

    try:
        #receiveData(1)
        #moveTwoMotors()
        moveMotor(0)
        #pote_test(0)
        #time.sleep(20)
        s.stopProcess()
    except Exception as e:
        print(e)
        s.stopProcess()

if __name__ == "__main__":

    s = HandSerial()
    s.startProcess()
    try:
        test(s)
    except Exception as e:
        print(e)
        s.stopProcess()
