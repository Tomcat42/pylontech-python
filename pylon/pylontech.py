''' Functions to support the Pylontech US2000 and similar Batteries.

    This module provides Classes to communicate over RS-485 to the Pylontech
    Battery. This code is based on the
    "PYLON low voltage Protocol RS485", Version 3.3 (2018/08/21)

    The RS-485 communication ist based on pyserial.
    As hardware, a simple usb-serial rs485 adapter can be used.
    these adapter are able to receive out of the box, sending is possible
    by enabling the transceive pin using the RTS signal.
'''

import serial
#from construct import *
import time

# message_crc = Struct('message_crc', 'crc'/Int32ul)

CHKSUM_BYTES = 4
EOI_BYTES = 1


#message_header =  'message_header'/Struct(
#    #'soi' / Int8ul,      # 1 byte hex value - single character
#    'ver' / Int16ul,     # 1 byte hex value => encoded as 2 Characters HEX
#    'adr' / Int16ul,     # 1 byte hex value => encoded as 2 Characters HEX
#    'cid1' / Int16ul,    # 1 byte hex value => encoded as 2 Characters HEX
#    'cid2' / Int16ul,    # 1 byte hex value => encoded as 2 Characters HEX
#    'length' / Int32ul,  # 2 byte hex value => encoded as 4 Characters HEX
#)

#message_format = 'message_format'/Struct(
#    #'soi' / Int8ul,      # 1 byte hex value - single character
#    'ver' / Int16ul,     # 1 byte hex value => encoded as 2 Characters HEX
#    'adr' / Int16ul,     # 1 byte hex value => encoded as 2 Characters HEX
#    'cid1' / Int16ul,    # 1 byte hex value => encoded as 2 Characters HEX
#    'cid2' / Int16ul,    # 1 byte hex value => encoded as 2 Characters HEX
#    'length' / Int32ul,  # 2 byte hex value => encoded as 4 Characters HEX
#    'cmd_info' / Int16ul,   # 1 byte hex value => encoded as 2 Characters HEX
#    'data_info' / Int16ul   # 1 byte hex value => encoded as 2 Characters HEX
#)



class Rs485Handler():
    ''' Handles the USB to RS485 adapter with TE / Transmit Enable on RTS
        preset for
        - 9600 baud,8n1
        - sending and receiving frames defined by start and end byte
     '''
    sendTime1 = 0
    sendTime2 = 0
    rcvTime1 = 0
    rcvTime2 = 0

    def __init__(self, device='/dev/ttyUSB0', baud=9600):
        #try:
            self.ser = serial.Serial(device,
                            baudrate=baud,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            rtscts=False,
                            dsrdtr=False,
                            timeout=10.0,
                            inter_byte_timeout=0.02)            # open serial port
        #except OSError:
        #    print("device not found: " + device)
        #    exit(1)

    def send(self, data):
        ''' send a Frame of binary data
        :param data:  binary data e.g. b'~2002464FC0048520FCB2\r'
        :return:      -
        '''
        print("->  " + data.decode())
        self.ser.rts = True      # set TX enable
        self.ser.write(data)
        self.ser.rts = False     # reset TX enable = enable Receive
        self.sendTime1 = time.time_ns()
        while self.ser.out_waiting > 0:
            time.sleep(0.001)
        self.sendTime2 = time.time_ns() - self.sendTime1


    def receive_frame(self, endtime, start=b'~', end=b'\r'):
        ''' receives a frame defined by a stert and end byte
        :param start: the start byte, e.g. b'~'
        :param end:   the end byte, e.g. b'\r'
        :return:      the frame as binary data,
                      e.g. b'~200246000000FDB2\r'
                      returns after the first end byte.
        '''
        char = self.ser.read(1)
        # wait for leading byte / start byte:
        while char != start:
            char = self.ser.read(1)
            if time.time() > endtime:
                return None
        self.rcvTime1 = time.time_ns() - self.sendTime1   #  just for Timeout hamdling
        # receive all until the trialing byte / end byte:
        data = self.ser.read_until(end)
        # build a complete frame:
        frame = start + data
        # just more timeout handling:
        self.rcvTime2 = time.time_ns() - self.sendTime1  # just for Timeout hamdling
        # just for debugging:
        print("\r <- " + frame.decode())
        # return the frame
        print(" times: {:04.3f}     {:6.3f} - {:6.3f} ".format(self.sendTime2 / 1000.0, self.rcvTime1 /1000.0, self.rcvTime2 /1000.0))
        return frame


class Pylontech_rs485():
    ''' pylontech rs485 protocol handler '''
    validchars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']


    def __init__(self, device='/dev/ttyUSB0', baud=9600):
        self.rs485 = Rs485Handler(device, baud)

    def recv(self, timeout=10):
        endtime = time.time() + timeout
        data = self.rs485.receive_frame(endtime=endtime, start=b'~', end=b'\r')
        # check len
        if data is None:
            return None
        if len(data) < 16:
            # smaller then minimal size
            return None
        start = data.index(b'~')
        if start > 0:
            data = data[start:-1]
        # check prefix and suffix
        index = 0
        while (data[index] != 0x7E) and (data[index] not in self.validchars):
            index += 1
            if (data[index] == 0x7E) and (data[index] in self.validchars):
                data = data[index:len(data)]
                break
        if data[0] != 0x7E:  # '~'
            # pefix missing
            return None
        if data[-1] != 0xd:  # '\r'
            # suffix missing
            return None
        data = data[1:-1]   # packet stripped, - without prefix, suffix
        packages = data.split(b'\r~')
        data2 = []
        for package in reversed(packages):
            chksum = self.get_chk_sum(package, len(package))
            chksum_from_pkg = int(package[-4:].decode(), base=16)
            if chksum == chksum_from_pkg:
                #data2.append(package[0:-4])
                data2.append(package)
            else:
                print("crc error soll<->ist   {:04x} --- {:04x}".format(chksum, chksum_from_pkg))
                print(package)
        return data2

    def get_chk_sum(self, data, size):
        sum = 0
        for byte in data[0:size - CHKSUM_BYTES]:
            sum += byte
        sum = ~sum
        sum &= 0xFFFF
        sum += 1
        return sum

    def send(self, data):   # data -> b'2002464FC0048520' for b'~2002464FC0048520....\r' to be sent
        # - checksum and prefix/suffix will be added.
        chksum = self.get_chk_sum(data, len(data)+CHKSUM_BYTES)
        package = ("~" + data.decode() + "{:04X}".format(chksum) + "\r").encode()
        self.rs485.send(package)

    def send1(self):
        #package = b'~21024651C0040000FCC0\r'
        package = b'~2002464FC0048520....\r'
        #package = b'~200246040000FDAE\r'
        chksum = self.get_chk_sum(package[1:-1], len(package)-2)
        data = package[0:-5].decode() + "{:04X}".format(chksum) + "\r"
        package = data.encode()
        self.rs485.send(package)

    pass
