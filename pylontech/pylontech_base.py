""" Functions to support the Pylontech US2000 and similar Batteries.

    This module provides Classes to communicate over RS-485 to the Pylontech
    Battery. This code is based on the
    "PYLON low voltage Protocol RS485", Version 3.3 (2018/08/21)

    The RS-485 communication ist based on pyserial.
    As hardware, a simple usb-serial rs485 adapter can be used.
    these adapter are able to receive out of the box, sending is possible
    by enabling the transceive pin using the RTS signal.
"""

import serial
import time


CHKSUM_BYTES = 4
EOI_BYTES = 1


class Rs485Handler:
    """ Handles the USB to RS485 adapter with TE / Transmit Enable on RTS
        provides sending and receiving frames defined by start byte and end byte
        preset for
        - 9600 baud,8n1
        - /dev/ttyUSB0 als serial device
     """
    sendTime1 = 0
    sendTime2 = 0
    rcvTime1 = 0
    rcvTime2 = 0
    verbose = False

    def connect(self):
        # try:
        # open serial port:
        if '://' in self.device:
            self.ser = serial.serial_for_url(url=self.device,
                                             baudrate=self.baud,
                                             bytesize=serial.EIGHTBITS,
                                             parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE,
                                             rtscts=False,
                                             dsrdtr=False,
                                             timeout=3.0,
                                             inter_byte_timeout=0.1
                                             )
        else:
            self.ser = serial.Serial(self.device,
                                     baudrate=self.baud,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     rtscts=False,
                                     dsrdtr=False,
                                     timeout=10.0,
                                     inter_byte_timeout=0.02)

        # except OSError:
        #    print("device not found: " + device)
        #    exit(1)


    def __init__(self, device='/dev/ttyUSB0', baud=9600):
        self.device=device
        self.baud=baud
        self.connect()
        self.clear_rx_buffer()

    def verbose_print(self, data):
        if self.verbose > 0:
            print(data)

    def send(self, data):
        """ send a Frame of binary data
        :param data:  binary data e.g. b'~2002464FC0048520FCB2\r'
        :return:      -
        """
        self.verbose_print("->  " + data.decode())
        self.ser.rts = True  # set TX enable
        self.ser.write(data)
        self.ser.rts = False  # reset TX enable = enable Receive
        self.sendTime1 = time.time_ns()
        if hasattr(self.ser, 'out_waiting'):
            while self.ser.out_waiting > 0:
                time.sleep(0.001)
        self.sendTime2 = time.time_ns() - self.sendTime1

    def receive_frame(self, end_time, start=b'~', end=b'\r'):
        """ receives a frame defined by a start byte/prefix and end byte/suffix
        :param end_time:
            we expect receiving the last character before this timestamp
        :param start:
            the start byte, e.g. b'~'
        :param end:
            the end byte, e.g. b'\r'
        :return:
            the frame as binary data,
            e.g. b'~200246000000FDB2\r'
            returns after the first end byte.
        """
        char = self.ser.read(1)
        # wait for leading byte / start byte; empty the buffer before the start byte:
        while char != start:
            char = self.ser.read(1)
            if time.time() > end_time:
                raise Exception('Timeout waiting for an answer.')
                return None
        self.rcvTime1 = time.time_ns() - self.sendTime1  # just for Timeout handling
        # receive all until the trialing byte / end byte:
        # and build a complete frame as we throw the start byte...
        frame = start + self.ser.read_until(end)  # this uses the inter_byte_timeout on failure.
        # just more timeout handling:
        self.rcvTime2 = time.time_ns() - self.sendTime1  # just for Timeout handling
        # just for debugging:
        self.verbose_print("\r <- " + frame.decode())
        self.verbose_print(" times: {:04.3f}     {:6.3f} - {:6.3f} ".format(
            self.sendTime2 / 1000.0, self.rcvTime1 / 1000.0, self.rcvTime2 / 1000.0))
        # return the frame
        return frame

    def clear_rx_buffer(self):
        """ clear pending characters from serial buffer. especially important for network adapters"""
        char = '1'
        restore_timeout = self.ser.timeout
        self.ser.timeout = 1
        while (char is not None) and (len(char) > 0):
            char = self.ser.read(1)
        self.ser.timeout = restore_timeout

    def reconnect(self):
        """ force reconnect to serial port"""
        self.ser.close();
        self.connect()
        self.clear_rx_buffer()

    def close(self):
        """ force close serial connection"""
        self.ser.close()


