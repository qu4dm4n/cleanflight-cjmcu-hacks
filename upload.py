#!/usr/bin/env python
# You'll need to "pip install intelhex pyserial"
# and to get stm32loader from here: https://github.com/jsnyder/stm32loader/blob/master/stm32loader.py
# You might have to change the port in the conf variable. It probably depends on the machine and the way pyserial works on it
import sys
from intelhex import IntelHex
import stm32loader

def flashSTM32(port, hexFileName):
    ih=IntelHex()
    ih.loadhex(hexFileName)
    data = ih.tobinstr()
    data = map(lambda c: ord(c), data)
    print "Data len is %d" % len(data)
    conf = {
        'port': port,
        'baud': 115200,
        'address': 0x08000000,
        'erase': 1,
        'write': 0,
        'verify': 0,
        'read': 0,
        'go_addr':-1,
    }
    cmd = stm32loader.CommandInterface()
    cmd.open(conf['port'], conf['baud'])
    try:
        cmd.initChip()
        bootversion = cmd.cmdGet()
        print "Bootloader version %X" % bootversion

        id = cmd.cmdGetID()
        print "Chip id: 0x%x (%s)" % (id, stm32loader.chip_ids.get(id, "Unknown"))

        print "Erasing memory"
        cmd.cmdEraseMemory()

        print "Memory erased. Performing write.."
        cmd.writeMemory(conf['address'], data)

        print "Write completed. Performing verification..."
        verify = cmd.readMemory(conf['address'], len(data))

        if (data == verify):
            print "Verified"
        else:
            print "Verification failed!"

        print "Done"
    finally:
        cmd.releaseChip()

if ("__main__" == __name__):
    flashSTM32(sys.argv[1])
