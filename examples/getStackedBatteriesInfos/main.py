#!/bin/env python
from pylontech import PylontechStack
x = PylontechStack("/dev/ttyUSB0",baud=115200,manualBattcountLimit=2)
x.battcount
x.pylonData
x.update()
