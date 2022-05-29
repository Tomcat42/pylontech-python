#!/usr/bin/python3
""" just an example to send and recveive over /dev/ttyUSB0
    on other OSes just replace e.g. by "COM3".
    This example expects you to change the DIP switches on
    the battery to 115200 Baud.
    next examples will use a baud autodetect feature.
"""
# from libPylon import Pylontech_rs485
from webencodings import decode
import sys
import os

sys.path.insert(0, '../../pylon')

from pylontech import Pylontech_rs485
from pylontech_decode import PylontechDecode
from pylontech_encode import PylontechEncode

if __name__ == '__main__':
    #device = 'COM3'
    device = '/dev/ttyUSB0'
    pylon = Pylontech_rs485(device=device, baud=115200)

    e = PylontechEncode()
    d = PylontechDecode()

    pylon.send(e.getProtocolVersion())  # get protocol version
    raws = pylon.recv()
    print(raws)
    d.decode_header(raws[0])
    print(d.decodePotocolVersion())

    for i in range(0,7):
        pylon.send(e.getManufacturerInfo(battNumber=i))
        raws = pylon.recv()
        print(raws)
        d.decode_header(raws[0])
        print(d.decodeManufacturerInfo())


    pylon.send(e.getSystemParameter())  # get system parameter, fixed point
    raws = pylon.recv()
    d.decode_header(raws[0])
    print(d.decodeSystemParameter())

    pylon.send(e.getAlarmInfo(battNumber=2))
    raws = pylon.recv()
    d.decode_header(raws[0])
    print(d.decodeAlarmInfo())

    pylon.send(e.getAlarmInfo(allPackData=True))
    raws = pylon.recv()
    d.decode_header(raws[0])
    print(d.decodeAlarmInfo())

    pylon.send(e.getChargeDischargeManagement(battNumber=0))
    raws = pylon.recv()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    pylon.send(e.getChargeDischargeManagement(battNumber=1))
    raws = pylon.recv()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    packCount=7
    for batt in range(0,packCount,1):
        pylon.send(e.getAnalogValue(battNumber=batt))  # get Analog Value
        raws = pylon.recv()
        d.decode_header(raws[0])
        print(d.decodeAnalogValue())

    for batt in range(0, packCount, 1):
        pylon.send(e.getSerialNumber(battNumber=batt))
        raws = pylon.recv()
        d.decode_header(raws[0])
        print(d.decodeSerialNumber())

