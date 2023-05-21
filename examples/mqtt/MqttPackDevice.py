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
                     entity=SensorInfo(name="CycleNumber", unit_of_measurement="", device_class="None",
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
                         entity=SensorInfo(name="CellVoltage_" + str(cell), unit_of_measurement="V",
                                           device_class="voltage",
                                           unique_id=unique_id_base + "_CellVoltage_" + str(cell),
                                           device=self.device_info))
            )

        for ts in range(temperature_count):
            packSensors['Temperature_' + str(ts)] = Sensor(
                Settings(mqtt=self.mqtt_settings,
                         entity=SensorInfo(name="Temperature_" + str(ts), unit_of_measurement="°C",
                                           device_class="temperature",
                                           unique_id=unique_id_base + "_Temperature_" + str(ts),
                                           device=self.device_info))
            )

        return packSensors

    def _create_alarm_sensors(self, serial_number, batt_nr, cell_count, temperature_count):
        unique_id_base = "PPack_Nr_" + str(batt_nr) + "_sn_" + self.serial_number
        packSensors = {}

        packSensors['ChargeCurentAlarm'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ChargeCurentAlarm", unit_of_measurement="",
                                       device_class="None", unique_id=unique_id_base + "_ChargeCurentAlarm",
                                       device=self.device_info))
        )
        packSensors['DischargeCurrentAlarm'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="DischargeCurrentAlarm", unit_of_measurement="",
                                       device_class="None", unique_id=unique_id_base + "_DischargeCurrentAlarm",
                                       device=self.device_info))
        )

        packSensors['InfoFlag'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="InfoFlag", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_InfoFlag", device=self.device_info))
        )

        packSensors['ModuleVoltageAlarm'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ModuleVoltageAlarm", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_ModuleVoltageAlarm", device=self.device_info))
        )

        packSensors['Status1'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Status1", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Status1", device=self.device_info))
        )

        packSensors['Status2'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Status2", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Status2", device=self.device_info))
        )

        packSensors['Status3'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Status3", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Status3", device=self.device_info))
        )

        packSensors['Status4'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Status4", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Status4", device=self.device_info))
        )

        packSensors['Status5'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="Status5", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_Status5", device=self.device_info))
        )

        for cell in range(cell_count):
            packSensors['CellAlarm_' + str(cell)] = Sensor(
                Settings(mqtt=self.mqtt_settings,
                         entity=SensorInfo(name="CellAlarm_" + str(cell), unit_of_measurement="", device_class="None",
                                           unique_id=unique_id_base + "_CellAlarm_" + str(cell),
                                           device=self.device_info))
            )

        for ts in range(temperature_count):
            packSensors['TemperatureAlarm_' + str(ts)] = Sensor(
                Settings(mqtt=self.mqtt_settings,
                         entity=SensorInfo(name="TemperatureAlarm_" + str(ts), unit_of_measurement="",
                                           device_class="None",
                                           unique_id=unique_id_base + "_TemperatureAlarm_" + str(ts),
                                           device=self.device_info))
            )

        return packSensors

    def _create_charge_management_sensors(self, serial_number, batt_nr, cell_count, temperature_count):
        unique_id_base = "PPack_Nr_" + str(batt_nr) + "_sn_" + self.serial_number
        packSensors = {}

        packSensors['ChargeCurrent'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ChargeCurrent", unit_of_measurement="A",
                                       device_class="current", unique_id=unique_id_base + "_ChargeCurrent",
                                       device=self.device_info))
        )
        packSensors['ChargeVoltage'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="ChargeVoltage", unit_of_measurement="V",
                                       device_class="voltage", unique_id=unique_id_base + "_ChargeVoltage",
                                       device=self.device_info))
        )

        packSensors['DischargeCurrent'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="DischargeCurrent", unit_of_measurement="A", device_class="current",
                                       unique_id=unique_id_base + "_DischargeCurrent", device=self.device_info))
        )

        packSensors['DischargeVoltage'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="DischargeVoltage", unit_of_measurement="V", device_class="voltage",
                                       unique_id=unique_id_base + "_DischargeVoltage", device=self.device_info))
        )

        packSensors['StatusChargeEnable'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="StatusChargeEnable", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_StatusChargeEnable", device=self.device_info))
        )

        packSensors['StatusChargeImmediately1'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="StatusChargeImmediately1", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_StatusChargeImmediately1", device=self.device_info))
        )

        packSensors['StatusChargeImmediately2'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="StatusChargeImmediately2", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_StatusChargeImmediately2", device=self.device_info))
        )

        packSensors['StatusDischargeEnable'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="StatusDischargeEnable", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_StatusDischargeEnable", device=self.device_info))
        )

        packSensors['StatusFullChargeRequired'] = Sensor(
            Settings(mqtt=self.mqtt_settings,
                     entity=SensorInfo(name="StatusFullChargeRequired", unit_of_measurement="", device_class="None",
                                       unique_id=unique_id_base + "_StatusFullChargeRequired", device=self.device_info))
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
        self.haSensors = {}
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
        self.haSensors['AnalogList'] = self._create_analog_sensors(serial_number, number, cell_count, temperature_count)
        self.haSensors['AlarmInfoList'] = self._create_alarm_sensors(serial_number, number, cell_count,
                                                                     temperature_count)
        self.haSensors['ChargeDischargeManagementList'] = self._create_charge_management_sensors(serial_number, number,
                                                                                                 cell_count,
                                                                                                 temperature_count)

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

    def update_alarm_sensors(self, newData):
        for e in newData.keys():
            if e in self.haSensors['AlarmInfoList']:
                # single sensors here
                print("set: ", e)
                self.haSensors['AlarmInfoList'][e].set_state(newData[e])
            else:
                # sensor lists go here
                if e == 'TemperatureAlarm':
                    for t in range(len(newData['TemperatureAlarm'])):
                        self.haSensors['AlarmInfoList']['TemperatureAlarm_' + str(t)].set_state(
                            newData['TemperatureAlarm'][t])
                if e == 'CellAlarm':
                    for c in range(len(newData['CellAlarm'])):
                        self.haSensors['AlarmInfoList']['CellAlarm_' + str(c)].set_state(newData['CellAlarm'][c])

    def update_charge_management_sensors(self, newData):
        for e in newData.keys():
            if e in self.haSensors['ChargeDischargeManagementList']:
                # single sensors here
                print("set: ", e)
                self.haSensors['ChargeDischargeManagementList'][e].set_state(newData[e])
