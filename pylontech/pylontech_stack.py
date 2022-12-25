"""! @brief Pylontech battery stack polling class."""
import time

##
# @file pylontech_stack.py
#
# @brief Pylontech battery stack polling class.
#
# @section pylontech-python Authors
# - Created by Bernd Singer
# - Abstraction layers added by Daniel Schramm
#
# @section License
# - MIT


from pylontech.pylontech_base import PylontechRS485
from pylontech.pylontech_decode import PylontechDecode
from pylontech.pylontech_encode import PylontechEncode


class PylontechStack:
    """! Whole battery stack abstraction layer.
    This class provides an easy-to-use interface to poll all batteries and get
    a ready calculated overall status for te battery stack.
    All Data polled is attached as raw result lists as well.
    """

    def poll_serial_number(self, batt, retries=3):
        retryCount = 0
        while retryCount < retries:
            retryCount = retryCount + 1
            packet_data = self.encode.getSerialNumber(battNumber=batt, group=self.group)
            self.pylon.send(packet_data)
            try:
                raws = self.pylon.receive(0.2)  # serial number should provide a fast answer.
            except Exception as e:
                print("Pylontech RX exception ", e.args)
                raws = None
                self.pylon.reconnect()
            except ValueError as e:
                print("Pylontech RX exception ", e.args)
                raws = None
                self.pylon.reconnect()

            if raws is not None:
                self.decode.decode_header(raws[0])
                try:
                    decoded = self.decode.decodeSerialNumber()
                    return decoded
                except Exception as e:
                    print("Pylontech decode exception ", e.args)
        raise Exception('Retry count exceeded.')

    def __init__(self, device, baud=9600, manualBattcountLimit=15, group=0):
        """! The class initializer.
        @param device  RS485 device name (ex Windows: 'com0', Linux: '/dev/ttyUSB0').
        @param baud  RS485 baud rate. Usually 9500 or 115200 for pylontech.
        @param manualBattcountLimit  Class probes for the number of batteries in stack which takes a lot of time.
        @param group Group number if more than one battery groups are configured
        This parameter limits the probe action for quick startup. (especially useful for Testing)

        @return  An instance of the Sensor class initialized with the specified name.
        """
        self.encode = PylontechEncode()
        self.decode = PylontechDecode()
        self.pylonData = {}
        self.group = group
        self.pylon = None

        try:
            self.pylon = PylontechRS485(device=device, baud=baud)
        except Exception as e:
            raise Exception('Connection to battery failed.') from e
        serialList = []
        for batt in range(0, manualBattcountLimit, 1):
            try:
                decoded = self.poll_serial_number(batt)
                serialList.append(decoded['ModuleSerialNumber'])
            except Exception as e:
                raise Exception('Poll for serial numbers failed.') from e
        self.pylonData['SerialNumbers'] = serialList
        self.battcount = len(serialList)
        self.pylonData['Calculated'] = {}

    def update(self):
        """! Stack polling function.
        @return  A dict with all collected Information.
        """
        starttime=time.time()
        print("start update")
        analoglList = []
        chargeDischargeManagementList = []
        alarmInfoList = []

        totalCapacity = 0
        remainCapacity = 0
        power = 0
        for batt in range(0, self.battcount):
            try:
                self.pylon.clear_rx_buffer()
                self.pylon.send(self.encode.getAnalogValue(battNumber=batt, group=self.group))
                raws = self.pylon.receive()
                self.decode.decode_header(raws[0])
                decoded = self.decode.decodeAnalogValue()
                analoglList.append(decoded)
                remainCapacity = remainCapacity + decoded['RemainCapacity']
                totalCapacity = totalCapacity + decoded['ModuleTotalCapacity']
                power = power + (decoded['Voltage'] * decoded['Current'])

                self.pylon.send(self.encode.getChargeDischargeManagement(battNumber=batt, group=self.group))
                raws = self.pylon.receive()
                self.decode.decode_header(raws[0])
                decoded = self.decode.decodeChargeDischargeManagementInfo()
                chargeDischargeManagementList.append(decoded)

                self.pylon.send(self.encode.getAlarmInfo(battNumber=batt, group=self.group))
                raws = self.pylon.receive()
                self.decode.decode_header(raws[0])
                decoded = self.decode.decodeAlarmInfo()
                alarmInfoList.append(decoded)
            except Exception as e:
                self.pylon.reconnect()
                raise Exception('Pylontech update error') from e
            except ValueError as e:
                self.pylon.reconnect()
                raise Exception('Pylontech update error') from e

        self.pylonData['AnaloglList'] = analoglList
        self.pylonData['ChargeDischargeManagementList'] = chargeDischargeManagementList
        self.pylonData['AlarmInfoList'] = alarmInfoList

        try:
            self.pylon.send(self.encode.getSystemParameter())
            raws = self.pylon.receive()
            self.decode.decode_header(raws[0])
            decoded = self.decode.decodeSystemParameter()
            self.pylonData['SystemParameter'] = decoded
        except Exception as e:
            self.pylon.reconnect()
            raise Exception('Pylontech update error') from e
        except ValueError as e:
            self.pylon.reconnect()
            raise Exception('Pylontech update error') from e

        self.pylonData['Calculated']['TotalCapacity_Ah'] = totalCapacity
        self.pylonData['Calculated']['RemainCapacity_Ah'] = remainCapacity
        self.pylonData['Calculated']['Remain_Percent'] = round((remainCapacity / totalCapacity) * 100, 0)

        self.pylonData['Calculated']['Power_kW'] = round(power / 1000, 5)
        if self.pylonData['Calculated']['Power_kW'] > 0:
            self.pylonData['Calculated']['ChargePower_kW'] = self.pylonData['Calculated']['Power_kW']
            self.pylonData['Calculated']['DischargePower_kW'] = 0
        else:
            self.pylonData['Calculated']['ChargePower_kW'] = 0
            self.pylonData['Calculated']['DischargePower_kW'] = -1.0 * self.pylonData['Calculated']['Power_kW']
        print("end update: ", time.time()-starttime)
        return self.pylonData


if __name__ == '__main__':
    import pprint

    # device = 'COM3'
    #dev = '/dev/ttyUSB0'
    dev = 'socket://10.10.4.13:23'
    pylon = PylontechStack(device=dev, baud=115200, manualBattcountLimit=7, group=0)
    stackResult = pylon.update()
    # pprint.pprint(stackResult)
    pprint.pprint(stackResult['Calculated'])
