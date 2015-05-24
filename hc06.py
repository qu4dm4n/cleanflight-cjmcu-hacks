import serial
import time

HC06_PARITY = serial.PARITY_NONE
HC06_STOPBITS = serial.STOPBITS_ONE
HC06_BYTESIZE = serial.EIGHTBITS

# Most chances these are correct
HC06_BAUDRATES_PRIORITY = [9600, 115200]

HC06_BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 1382400]

CLEANFLIGHT_BAUDRATE = 115200

class hc06Configurator:
    def __init__(self, port):
        self.port = port
        self.baud = self.checkBuadrate(HC06_BAUDRATES_PRIORITY)

        if (None == self.baud):
            self.baud = self.checkBuadrate(HC06_BAUDRATES)
            if (None == self.baud):
                print "HC-06 was not found on any of the baudrates"
                self.serialHandle = None
                return

        self.serialHandle = serial.Serial(port=self.port, baudrate=self.baud, parity=HC06_PARITY, stopbits=HC06_STOPBITS, bytesize=HC06_BYTESIZE, timeout=2)

    def open(self):
        if (None == self.serialHandle):
            return False
        try:
            self.serialHandle.open()
        except:
            pass

    def close(self):
        if (None == self.serialHandle):
            return False
        self.serialHandle.close()

    def setName(self, name):
        if (None == self.serialHandle):
            return False

        if (20 < len(name)):
            return False

        self.serialHandle.write('AT+NAME%s' % (name))

        if ('OKsetname' != self.serialHandle.read(len('OKsetname'))):
            return False

        return True

    def setPin(self, pin):
        if (None == self.serialHandle):
            return False

        if ((4 != len(pin)) or not (pin.isdigit())):
            return False

        self.serialHandle.write('AT+PIN%s' % (pin))

        if ('OKsetPIN' != self.serialHandle.read(len('OKsetPIN'))):
            return False

        return True

    def setCleanflightBaudrate(self):
        if (None == self.serialHandle):
            return False

        if (self.baud == CLEANFLIGHT_BAUDRATE):
            return True

        baudrateIndex = HC06_BAUDRATES.index(CLEANFLIGHT_BAUDRATE) + 1
        self.serialHandle.write('AT+BAUD%01X' % (baudrateIndex))

        expectedAnswer = 'OK%d' % CLEANFLIGHT_BAUDRATE
        if (expectedAnswer != self.serialHandle.read(len(expectedAnswer))):
            return False

        self.serialHandle.close()
        time.sleep(2)
        self.baud = CLEANFLIGHT_BAUDRATE
        self.serialHandle = serial.Serial(port=self.port, baudrate=self.baud, parity=HC06_PARITY, stopbits=HC06_STOPBITS, bytesize=HC06_BYTESIZE, timeout=2)
        self.open()


        self.serialHandle.write('AT')
        if ('OK' == self.serialHandle.read(2)):
            return True

        return False

    def checkBuadrate(self, optionalBaudrates):
        for singleRate in optionalBaudrates:
            print "checking rate " + str(singleRate)
            serialHandle = serial.Serial(port=self.port, baudrate=singleRate, parity=HC06_PARITY, stopbits=HC06_STOPBITS, bytesize=HC06_BYTESIZE, timeout=2)

            try:
                serialHandle.open()
            except:
                pass

            if (not serialHandle.isOpen()):
                print "Failed isOpen"
                serialHandle.close()
                continue

            serialHandle.write('AT')
            if ('OK' == serialHandle.read(2)):
                serialHandle.close()
                return singleRate

            serialHandle.close()
        return None
