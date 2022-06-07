#!/usr/bin/env python3
from pylontech import PylontechStack
print('evaluating the stack of batteries (0..n batteries)')
x = PylontechStack("/dev/ttyUSB0", baud=115200, manualBattcountLimit=3)
print('number of batteries found: {}'.format(x.battcount))
print('received data:')
print(x.pylonData)

x.update()
