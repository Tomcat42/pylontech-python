import binascii


class PylontechEncode:
    def __init__(self):
        self.protocol_version = '20'
        pass

    def lenChecksum(self, length):
        cs = length & 0xf
        cs = cs + ((length >> 4) & 0xf)
        cs = cs + ((length >> 8) & 0xf)
        cs = ((~cs) & 0xf) + 1
        cs = cs << 12
        return "{:04X}".format((length + cs) & 0xffff)

    def genFrame(self, adr, cid2, length, info):
        command = self.protocol_version
        command = command + "{:02X}".format(adr)  # ADR
        command = command + '46'  # CID1 = Li Batt
        command = command + "{:02X}".format(cid2)  # CID2 = Get Analog Value
        command = command + self.lenChecksum(length)  # LENGTH inc. Checksum
        for l in range(0, length, 1):
            command = command + info[l]
        return bytes(command, 'ascii')

    # BattNumber 0..15
    def analogValue(self, battNumber=0, allPackData=False):
        # First Battery is input val, info 1 and adr 2
        if allPackData:
            return self.genFrame(2, 0x42, 4, '02ff')
        else:
            info = str("{:02x}".format(battNumber + 2))
            info = info + str("{:02x}".format(battNumber + 1))
            return self.genFrame(2 + battNumber, 0x42, 4, info)

    def getProtocolVersion(self):
        return self.genFrame(2, 0x4f, 0, '')

    def getManufacturerInfo(self, battNumber=0):
        # answers on each Address but always with the Informarion of the first Battery
        # example Stack mixed of 2 US5000 and 5 US3000 replies on addr. 2..8 with "US5000"
        return self.genFrame(2 + battNumber, 0x51, 0, '')

    def getAlarmInfo(self, battNumber=0, allPackData=False):
        # First Battery is input val, info 1 and adr 2
        if allPackData:
            return self.genFrame(2, 0x44, 4, '02ff')
        else:
            info = str("{:02x}".format(battNumber + 2))
            info = info + str("{:02x}".format(battNumber + 1))
            return self.genFrame(2 + battNumber, 0x44, 4, info)

    def getSystemParameter(self):
        return self.genFrame(2, 0x47, 0, '')

    def getChargeDischargeManagement(self, battNumber=0):
        info = str("{:02x}".format(battNumber + 2))
        info = info + str("{:02x}".format(battNumber + 1))
        return self.genFrame(2+battNumber, 0x92, 4, info)

    def getSerialNumber(self, battNumber=0):
        info = str("{:02x}".format(battNumber + 2))
        info = info + str("{:02x}".format(battNumber + 1))
        return self.genFrame(2+battNumber, 0x93, 4, info)


if __name__ == '__main__':
    print('test some return values')
    e = PylontechEncode()
    print(e.lenChecksum(4))
    print(e.lenChecksum(18))
    print(e.genFrame(2, 0x4f, 0, ''))
