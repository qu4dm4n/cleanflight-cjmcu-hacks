# This code works on windows and ubuntu
# Besides Python, it requires the following preparation:
# for WINDOWS:
#   1.  Download pybluez for windows from-
#       https://code.google.com/p/pybluez/downloads/detail?name=PyBluez-0.20.win32-py2.7.exe&can=2&q=
#   2.  Turn on the quad with bluetooth module attached
#   3.  Start->"add a bluetooth device"->scan and find it->choose to enter pin.
#   4.  afer binding its available on control panel "devices and printers"->"bluetooth devices"
#   5.  Right click it, properties. "Hardware tab", properties, port settings. Set it to 115200, 8 data bits, none parity, 1 stop bit, None flow control.
#
# Known issues - Python throws "windows bluetooth A socket operation was attempted to an unreachable network" upon connection.
#  solved by going to "devices and printers"->"bluetooth devices", and removing the device, and doing the pair again (steps 2-5)

# for UBUNTU:
#   1.  sudo apt-get install bluez python-bluez
#   2.  bluez-simple-agent hci# xx:xx:xx:xx:xx:xx
#       a. dash # is local bluetooth device index, find it by running "hcitool
#       dev" (its probably 0)
#       b. xx:xx:xx:xx:xx:xx is address of destination bluetooth, find it by turning on the quad and running "hcitool scan"
#       c. you will be asked about the pin code, enter it


# extra info:
#   Notice this bluetooth library is not ideal for windows since on windows it doesnt support any form of non-blocking mode (settimeout or setblocking), too bad...



import sys
import time
import struct
import binascii


import bluetooth

OUT_MSG_PREFIX = "$M<"
IN_MSG_PREFIX = "$M>"


MSP_API_VERSION = 1
MSP_SET_MOTOR = 214
MSP_ATTITUDE = 108
MSP_RAW_IMU = 102
MSP_SET_RAW_RC = 200

def packMessage(msg):
    if (dict != type(msg)):
        return None

    if ('command' not in msg.keys()) or ('data' not in msg.keys()):
        return None

    checksum = len(msg['data']) ^ msg['command']
    for singleChar in msg['data']:
        checksum ^= ord(singleChar)

    return struct.pack(str(len(OUT_MSG_PREFIX)) + "sBB" + str(len(msg['data'])) + "sB", OUT_MSG_PREFIX, len(msg['data']), msg['command'], msg['data'], checksum)


def unpackMessage(msg):
    if (str != type(msg)):
        return None

    # PREFIX + data size + checksum is the bare minimum
    if (len(msg) < len(IN_MSG_PREFIX) + 1 + 1):
        return None

    if (not msg.startswith(IN_MSG_PREFIX)):
        return None

    dataSize = ord(msg[len(IN_MSG_PREFIX)])

    # PREFIX + data size + the command this responds to + data + checksum
    if (len(msg) < len(IN_MSG_PREFIX) + 1 + 1 + dataSize + 1):
        return None

    commandRespond = ord(msg[len(IN_MSG_PREFIX) + 1])
    dataContent = msg[len(IN_MSG_PREFIX) + 1 + 1:len(IN_MSG_PREFIX) + 1 + 1 + dataSize]
    dataChecksum = ord(msg[-1])

    checksum = dataSize ^ commandRespond
    for singleChar in dataContent:
        checksum ^= ord(singleChar)

    if (dataChecksum != checksum):
        return None

    return {'dataContent': dataContent, 'commandRespond': commandRespond}