class PylontechRS485:
    """ pylontech rs485 protocol handler
        can send and receive using a RS-485 adapter
        - checks the packet checksum for received packets.
        - adapts the packet checksum and adds prefix and suffix for packets to be sent.
    """
    valid_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    verbose = 0

    def __init__(self, device='/dev/ttyUSB0', baud=9600):
        """ init function of the pylontech rs485 protocol handler
        :param device:
                    serial device, depends on the Operating system
                    e.g. /dev/ttyUSB0, /dev/ttyS0
        :param baud:
                    valid baud rate, identical to the setting at the Battery,
                    e.g. 9600 or 115200
        """
        self.rs485 = Rs485Handler(device, baud)

    def reconnect(self):
        """ force reconnect to serial port"""
        self.rs485.reconnect()

    def close(self):
        """ force close serial connection"""
        self.rs485.close()


    def verbose(self, level=0):
        self.verbose = level
        if level >10:
            self.rs485.verbose = level - 10
        else:
            self.rs485.verbose = 0

    def receive(self, timeout=1):
        """
        try to receive a pylontech type packet from the RS-485 serial port.
        checks the packet checksum and returns the packet if the checksum is correct.
        :param timeout:
            timespan until packet has to be received
        :return:
            returns the frame or an empty list
        """
        start_byte = b'~'
        end_byte = b'\r'
        end_time = time.time() + timeout
        data = self.rs485.receive_frame(end_time=end_time, start=start_byte, end=end_byte)
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
        while (data[index] != 0x7E) and (data[index] not in self.valid_chars):
            index += 1
            if (data[index] == 0x7E) and (data[index] in self.valid_chars):
                data = data[index:len(data)]
                break
        if data[0] != start_byte[0]:  # default: start = 0x7e = '~'
            # pefix missing
            raise ValueError("no Prefix '{}' received:\nreceived:\n{}".format(start_byte, data[0]))
            return None
        if data[-1] != end_byte[0]:   # default: start = 0xd = '\r'
            # suffix missing
            raise ValueError("no suffix '{}' received:\nreceived:\n{}".format(end_byte, data[-1]))
            return None
        data = data[1:-1]  # packet stripped, - without prefix, suffix
        packages = data.split(b'\r~')
        data2 = []
        for package in reversed(packages):
            chksum = self.get_chk_sum(package, len(package))
            chksum_from_pkg = int(package[-4:].decode(), base=16)
            if chksum == chksum_from_pkg:
                data2.append(package)
            else:
                raise ValueError("crc error;  Soll<->ist: {:04x} --- {:04x}\nPacket:\n{}".format(chksum, chksum_from_pkg, package))
        return data2

    @staticmethod
    def get_chk_sum(data, size):
        sum = 0
        for byte in data[0:size - CHKSUM_BYTES]:
            sum += byte
        sum = ~sum
        sum &= 0xFFFF
        sum += 1
        return sum

    def send(self, data):
        """
        sends a pylontech type packet to the RS-485 serial port.
        :param data: packet as binary string
                     - checksum will be calculated and written,
                     - prefix/suffix will be added.
                     e.g. given b'2002464FC0048520' will be sent as b'~2002464FC0048520....\r'
        :return:     -
        """
        chksum = self.get_chk_sum(data, len(data) + CHKSUM_BYTES)
        package = ("~" + data.decode() + "{:04X}".format(chksum) + "\r").encode()
        self.rs485.send(package)

    def clear_rx_buffer(self):
        """ clear pending characters from serial buffer. especially important for network adapters"""
        self.rs485.clear_rx_buffer()

    pass
