import binascii

class PylontechEncode:
    def __init__(self):
        pass

    def lenChecksum(self, length):
        cs = length & 0xf
        cs = cs + ((length >> 4) & 0xf)
        cs = cs + ((length >> 8) & 0xf)
        cs = ((~cs)&0xf) + 1
        cs = cs << 12
        return "{:04X}".format((length+cs)&0xffff)

    def genFrame(self, adr, cid2, length, info):
        command = '20'  # VER
        command = command + "{:02X}".format(adr)  # ADR
        command = command + '46'  # CID1 = Li Batt
        command = command + "{:02X}".format(cid2)  # CID2 = Get Analog Value
        command = command + self.lenChecksum(length)  # LENGTH inc. Checksum
        for l in range(0, length, 1):
            command = command + "{:02X}".format(info[l])
        return bytes(command, 'ascii')

    # BattNumber 0..15
    def analogValue(self, BattNumber):
        command = '20'  # VER
        command = command + "{:02x}".format(BattNumber+2)  # ADR
        command = command + '46'  # CID1 = Li Batt
        command = command + '42'  # CID2 = Get Analog Value
        command = command + 'C004'  # LENGTH inc. Checksum
        command = command + "{:02x}".format(BattNumber+2)
        command = command + '00'
        return bytes(command, 'ascii')

    def getProtocolVersion(self):
        return self.genFrame(2, 0x4f, 0, '')

    def getManufacturerInfo(self, battNumber=0):
        return self.genFrame(2+battNumber, 0x51, 0, '')


if __name__ == '__main__':

    print('test some return values')
    e = PylontechEncode()
    print(e.lenChecksum(4))
    print(e.lenChecksum(18))
    print(e.genFrame(2, 0x4f, 0, ''))