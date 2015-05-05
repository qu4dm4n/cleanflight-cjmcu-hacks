from hc06 import *
import sys

DEFAULT_SERIAL_PORT_PATH = r'/dev/ttyUSB0'

if (len(sys.argv) > 1):
    DEFAULT_SERIAL_PORT_PATH = argv[1]


while True:
    print "\n\n\n\nConnect a dongle and then press ENTER"
    raw_input()

    dongle = hc06Configurator(DEFAULT_SERIAL_PORT_PATH)

    if (False == dongle.open()):
        print "Failed opening port"
        continue

    name = raw_input("Enter a unique name for your device (MAX 20 chars):")

    while len(name) > 20:
        print "Your name is too long!\n"
        name = raw_input("Enter a unique name for your device (MAX 20 chars):")

    print "Setting name to %s" % name

    if (False == dongle.setName(name)):
        print "Failed changing name"
        continue

    pin = raw_input("Enter a 4 digit PIN code for your device:")

    while len(pin) != 4 or not pin.isdigit():
        print "Invalid PIN code!\n"
        pin = raw_input("Enter a 4 digit PIN code for your device:")

    print "Setting pin to %s" % pin
    if (False == dongle.setPin(pin)):
        print "Failed changing pin"
        continue

    if (False == dongle.setCleanflightBaudrate()):
        print "Failed changing baudrate"

    dongle.close()
