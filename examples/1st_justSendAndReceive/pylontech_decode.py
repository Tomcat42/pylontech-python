
class PylontechDecode:
    def __init__(self):
        self.data={}
        pass


    def decode_header(self, rawdata):
        print(rawdata)
        header = {}
        header['VER'] = int(rawdata[0:2], 16)
        header['ADR'] = int(rawdata[2:4], 16)
        header['ID'] = int(rawdata[4:6], 16)
        header['RTN'] = int(rawdata[6:8], 16)
        header['LENGTH'] = int(rawdata[8:12], 16)&0x0fff
        header['PAYLOAD'] = rawdata[12:12 + header['LENGTH']]
        self.data=header
        return header

    def decodeChargeDischargeManagementInfo(self):
        if(self.data['ID'] == 0x46):
            payload=self.data['PAYLOAD']
            self.data['CommandValue'] = int(payload[0:2], 16)
            self.data['ChargeVoltage'] = int(payload[2:6], 16)/1000.0
            self.data['DischargeVoltage'] = int(payload[6:10], 16)/1000.0
            self.data['ChargeCurrent'] = int(payload[10:14], 16)/1000.0
            self.data['DischargeCurrent'] = int(payload[14:18], 16)/1000.0
            self.data['StatusChargeEnable'] = bool(int(payload[18:20], 16)&0x80)
            self.data['StatusDischargeEnable'] = bool(int(payload[18:20], 16)&0x40)
            self.data['StatusChargeImmediately1'] = bool(int(payload[18:20], 16)&0x20)
            self.data['StatusChargeImmediately2'] = bool(int(payload[18:20], 16)&0x10)
            self.data['StatusFullChargeRequired'] = bool(int(payload[18:20], 16)&0x08)
        else:
            print('wrong decoder selected')
        return self.data

    def decodeAnalogValue(self):
        if(self.data['ID'] == 0x46):
            payload=self.data['PAYLOAD']
            i = 2
            self.data['CommandValue'] = int(payload[i:i+2], 16)
            i=i+2
            self.data['CellCount'] = int(payload[i:i+2], 16)
            i = i + 2
            cellVoltages=[]
            for c in range(0, self.data['CellCount']):
                cellVoltages.append( int(payload[i:i+4], 16)/1000.0)
                i = i + 4
            self.data['CellVoltages'] = cellVoltages
            self.data['TemperatureCount'] = int(payload[i:i+2], 16)
            i = i + 2
            temperatures=[]
            for c in range(0, self.data['TemperatureCount']):
                temperatures.append( round((int(payload[i:i+4], 16)/10.0)-273.1,2))
                i = i + 4
            self.data['Temperatures'] = temperatures
            self.data['Current'] = int(payload[i:i+4], 16)/100.0 # TODO Vorzeichenzahl richtig umwandeln !!!
            i = i + 4
            self.data['Voltage'] = int(payload[i:i+4], 16)/1000.0
            i = i + 4
            self.data['RemainCapacity'] = int(payload[i:i+4], 16)/1000.0
            i = i + 4
            if(int(payload[i:i+2], 16) == 4):
                self.data['CapDetect'] = '>65Ah'
            else:
                self.data['CapDetect'] = '<=65Ah'
            i = i + 2
            self.data['ModuleTotalCapacity'] = int(payload[i:i+4], 16)/1000.0
            i = i + 4
            self.data['CycleNumber'] = int(payload[i:i+4], 16)
            i = i + 4
            if(self.data['CapDetect'] == '>65Ah'):
                self.data['RemainCapacity'] = int(payload[i:i + 6], 16) / 1000.0
                i = i + 6
                self.data['ModuleTotalCapacity'] = int(payload[i:i + 6], 16) / 1000.0
                i = i + 6



        else:
            print('wrong decoder selected')
        return self.data


if __name__ == '__main__':
    pass