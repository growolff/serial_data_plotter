# -*- coding: utf-8 -*-

import struct

class MotorCommand(object):

    _struct = struct.Struct('<BBhhhh')

    def __init__(self):
        self.id = 0
        self.cmd = 0
        self.pref = 0
        self.P = 0
        self.I = 0
        self.D = 0

    def serialize(self, buff):
        #try
        buff.write(MotorCommand._struct.pack(self.id, self.cmd, self.pref, self.P, self.I, self.D))
        #except struct.error as se:
        #    raise SerializationError('Error in serialization %s' % (self.__str__))

    def fromTuple(self, data):
        self.id = data.id
        self.cmd = data.cmd
        self.pref = data.pref
        self.P = data.P
        self.I = data.I
        self.D = data.D


def to_hex(data):
    return ":".join("{:02x}".format(c) for c in data)

def test():
    from io import BytesIO
    buff = BytesIO()
    CMD = MotorCommand()

    CMD.id = ord('A')
    CMD.cmd = 1
    CMD.pref = 0
    CMD.tref = 10

    CMD.serialize(buff)

    print(to_hex(buff.getvalue()))
    print(buff.getvalue())


if __name__ == '__main__':

    test()
