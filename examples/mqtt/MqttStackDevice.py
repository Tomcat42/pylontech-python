#!/usr/bin/env python3
import time
from pprint import pprint
from threading import Event
import paho.mqtt.client as mqtt
from pylontech import PylontechStack
import os

import pickle

from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo, Sensor, SensorInfo


class MqttStackDevice:

    def _create_calc_sensors(self):
        calcSensors = {}
        calcSensors['Power'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Power", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_Power_1", device=self.device_info))
        )
        calcSensors['ChargePower_W'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ChargePower", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_ChargePower_1", device=self.device_info))
        )
        calcSensors['DischargePower_W'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="DischargePower", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_DischargePower_1", device=self.device_info))
        )
        calcSensors['RemainCapacity_Ah'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="RemainCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id="Pylon_RemainCapacity_1",
                                       device=self.device_info))
        )
        calcSensors['TotalCapacity_Ah'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="TotalCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id="Pylon_TotalCapacity_1",
                                       device=self.device_info))
        )

        calcSensors['Remain_Percent'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Remain_Percent", unit_of_measurement="%", device_class="battery",
                                       unique_id="Pylon_Remain_Percent_1", device=self.device_info))
        )

        return calcSensors

    def __init__(self, mqtt_settings):
        # TODO: replace with parameters
        self.mqtt_settings = mqtt_settings
        self.device_info = DeviceInfo(name="Pylontech_Stack", identifiers="Pylontech_Stack_10_10_10_8")
        self.haSensors = {'Calculated': self._create_calc_sensors()}
        time.sleep(2)

    def update_sensors(self, newData):
        for e in newData['Calculated'].keys():
            print(e)
            if e in self.haSensors['Calculated']:
                print("set: ", e)
                self.haSensors['Calculated'][e].set_state(newData['Calculated'][e])

"""
System parameter

{'ADR': 2,
 'ChargeLowerLimitCurrent': 1817.9,
 'ChargeLowerLimitTemperature': -195.3,
 'ChargeUpperLimitTemperature': -681.4,
 'DischargeLowerLimitCurrent': 1842.8,
 'DischargeLowerLimitTemperature': -195.3,
 'DischargeUpperLimitTemperature': -476.6,
 'ID': 70,
 'LENGTH': 50,
 'LowerLimitOfTotalVoltage': 61.619,
 'PAYLOAD': b'100E420BEA0AF00D030A4703E8D2F0B3B0A7F80D030A47FC18',
 'RTN': 0,
 'UnderVoltageOfTotalVoltage': 45.223,
 'UnitCellHighVoltageThreshold': -5.622,
 'UnitCellLowVoltageThreshold': 16.907,
 'UnitCellVoltage': 4.11,
 'UpperLimitOfTotalVoltage': 59.602,
 'VER': 32} 
"""