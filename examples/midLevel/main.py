#!/usr/bin/python3
""" just an example to send and recveive over /dev/ttyUSB0
    on other OSes just replace e.g. by "COM3".
    This example expects you to set the DIP switches on
    the battery to 115200 Baud.
"""
# from pylontech import PylontechRS485
#from webencodings import decode
#import sys
#import os
from pylontech import PylontechRS485
from pylontech import PylontechDecode
from pylontech import PylontechEncode


if __name__ == '__main__':
    #device = 'COM3'
    device = '/dev/ttyUSB0'
    pylon = PylontechRS485(device=device, baud=115200)

    e = PylontechEncode()
    d = PylontechDecode()

    pylon.send(e.getProtocolVersion())  # get protocol version
    raws = pylon.receive()
    print(raws)
    d.decode_header(raws[0])
    print(d.decodePotocolVersion())

    for i in range(0,7):
        pylon.send(e.getManufacturerInfo(battNumber=i))
        raws = pylon.receive()
        print(raws)
        d.decode_header(raws[0])
        print(d.decodeManufacturerInfo())

    pylon.send(e.getSystemParameter())  # get system parameter, fixed point
    raws = pylon.receive()
    d.decode_header(raws[0])
    print(d.decodeSystemParameter())

    pylon.send(e.getAlarmInfo(battNumber=2))
    raws = pylon.receive()
    d.decode_header(raws[0])
    print(d.decodeAlarmInfo())

    pylon.send(e.getAlarmInfo(allPackData=True))
    raws = pylon.receive()
    d.decode_header(raws[0])
    print(d.decodeAlarmInfo())

    pylon.send(e.getChargeDischargeManagement(battNumber=0))
    raws = pylon.receive()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    pylon.send(e.getChargeDischargeManagement(battNumber=1))
    raws = pylon.receive()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    packCount=7
    for batt in range(0,packCount,1):
        pylon.send(e.getAnalogValue(battNumber=batt))  # get Analog Value
        raws = pylon.receive()
        d.decode_header(raws[0])
        print(d.decodeAnalogValue())

    for batt in range(0, packCount, 1):
        pylon.send(e.getSerialNumber(battNumber=batt))
        raws = pylon.receive()
        d.decode_header(raws[0])
        print(d.decodeSerialNumber())
