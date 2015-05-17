from hc06 import *
import sys


def setup_HC06(port):
    print "\n\n\n\nConnect a dongle and then press ENTER"
    raw_input()

    dongle = hc06Configurator(port)

    if (False == dongle.open()):
        print "Failed opening port"
        return

    name = raw_input("Enter a unique name for your device (MAX 20 chars, MIN 5 chars):")

    while ((len(name) > 20) or (len(name) < 5)):
        print "Enter a name within the length limits\n"
        name = raw_input("Enter a unique name for your device (MAX 20 chars, MIN 5 chars):")

    print "Setting name to %s" % name

    if (False == dongle.setName(name)):
        print "Failed changing name"
        return

    pin = raw_input("Enter a 4 digit PIN code for your device:")

    while len(pin) != 4 or not pin.isdigit():
        print "Invalid PIN code!\n"
        pin = raw_input("Enter a 4 digit PIN code for your device:")

    print "Setting pin to %s" % pin
    if (False == dongle.setPin(pin)):
        print "Failed changing pin"
        return

    if (False == dongle.setCleanflightBaudrate()):
        print "Failed changing baudrate"

    dongle.close()
    
if ("__main__" == __name__):
    DEFAULT_SERIAL_PORT_PATH = r'/dev/ttyUSB0'
    
    if (len(sys.argv) > 1):
        DEFAULT_SERIAL_PORT_PATH = argv[1]
    
    setup_HC06(DEFAULT_SERIAL_PORT_PATH)