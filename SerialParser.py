
import struct

class Data(object):
    def __init__(self,msg,value):
        self.msg = msg
        self.value = value

def serialParser(msg,fmt):

    #print(msg)
    rxCom = struct.unpack(fmt, msg)
    #com = rxCom[1]
    #msg1 = rxCom[2]
    #msg2 = rxCom[3]
    #msg3 = rxCom[4]
    #print(com)
    #msg = msg.rstrip()
    #print(msg)
    command = list()

    for i in range(1,5):
        command.append(rxCom[i])
        #print(rxCom[i])

    #print(command)
    return(command)

    '''
    if com == 5: # pid data
        command.append(com)
        command.append(msg1)
        command.append(msg2)
        command.append(msg3)
        #print(command)
        return command

    if com == 1:    # motor data
        command.append(com)
        command.append(msg1)
        command.append(msg2)
        command.append(msg3)
        #print(command)
        return command
    '''
    if msg[0] == "&":
        return msg[1:]

    if msg[0] == "!":
        return int(msg[1])

    if msg[0] == "*":
        pid_params = msg.split(charParamsSeparator)
        pid.append(float(pid_params[1])/4096)
        pid.append(float(pid_params[2])/4096)
        pid.append(float(pid_params[3])/4096)
        #print(pid)
        return pid

    # separate message in parts
    variables = msg.split(charDataSeparator)
    dataArray = list()

    # iterate over all the data and fill a dictionary with ids and measurements
    for v in variables:
        vAux = v.split(charMessageSeparator)
        dataArray.append(Data(vAux[0],vAux[1]))

    grahps = dict([ (d.msg, d.value) for d in dataArray ])

    return grahps
