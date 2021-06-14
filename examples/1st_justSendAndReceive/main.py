#!/usr/bin/python3
""" just an example to send and recveive over /dev/ttyUSB0
    on other OSes just replace e.g. by "COM3".
    This example expects you to change the DIP switches on
    the battery to 9600 Baud.
    next examples will use a baud autodetect feature.
"""
from libPylon import Pylontech_rs485

if __name__ == '__main__':
    # device = 'COM3'
    device = '/dev/ttyUSB0'
    pylon = Pylontech_rs485(device=device)
    pylon.send(b'2002464FC0048520')  # get protocol version
    raws = pylon.recv()

    pylon.send(b'20024651C0040000')  # get manufactory info
    raws = pylon.recv()

    pylon.send(b'20024642C0040202')  # get Analog Value - get data of Battery 2
    raws = pylon.recv()

    pylon.send(b'20024642C0040201')  # get Analog Value - get data of Battery 1
    raws = pylon.recv()

    pylon.send(b'20024647C0040000')  # get system parameter, fixed point
    raws = pylon.recv()

    pylon.send(b'20024644C0040201')  # get alarm info   - get data of Battery 1
    raws = pylon.recv()
    pylon.send(b'20024644C0040202')  # get alarm info   - get data of Battery 2
    raws = pylon.recv()

    pylon.send(b'20024692C0040201')  # get charge, discharge management info - get data of Battery 1
    raws = pylon.recv()
    pylon.send(b'20024692C0040202')  # get charge, discharge management info - get data of Battery 2
    raws = pylon.recv()

    #pylon.send(b'20024693C0040201')  # get module SN number - get data of Battery 1
    #raws = pylon.recv()
    #pylon.send(b'20024693C0040202')  # get module SN number - get data of Battery 2
    #raws = pylon.recv()
    #pylon.send(b'20024693C0040204')  # get module SN number - get data of Battery 3
    #raws = pylon.recv()

    pylon.send(b'20024696C0040201')  # get software version - get data of Battery 1
    raws = pylon.recv()
    pylon.send(b'20024696C0040202')  # get software version - get data of Battery 1
    raws = pylon.recv()