class quadComm:
    def __init__(self, address):
        self.address = address
        self.sock = None

    def open(self):
        try:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect((self.address, 1))
        except bluetooth.BluetoothError:
            self.sock = None
            return False

        return True

    def close(self):
        self.sock.close()
        self.sock = None

    def blockingReceive(self, size):
        data = ''
        while (size > len(data)):
            data += self.sock.recv(size - len(data))

        return data

    def getReply(self):
        if (None == self.sock):
            return None

        reply = self.blockingReceive(3)
        if (not reply.startswith(IN_MSG_PREFIX)):
            return None

        reply += self.blockingReceive(1)
        if (len(reply) != 4):
            return None

        dataSize = ord(reply[-1])
        # Command byte + data + checksum
        reply += self.blockingReceive(1 + dataSize + 1)

        if (len(reply) != len(IN_MSG_PREFIX) + 1 + 1 + dataSize + 1):
            return None

        return reply

    def getAPIversion(self):
        if (None == self.sock):
            return None

        msg = {}

        msg['command'] = MSP_API_VERSION
        msg['data'] = ''
        request = packMessage(msg)
        self.sock.send(request)
        reply = self.getReply()

        if (None == reply):
            return None

        answer = unpackMessage(reply)
        if (None == answer):
            return None

        if (MSP_API_VERSION != answer['commandRespond']):
            return None

        (mpv, avmj, avmn) = struct.unpack("BBB", answer['dataContent'])

        version = {'msp protocol version': mpv, 'api version major': avmj, 'api version minor': avmn}

        return version

    def setMotorsSpeed(self, motorsSpeed):
        if (None == self.sock):
            return False

        if (list != type(motorsSpeed)):
            return False

        if (8 != len(motorsSpeed)):
            return False

        msg = {}

        msg['command'] = MSP_SET_MOTOR
        msg['data'] = ''
        for singleMotorSpeed in motorsSpeed:
            if (singleMotorSpeed < 1000) or (singleMotorSpeed > 2000):
                return False
            msg['data'] += struct.pack('<H', singleMotorSpeed)

        request = packMessage(msg)

        self.sock.send(request)

        return True

    def getAttitude(self):
        if (None == self.sock):
            return None

        msg = {}

        msg['command'] = MSP_ATTITUDE
        msg['data'] = ''
        request = packMessage(msg)

        self.sock.send(request)
        reply = self.getReply()
        if (None == reply):
            return None

        answer = unpackMessage(reply)
        if (None == answer):
            return None

        if (MSP_ATTITUDE != answer['commandRespond']):
            return None

        (lrt, fbt, head) = struct.unpack("<hhH", answer['dataContent'])

        attitude = {'left-right tilt': lrt, 'forward-backward tilt': fbt, 'heading': head}

        return attitude

    def getRawSensors(self):
        if (None == self.sock):
            return None

        msg = {}

        msg['command'] = MSP_RAW_IMU
        msg['data'] = ''
        request = packMessage(msg)

        self.sock.send(request)
        reply = self.getReply()
        if (None == reply):
            return None

        answer = unpackMessage(reply)
        if (None == answer):
            return None

        if (MSP_RAW_IMU != answer['commandRespond']):
            return None

        (acc1, acc2, acc3, gyro1, gyro2, gyro3, mag1, mag2, mag3) = struct.unpack("<hhhhhhhhh", answer['dataContent'])

        rawSensors = {'acc1': acc1, 'acc2': acc2, 'acc3': acc3,
                    'gyro1': gyro1, 'gyro2': gyro2, 'gyro3': gyro3,
                      'mag1': mag1, 'mag2': mag2, 'mag3': mag3}

        return rawSensors

    def setRCcommand(self, commands):
        """
        commads is a list of 8 short integers representing desired channel values, ranging from 1000 to 2000.
        1: Roll (tilt right-left). 1000-1499 is tilt left. 1500 is no tilt. 1501-2000 is tilt right.
        2: Pitch (tilt forward-backward). 1000-1499 is backward. 1500 is no tilt. 1501-2000 is forward.
        3: Yaw (look right-left), 1000-1499 is yaw left. 1500 is no yaw. 1501-2000 is yaw right.
        4: Throttle. 1000 is low throtle, 2000 is high throttle.
        5: AUX1. Low 1000, mid 1500, high 2000.
        6: AUX2
        7: AUX3
        8: AUX4
        """
        if (None == self.sock):
            return False

        if (list != type(commands)):
            return False

        if (8 != len(commands)):
            return False

        msg = {}

        msg['command'] = MSP_SET_RAW_RC
        msg['data'] = ''
        for singleRCcommand in commands:
            if (singleRCcommand < 1000) or (singleRCcommand > 2000):
                return False
            msg['data'] += struct.pack('<H', singleRCcommand)

        request = packMessage(msg)

        self.sock.send(request)

        return True


def motorsTest(quad):
    time.sleep(1)
    qc.setMotorsSpeed([1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000])
    time.sleep(1)
    qc.setMotorsSpeed([1200, 1000, 1000, 1000, 1000, 1000, 1000, 1000])
    time.sleep(2)
    qc.setMotorsSpeed([1000, 1200, 1000, 1000, 1000, 1000, 1000, 1000])
    time.sleep(2)
    qc.setMotorsSpeed([1000, 1000, 1200, 1000, 1000, 1000, 1000, 1000])
    time.sleep(2)
    qc.setMotorsSpeed([1000, 1000, 1000, 1200, 1000, 1000, 1000, 1000])
    time.sleep(2)
    qc.setMotorsSpeed([1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000])


def msgParsingTest():
    print(unpackMessage("$M>\x06l\r\x00\xe3\xffe\x00\x1e"))
    print(unpackMessage('$M>\x03\x01\x00\x01\x08\x0b'))

    packMessage({'command': 1, 'data': ''})


def attitudeReadingsTest(quad):
    readings = 100
    while (readings > 0):
        print(quad.getAttitude())
        time.sleep(0.2)
        readings -= 1


def sensorsReadingsTest(quad):
    readings = 100
    while (readings > 0):
        print(quad.getRawSensors())
        time.sleep(0.2)
        readings -= 1


def RCcommandTest(quad):
    # Idle
    quad.setRCcommand([1500, 1500, 1500, 1000, 1000, 1000, 1000, 1000])
    time.sleep(1)
    # Arm the engines
    quad.setRCcommand([1500, 1500, 1500, 1000, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Turn on throttle
    quad.setRCcommand([1500, 1500, 1500, 1150, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Test yaw
    quad.setRCcommand([1500, 1500, 1000, 1150, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Test tilt backward
    quad.setRCcommand([1500, 1000, 1500, 1150, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Test tilt left
    quad.setRCcommand([1000, 1500, 1500, 1150, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Back to idle
    quad.setRCcommand([1500, 1500, 1500, 1000, 1500, 1000, 1000, 1000])
    time.sleep(1)

    # Disarm motors
    quad.setRCcommand([1500, 1500, 1500, 1000, 1000, 1000, 1000, 1000])
    time.sleep(1)



def test_functionality():
    MY_QUAD_BLUETOOTH_ADDRESS = '20:15:03:31:34:16'

    qc = quadComm(MY_QUAD_BLUETOOTH_ADDRESS)

    if (False == qc.open()):
        print("Failed connecting!")
        sys.exit(1)

    print("Connected!")

    time.sleep(3)

    retries = 5

    quadVersion = qc.getAPIversion()
    while ((None == quadVersion) and (retries > 0)):
        time.sleep(1)
        quadVersion = qc.getAPIversion()
        retries -= 1

    if (None == quadVersion):
        print("Failed retrieving version information")
        qc.close()
        sys.exit(1)

    print(quadVersion)

    # Uncomment one of these to check functionality.
    # WARNING!! some of them will spin the motors

    #motorsTest(qc)
    #attitudeReadingsTest(qc)
    #sensorsReadingsTest(qc)
    #RCcommandTest(qc)

    qc.close()

if ('__main__' == __name__):
    test_functionality()
