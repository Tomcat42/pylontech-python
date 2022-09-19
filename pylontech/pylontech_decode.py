class PylontechDecode:
    def __init__(self):
        self.data = {}
        pass

    def twosComplement_hex(self, hexstr):
        bits = 16  # Number of bits in a hexadecimal number format
        val = int(hexstr, 16)
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val

    def cellVoltage(self, hexstr):  # signed int
        return self.twosComplement_hex(hexstr) / 1000.0

    def alarm(self, hexstr):  # signed int
        temp = self.twosComplement_hex(hexstr)
        if temp == 0:
            return 'Ok'
        if temp == 1:
            return 'BelowLimit'
        if temp == 2:
            return 'AboveLimit'
        return 'OtherError'

    def moduleVoltage(self, hexstr):  # unsigned int
        return int(hexstr, 16) / 1000.0

    def moduleCurrent(self, hexstr):  # signed int (charge +)
        return self.twosComplement_hex(hexstr) / 10.0

    def capacity(self, hexstr):  # unsigned int
        return int(hexstr, 16) / 1000.0

    def systemParameter(self, hexstr):  # signed int
        return self.twosComplement_hex(hexstr)

    def temperature(self, hexstr):  # signed int
        temp = self.twosComplement_hex(hexstr)
        return (temp - 2731) / 10.0

    def decode_header(self, rawdata):
        header = {}
        header['VER'] = int(rawdata[0:2], 16)
        header['ADR'] = int(rawdata[2:4], 16)
        header['ID'] = int(rawdata[4:6], 16)
        header['RTN'] = int(rawdata[6:8], 16)
        header['LENGTH'] = int(rawdata[8:12], 16) & 0x0fff
        header['PAYLOAD'] = rawdata[12:12 + header['LENGTH']]
        #print('Len: ', header['LENGTH'] ,  "RTN: ", header['RTN'] )
        self.data = header
        return header

    def decodePotocolVersion(self):
        if self.data['ID'] == 0x46:
            pass  # no payload, Version info is in VER field of header
        else:
            print('wrong decoder selected')
        return self.data

    def decodeManufacturerInfo(self):
        if self.data['ID'] == 0x46:
            payload = self.data['PAYLOAD']
            print(payload[0:20].decode("ASCII"))
            self.data['BatteryName'] = bytes.fromhex(payload[0:20].decode("ASCII")).decode("ASCII").rstrip('\x00')
            self.data['SoftwareVersion'] = int(payload[20:24], 16)
            self.data['ManufacturerName'] = bytes.fromhex(payload[24:64].decode("ASCII")).decode("ASCII").rstrip('\x00')
        else:
            print('wrong decoder selected')
        return self.data

    def decodeChargeDischargeManagementInfo(self):
        payload = self.data['PAYLOAD']
        if (self.data['ID'] == 0x46) and (len(payload) == 20):
            payload = self.data['PAYLOAD']
            self.data['CommandValue'] = int(payload[0:2], 16)
            self.data['ChargeVoltage'] = self.moduleVoltage(payload[2:6])
            self.data['DischargeVoltage'] = self.moduleVoltage(payload[6:10])
            self.data['ChargeCurrent'] = self.moduleCurrent(payload[10:14])
            self.data['DischargeCurrent'] = self.moduleCurrent(payload[14:18])
            self.data['StatusChargeEnable'] = bool(int(payload[18:20], 16) & 0x80)
            self.data['StatusDischargeEnable'] = bool(int(payload[18:20], 16) & 0x40)
            self.data['StatusChargeImmediately1'] = bool(int(payload[18:20], 16) & 0x20)
            self.data['StatusChargeImmediately2'] = bool(int(payload[18:20], 16) & 0x10)
            self.data['StatusFullChargeRequired'] = bool(int(payload[18:20], 16) & 0x08)
        else:
            self.data['CommandValue'] = None
            self.data['ChargeVoltage'] = None
            self.data['DischargeVoltage'] = None
            self.data['ChargeCurrent'] = None
            self.data['DischargeCurrent'] = None
            self.data['StatusChargeEnable'] = None
            self.data['StatusDischargeEnable'] = None
            self.data['StatusChargeImmediately1'] = None
            self.data['StatusChargeImmediately2'] = None
            self.data['StatusFullChargeRequired'] = None
            raise Exception('format error')
        return self.data

    def decodeAlarmInfo(self):
        if self.data['ID'] == 0x46:
            # No size check - variable size possible
            payload = self.data['PAYLOAD']
            i = 0
            self.data['InfoFlag'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['CommandValue'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['CellCount'] = int(payload[i:i + 2], 16)
            i = i + 2
            cellAlarm = []
            for c in range(0, self.data['CellCount']):
                cellAlarm.append(self.alarm(payload[i:i + 2]))
                i = i + 2
            self.data['CellAlarm'] = cellAlarm
            self.data['TemperatureCount'] = int(payload[i:i + 2], 16)
            i = i + 2
            temperatureAlarm = []
            for c in range(0, self.data['TemperatureCount']):
                temperatureAlarm.append(self.alarm(payload[i:i + 2]))
                i = i + 2
            self.data['TemperatureAlarm'] = temperatureAlarm

            self.data['ChargeCurentAlarm'] = self.alarm(payload[i:i + 2])
            i = i + 2
            self.data['ModuleVoltageAlarm'] = self.alarm(payload[i:i + 2])
            i = i + 2
            self.data['DischargeCurrentAlarm'] = self.alarm(payload[i:i + 2])
            i = i + 2
            self.data['Status1'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['Status2'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['Status3'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['Status4'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['Status5'] = int(payload[i:i + 2], 16)
            i = i + 2
        else:
            print('wrong decoder selected')
        return self.data


    def decodeSystemParameter(self):
        payload = self.data['PAYLOAD']
        if (self.data['ID'] == 0x46) and (len(payload) == 50):
            self.data['UnitCellVoltage'] = self.moduleVoltage(payload[0:4])
            self.data['UnitCellLowVoltageThreshold'] = self.cellVoltage(payload[4:8])
            self.data['UnitCellHighVoltageThreshold'] = self.cellVoltage(payload[8:12])
            # TODO: Temperature decoding seems broken here.
            self.data['ChargeUpperLimitTemperature'] = self.temperature(payload[12:16])
            self.data['ChargeLowerLimitTemperature'] = self.temperature(payload[16:20])
            self.data['ChargeLowerLimitCurrent'] = self.moduleCurrent(payload[20:24])
            self.data['UpperLimitOfTotalVoltage'] = self.moduleVoltage(payload[24:28])
            self.data['LowerLimitOfTotalVoltage'] = self.moduleVoltage(payload[28:32])
            self.data['UnderVoltageOfTotalVoltage'] = self.moduleVoltage(payload[32:36])
            self.data['DischargeUpperLimitTemperature'] = self.temperature(payload[36:40])
            self.data['DischargeLowerLimitTemperature'] = self.temperature(payload[40:44])
            self.data['DischargeLowerLimitCurrent'] = self.moduleCurrent(payload[44:48])
        else:
            self.data['UnitCellVoltage'] = None
            self.data['UnitCellLowVoltageThreshold'] = None
            self.data['UnitCellHighVoltageThreshold'] = None
            self.data['ChargeUpperLimitTemperature'] = None
            self.data['ChargeLowerLimitTemperature'] = None
            self.data['ChargeLowerLimitCurrent'] = None
            self.data['UpperLimitOfTotalVoltage'] = None
            self.data['LowerLimitOfTotalVoltage'] = None
            self.data['UnderVoltageOfTotalVoltage'] = None
            self.data['DischargeUpperLimitTemperature'] = None
            self.data['DischargeLowerLimitTemperature'] = None
            self.data['DischargeLowerLimitCurrent'] = None
            raise Exception('format error')
        return self.data

    def decodeAnalogValue(self):
        if self.data['ID'] == 0x46:
            # No size check - variable size possible
            payload = self.data['PAYLOAD']
            i = 0
            self.data['InfoFlag'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['CommandValue'] = int(payload[i:i + 2], 16)
            i = i + 2
            self.data['CellCount'] = int(payload[i:i + 2], 16)
            i = i + 2
            cellVoltages = []
            for c in range(0, self.data['CellCount']):
                cellVoltages.append(self.cellVoltage(payload[i:i + 4]))
                i = i + 4
            self.data['CellVoltages'] = cellVoltages
            self.data['TemperatureCount'] = int(payload[i:i + 2], 16)
            i = i + 2
            temperatures = []
            for c in range(0, self.data['TemperatureCount']):
                temperatures.append(self.temperature(payload[i:i + 4]))
                i = i + 4
            self.data['Temperatures'] = temperatures
            self.data['Current'] = self.moduleCurrent(payload[i:i + 4])
            i = i + 4
            self.data['Voltage'] = self.moduleVoltage(payload[i:i + 4])
            i = i + 4
            self.data['RemainCapacity'] = int(payload[i:i + 4], 16) / 1000.0
            i = i + 4
            if int(payload[i:i + 2], 16) == 4:
                self.data['CapDetect'] = '>65Ah'
            else:
                self.data['CapDetect'] = '<=65Ah'
            i = i + 2
            self.data['ModuleTotalCapacity'] = int(payload[i:i + 4], 16) / 1000.0
            i = i + 4
            self.data['CycleNumber'] = int(payload[i:i + 4], 16)
            i = i + 4
            if self.data['CapDetect'] == '>65Ah':
                self.data['RemainCapacity'] = self.capacity(payload[i:i + 6])
                i = i + 6
                self.data['ModuleTotalCapacity'] = self.capacity(payload[i:i + 6])
                i = i + 6
        else:
            print('wrong decoder selected')
        return self.data

    def decodeSerialNumber(self):
        payload = self.data['PAYLOAD']
        if (self.data['ID'] == 0x46) and (len(payload) == 34):
            self.data['CommandValue'] = bytes.fromhex(payload[0:2].decode("ASCII")).decode("ASCII").rstrip('\x00')
            self.data['ModuleSerialNumber'] = bytes.fromhex(payload[2:34].decode("ASCII")).decode("ASCII").rstrip(
                '\x00')
        else:
            print('Format Error')
            self.data['ModuleSerialNumber'] = None
            self.data['CommandValue'] = None
        return self.data


if __name__ == '__main__':
    pass
