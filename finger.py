# -*- coding: utf-8 -*-

from HandSerial import HandSerial

import time

# finger cmds
F_OPEN = 30
F_CLOSE = 31
I_ME_OPEN_POS = 380
I_MF_OPEN_POS = 0

I_ME_CLOSED_POS = 0
I_MF_CLOSED_POS = 380

# motor defs
F1_ME_IDX = 1
F1_MF_IDX = 0

# motor cmds
SET_POS_REF = 1
SET_FORCE_REF = 2
REQ_PID_VALUES = 22
SET_PID_VALUES = 23
SET_CONTROL_MODE = 24
DISABLE_MOTOR = 25
ENABLE_MOTOR = 26

# system cmds
SEND_DATA_TRUE = 40
SEND_DATA_FALSE = 20
DEBUG_VAR = 55
SOFTWARE_RESET = 99

POSITION_CONTROL = 1

class Finger(object):

    def __init__(self, idx=0):
        self.ser = HandSerial()
        self.idx = idx

    def enable(self):
        self.ser.sendCMD(id=F1_ME_IDX,cmd=SET_CONTROL_MODE,pref=POSITION_CONTROL) # set control mode position
        self.ser.sendCMD(id=F1_MF_IDX,cmd=SET_CONTROL_MODE,pref=POSITION_CONTROL) # set control mode position
        self.ser.sendCMD(id=F1_ME_IDX,cmd=ENABLE_MOTOR)
        self.ser.sendCMD(id=F1_MF_IDX,cmd=ENABLE_MOTOR)

    def relax(self):
        self.ser.sendCMD(id=F1_MF_IDX,cmd=SET_POS_REF,pref=0)

    def open(self):
        #self.ser.sendCMD(id=self.idx,cmd=F_OPEN)
        self.ser.sendCMD(id=F1_MF_IDX,cmd=SET_POS_REF,pref=I_MF_OPEN_POS)
        self.ser.sendCMD(id=F1_ME_IDX,cmd=SET_POS_REF,pref=I_ME_OPEN_POS)

    def close(self):
        #self.ser.sendCMD(id=self.idx,cmd=F_CLOSE)
        self.ser.sendCMD(id=F1_MF_IDX,cmd=SET_POS_REF,pref=I_MF_CLOSED_POS)
        self.ser.sendCMD(id=F1_ME_IDX,cmd=SET_POS_REF,pref=I_ME_CLOSED_POS)

def main():
    indice = Finger(idx=0)
    indice.enable()
    indice.open()
    
    time.sleep(2)
    indice.close()
    time.sleep(2)
    indice.open()
    time.sleep(2)
    indice.close()

    time.sleep(2)
    indice.relax()

if __name__ == '__main__':
    main()
