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

"""
ChargeDischargeManagementList entry
[{'ADR': 2,
  'ChargeCurrent': 80.0,
  'ChargeVoltage': 53.25,
  'CommandValue': 2,
  'DischargeCurrent': -80.0,
  'DischargeVoltage': 45.0,
  'ID': 70,
  'LENGTH': 20,
  'PAYLOAD': b'02D002AFC80320FCE0C0',
  'RTN': 0,
  'StatusChargeEnable': True,
  'StatusChargeImmediately1': False,
  'StatusChargeImmediately2': False,
  'StatusDischargeEnable': True,
  'StatusFullChargeRequired': False,
  'VER': 32},
  
  AlarmInfoList entry
{'ADR': 2,
  'CellAlarm': ['Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok',
                'Ok'],
  'CellCount': 15,
  'ChargeCurentAlarm': 'Ok',
  'CommandValue': 2,
  'DischargeCurrentAlarm': 'Ok',
  'ID': 70,
  'InfoFlag': 0,
  'LENGTH': 68,
  'ModuleVoltageAlarm': 'Ok',
  'PAYLOAD': b'00020F00000000000000000000000000000006000000000000000000000E4000'
             b'0000',
  'RTN': 0,
  'Status1': 0,
  'Status2': 14,
  'Status3': 64,
  'Status4': 0,
  'Status5': 0,
  'TemperatureAlarm': ['Ok', 'Ok', 'Ok', 'Ok', 'Ok', 'Ok'],
  'TemperatureCount': 6,
  'VER': 32},  
"""


class MqttPackDevice:
    def _create_analog_sensors(self, serial_number, batt_nr, cell_count, temperature_count):
        unique_id_base = "PPack_Nr_" + str(batt_nr) + "_sn_" + self.serial_number
        packSensors = {}

        packSensors['RemainCapacity'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="RemainCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id=unique_id_base + "_RemainCapacity",
                                       device=self.device_info))
        )
        packSensors['ModuleTotalCapacity'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ModuleTotalCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id=unique_id_base + "_ModuleTotalCapacity",
                                       device=self.device_info))
        )

        packSensors['CycleNumber'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="CycleNumber", unit_of_measurement="%", device_class="None",
                                       unique_id=unique_id_base + "_CycleNumber", device=self.device_info))
        )

        packSensors['Current'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Current", unit_of_measurement="A", device_class="current",
                                       unique_id=unique_id_base + "_Current", device=self.device_info))
        )

        packSensors['Voltage'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Voltage", unit_of_measurement="V", device_class="voltage",
                                       unique_id=unique_id_base + "_Voltage", device=self.device_info))
        )

        for cell in range(cell_count):
            packSensors['CellVoltage_' + str(cell)] = Sensor(
                Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="CellVoltage_" + str(cell), unit_of_measurement="V", device_class="voltage",
                                       unique_id=unique_id_base + "_CellVoltage_" + str(cell), device=self.device_info))
            )

        for ts in range(temperature_count):
            packSensors['Temperature_' + str(ts)] = Sensor(
                Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Temperature_" + str(ts), unit_of_measurement="V", device_class="temperature",
                                       unique_id=unique_id_base + "_Temperature_" + str(ts), device=self.device_info))
            )

        return packSensors

    def __init__(self, mqtt_settings, serial_number, number, cell_count, temperature_count):
        # TODO: replace with parameters
        print("create pack device: ", number)
        self.serial_number = serial_number
        self.mqtt_settings = mqtt_settings
        unique_id_base = "PPack" + self.serial_number
        self.device_info = DeviceInfo(name="Pylontech Pack (" + str(number) + ") " + str(serial_number),
                                      identifiers="Pylontech_Pack_" + serial_number)
        self.haSensors={}
        self.haSensors['number'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Number in Stack", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Nr", device=self.device_info))
        )
        self.haSensors['serial_number'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Serial Number", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_SN", device=self.device_info))
        )
        self.haSensors['AnalogList']=self._create_analog_sensors(serial_number, number, cell_count, temperature_count)

    def update_analog_sensors(self, newData):
        for e in newData.keys():
            if e in self.haSensors['AnalogList']:
                # single sensors here
                print("set: ", e)
                self.haSensors['AnalogList'][e].set_state(newData[e])
            else:
                # sensor lists go here
                if e == 'Temperatures':
                    for t in range(len(newData['Temperatures'])):
                        self.haSensors['AnalogList']['Temperature_' + str(t)].set_state(newData['Temperatures'][t])
                if e == 'CellVoltages':
                    for c in range(len(newData['CellVoltages'])):
                        self.haSensors['AnalogList']['CellVoltage_' + str(c)].set_state(newData['CellVoltages'][c])


