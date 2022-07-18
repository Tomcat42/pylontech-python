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

    print('- get Protocol Version:')
    pylon.send(e.getProtocolVersion())  # get protocol version
    try:
        raws = pylon.receive(0.1)
        print(raws)
        d.decode_header(raws[0])
        print(d.decodePotocolVersion())
    except Exception as ex:
        print("     " + str(ex))

    packCount = 8
    print('- get ManufacturerInfo:')
    for batt in range(0, packCount, 1):
        print('  - try battery #' + str(batt))
        pylon.send(e.getManufacturerInfo(battNumber=batt))
        try:
            raws = pylon.receive(0.1)
            print(raws)
            d.decode_header(raws[0])
            print(d.decodeManufacturerInfo())
        except Exception as ex:
            print("     " + str(ex))

    print('- get System Parameter:')
    pylon.send(e.getSystemParameter())  # get system parameter, fixed point
    try:
        raws = pylon.receive(0.1)
        d.decode_header(raws[0])
        print(d.decodeSystemParameter())
    except Exception as ex:
        print("     " + str(ex))

    print('- get alarm info of Battery #2:')
    pylon.send(e.getAlarmInfo(battNumber=2))
    try:
        raws = pylon.receive(0.1)
        d.decode_header(raws[0])
        print(d.decodeAlarmInfo())
    except Exception as ex:
        print("     " + str(ex))

    print('- get alarm info of Battery:')
    pylon.send(e.getAlarmInfo(allPackData=True))
    try:
        raws = pylon.receive(0.1)
        d.decode_header(raws[0])
        print(d.decodeAlarmInfo())
    except Exception as ex:
        print("     " + str(ex))

    print('- get Charge/Discharge Management values of Battery #0:')
    pylon.send(e.getChargeDischargeManagement(battNumber=0))
    try:
        raws = pylon.receive(0.1)
        print(d.decode_header(raws[0]))
        print(d.decodeChargeDischargeManagementInfo())
    except Exception as ex:
        print("     " + str(ex))

    print('- get Charge/Discharge Management values of Battery #1:')
    pylon.send(e.getChargeDischargeManagement(battNumber=1))
    try:
        raws = pylon.receive(0.1)
        print(d.decode_header(raws[0]))
        print(d.decodeChargeDischargeManagementInfo())
    except Exception as ex:
        print("     " + str(ex))

    packCount = 8
    print('- get analogue values:')
    for batt in range(0, packCount, 1):
        print('  - try battery #' + str(batt))
        pylon.send(e.getAnalogValue(battNumber=batt))  # get Analog Value
        try:
            raws = pylon.receive(0.1)
            d.decode_header(raws[0])
            print(d.decodeAnalogValue())
        except Exception as ex:
            print("     " + str(ex))
    print('- get serial numbers:')
    for batt in range(0, packCount, 1):
        print('  - try battery #' + str(batt))
        pylon.send(e.getSerialNumber(battNumber=batt))
        try:
            raws = pylon.receive(0.1)
            d.decode_header(raws[0])
            print(d.decodeSerialNumber())
        except Exception as ex:
            print("     " + str(ex))
