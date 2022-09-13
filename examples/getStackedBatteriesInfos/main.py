#!/usr/bin/env python3
from pylontech import PylontechStack
print('evaluating the stack of batteries (0..n batteries)')
x = PylontechStack("socket://10.10.4.13:23", baud=115200, manualBattcountLimit=3)
print('number of batteries found: {}'.format(x.battcount))
print('received data:')
print(x.pylonData)

x.update()
