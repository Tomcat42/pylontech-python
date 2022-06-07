#!/usr/bin/python3
""" just an example to send and receive over /dev/ttyUSB0
    on other OSes just replace e.g. by "COM3".
    This example expects you to set the DIP switches on
    the battery to 115200 Baud.
    next examples will use a baud autodetect feature.
"""

# PylontechRS485 handles send & receive and Prefix/suffix/checksum and timeout handling.
from pylontech import PylontechRS485


def do_some_stuff(device='/dev/ttyUSB0'):
    '''
    send valid packages to the Battery,
    :param device:
        your serial Port name/device Name, e.g. /dev/ttyS0 or COM1:
    :return:
        No return Value
    '''
    # on Windows: device = 'COM3'
    pylon = PylontechRS485(device=device, baud=115200)
    pylon.verbose(level=11)  # activate verbosity, to show packages
    pylon.send(b'2002464FC0048520')  # get protocol version
    raws = pylon.receive()

    pylon.send(b'20024651C0040000')  # get manufactory info
    raws = pylon.receive()

    pylon.send(b'20024642C0040202')  # get Analog Value - get data of Battery 2
    raws = pylon.receive()

    pylon.send(b'20024642C0040201')  # get Analog Value - get data of Battery 1
    raws = pylon.receive()

    pylon.send(b'20024647C0040000')  # get system parameter, fixed point
    raws = pylon.receive()

    pylon.send(b'20024644C0040201')  # get alarm info   - get data of Battery 1
    raws = pylon.receive()
    pylon.send(b'20024644C0040202')  # get alarm info   - get data of Battery 2
    raws = pylon.receive()

    pylon.send(b'20024692C0040201')  # get charge, discharge management info - get data of Battery 1
    raws = pylon.receive()
    pylon.send(b'20024692C0040202')  # get charge, discharge management info - get data of Battery 2
    raws = pylon.receive()

    #pylon.send(b'20024693C0040201')  # get module SN number - get data of Battery 1
    #raws = pylon.receive()
    #pylon.send(b'20024693C0040202')  # get module SN number - get data of Battery 2
    #raws = pylon.receive()
    #pylon.send(b'20024693C0040204')  # get module SN number - get data of Battery 3
    #raws = pylon.receive()

    pylon.send(b'20024696C0040201')  # get software version - get data of Battery 1
    raws = pylon.receive()
    pylon.send(b'20024696C0040202')  # get software version - get data of Battery 1
    raws = pylon.receive()

if __name__ == '__main__':
    do_some_stuff()
