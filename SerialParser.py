
class Data(object):
    def __init__(self,msg,value):
        self.msg = msg
        self.value = value

def serialParser(msg):

    charParamsSeparator = '*'
    charDataSeparator = '\t'
    charMessageSeparator = ' '

    msg = msg.rstrip()
    #print(msg)
    pid = list()

    if msg[0] == "&":
        return msg[1:]

    if msg[0] == "!":
        return int(msg[1])

    if msg[0] == "*":
        pid_params = msg.split(charParamsSeparator)
        pid.append(float(pid_params[1]))
        pid.append(float(pid_params[2]))
        pid.append(float(pid_params[3]))
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
