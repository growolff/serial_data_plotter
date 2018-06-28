# -*- coding: utf-8 -*-

import struct

class MotorCommand(object):

    _struct = struct.Struct('<BBBBBh')

    def __init__(self):
        self.cmd = 0
        self.motor = 0
        self.dpin = 0
        self.onoff = 0
        self.ctrl = 0
        #self.asd = 0
        self.valstr = 0

    def serialize(self, buff):
        #try:
        #buff.write(MotorCommand._struct.pack(self.cmd, self.motor, self.dpin, self.onoff, self.ctrl, self.asd, self.value))
        #buff.write(MotorCommand._struct.pack(self.cmd, self.motor, self.dpin, self.onoff, self.ctrl, self.asd, self.valstr))
        buff.write(MotorCommand._struct.pack(self.cmd, self.motor, self.dpin, self.onoff, self.ctrl, self.valstr))
        #except struct.error as se:
        #    raise SerializationError('Error in serialization %s' % (self.__str__))

    def fromTuple(self, data):
        self.cmd = data.cmd
        self.motor = data.motor
        self.dpin = data.dpin
        self.onoff = data.onoff
        self.ctrl = data.ctrl
        #self.asd = data.asd
        self.valstr = data.valstr

def to_hex(data):
    return ":".join("{:02x}".format(c) for c in data)

def test():
    from io import BytesIO
    buff = BytesIO()
    CMD = MotorCommand()
    CMD.cmd = ord('C')
    CMD.motor = 1
    CMD.dpin = ord('E')
    CMD.onoff = 1
    CMD.ctrl = ord('S')
    #CMD.asd = 255
    CMD.valstr = 256
    CMD.serialize(buff)

    print(to_hex(buff.getvalue()))
    print(buff.getvalue())


if __name__ == '__main__':

    test()
