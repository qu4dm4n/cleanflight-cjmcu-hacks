from hc06_setup import *
from quadComm import *
import time
from upload import *

CLEANFLIGHT_FIRMWARE_HEX_FILENAME = 'cleanflight_CJMCU_v1.8.1.hex'

def configureControlBoard(port):
    qc = usbQuadComm()

    if (False == qc.open(port)):
        print("Failed connecting!")
        return

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
        return

    print(quadVersion)

    cliCommandsFromFile(qc, "cli_commands.txt")
    qc.close()



comPort = raw_input("Please enter a valid COM port name.\r\n>> ")

while True:
    selection = raw_input("\r\n\r\nSelect a task:\r\n1. Configure the bluetooth module.\r\n2. Flash the control-board firmware.\r\n3. Configure the control board.\r\n>> ")

    if ("1" == selection):
        try:
            setup_HC06(comPort)
        except:
            pass

    elif ("2" == selection):
        try:
            flashSTM32(comPort, CLEANFLIGHT_FIRMWARE_HEX_FILENAME)
        except:
            pass

    elif ("3" == selection):
        try:
            configureControlBoard(comPort)
        except:
            pass
