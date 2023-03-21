#!/usr/bin/env python3
import time
from pprint import pprint
from threading import Event

from pylontech import PylontechStack
print('evaluating the stack of batteries (0..n batteries)')
x = PylontechStack('/dev/ttyUSB0', baud=115200, manualBattcountLimit=7)
print('number of batteries found: {}'.format(x.battcount))
print('received data:')
print(x.pylonData)

while 1:
    try:
        x.update()
        Event.wait(1)
        pprint(x.pylonData['Calculated'])
    except Exception as err:
        print("Timeout ", err)
