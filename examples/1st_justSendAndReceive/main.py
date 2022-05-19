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
    # device = 'COM3'
    device = '/dev/ttyUSB0'
    pylon = Pylontech_rs485(device=device, baud=115200)

    e = PylontechEncode()
    d = PylontechDecode()

    #pylon.send(b'2002464FC0048520')  # get protocol version
    pylon.send(e.getProtocolVersion())  # get protocol version
    raws = pylon.recv()
    print(raws)
    d.decode_header(raws[0])
    print(d.decodePotocolVersion())

    #pylon.send(b'20024651C0040000')  # get manufactory info
    for i in range(0,15):
        pylon.send(e.getManufacturerInfo(battNumber=i))
        raws = pylon.recv()
        print(raws)
        d.decode_header(raws[0])
        print(d.decodeManufacturerInfo())

    pylon.send(b'20024647C0040000')  # get system parameter, fixed point
    raws = pylon.recv()

    pylon.send(b'20024644C0040201')  # get alarm info   - get data of Battery 1
    raws = pylon.recv()
    pylon.send(b'20024644C0040202')  # get alarm info   - get data of Battery 2
    raws = pylon.recv()

    pylon.send(b'20024692C0040201')  # get charge, discharge management info - get data of Battery 1
    raws = pylon.recv()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    pylon.send(b'20024692C0040202')  # get charge, discharge management info - get data of Battery 2
    raws = pylon.recv()
    print(d.decode_header(raws[0]))
    print(d.decodeChargeDischargeManagementInfo())

    packCount=7
    for batt in range(0,packCount,1):
        pylon.send(e.analogValue(BattNumber=batt))  # get Analog Value
        raws = pylon.recv()
        d.decode_header(raws[0])
        print(d.decodeAnalogValue())


    sys.exit(0)


    # pylon.send(b'20024693C0040201')  # get module SN number - get data of Battery 1
    # raws = pylon.recv()
    # pylon.send(b'20024693C0040202')  # get module SN number - get data of Battery 2
    # raws = pylon.recv()
    # pylon.send(b'20024693C0040204')  # get module SN number - get data of Battery 3
    # raws = pylon.recv()

    # pylon.send(b'20024696C0040201')  # get software version - get data of Battery 1
    # raws = pylon.recv()
    # pylon.send(b'20024696C0040202')  # get software version - get data of Battery 1
    # raws = pylon.recv()
