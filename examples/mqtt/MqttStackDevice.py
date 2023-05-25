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
        name_base = "PylontechStack_"
        calcSensors = {}
        calcSensors['Power'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "Power", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_Power_1", device=self.device_info))
        )
        calcSensors['ChargePower_W'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "ChargePower", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_ChargePower_1", device=self.device_info))
        )
        calcSensors['DischargePower_W'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "DischargePower", unit_of_measurement="W", device_class="power",
                                       unique_id="Pylon_DischargePower_1", device=self.device_info))
        )
        calcSensors['RemainCapacity_Ah'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "RemainCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id="Pylon_RemainCapacity_1",
                                       device=self.device_info))
        )
        calcSensors['TotalCapacity_Ah'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "TotalCapacity", unit_of_measurement="Ah",
                                       device_class="energy_storage", unique_id="Pylon_TotalCapacity_1",
                                       device=self.device_info))
        )

        calcSensors['Remain_Percent'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name=name_base + "Remain_Percent", unit_of_measurement="%", device_class="battery",
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
