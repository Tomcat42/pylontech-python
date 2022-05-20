from _codecs import decode

from pkg_resources import to_filename

from pylontech import Pylontech_rs485
from pylontech_decode import PylontechDecode
from pylontech_encode import PylontechEncode


class PylontechStack:
    def __init__(self, device, baud=9600):
        self.pylon = Pylontech_rs485(device=device, baud=baud)
        self.encode = PylontechEncode()
        self.decode = PylontechDecode()

        self.pylonData = {}

        serialList = []
        for batt in range(0, 15, 1):
            self.pylon.send(self.encode.getSerialNumber(battNumber=batt))
            raws = self.pylon.recv()
            if raws is None:
                break
            self.decode.decode_header(raws[0])
            decoded = self.decode.decodeSerialNumber()
            serialList.append(decoded['ModuleSerialNumber'])
        self.pylonData['SerialNumbers'] = serialList
        self.battcount = len(serialList)

        self.pylonData['Calculated'] = {}

    def update(self):
        analoglList = []
        totalCapacity = 0
        remainCapacity = 0
        for batt in range(0, self.battcount-1):
            self.pylon.send(self.encode.getAnalogValue(battNumber=batt))
            raws = self.pylon.recv()
            self.decode.decode_header(raws[0])
            decoded = self.decode.decodeAnalogValue()
            analoglList.append(decoded)
            remainCapacity = remainCapacity + decoded['RemainCapacity']
            totalCapacity = totalCapacity + decoded['ModuleTotalCapacity']
        self.pylonData['analoglList'] = analoglList

        self.pylonData['Calculated']['TotalCapacity'] = totalCapacity
        self.pylonData['Calculated']['RemainCapacity'] = remainCapacity
        self.pylonData['Calculated']['RemainPercent'] = round((remainCapacity / totalCapacity) * 100,0)

        return self.pylonData

if __name__ == '__main__':
    # device = 'COM3'
    dev = '/dev/ttyUSB0'
    pylon = PylontechStack(device=dev, baud=115200)

    print(pylon.update())
