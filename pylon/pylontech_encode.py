import binascii

class PylontechEncode:
    def __init__(self):
        pass


    # BarrNumber 0..15
    def analogValue(self, BattNumber):
        command = '20'  # VER
        command = command + "{:02x}".format(BattNumber+2)  # ADR
        command = command + '46'  # CID1 = Li Batt
        command = command + '42'  # CID2 = Get Analog Value
        command = command + 'C004'  # LENGTH inc. Checksum
        command = command + "{:02x}".format(BattNumber+2)
        command = command + '00'
        return bytes(command, 'ascii')

if __name__ == '__main__':
    pass