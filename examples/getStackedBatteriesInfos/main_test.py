#!/bin/env python3
import datetime
from enum import auto

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
#from samba.dcerpc.initshutdown import initshutdown
from strenum import StrEnum

from dataclasses import dataclass
from typing import List
from typing import Any, Optional, Union
from pylontech import PylontechStack

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

DOMAIN = "pylontech_us"


class PylontechCoordinator:
    def dummy(self):
        pass


class PylontechPackSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Pylontech sensor."""

    def __init__(
            self,
            hass: HomeAssistant | None,
            coordinator: PylontechCoordinator | None,
            name: str,
            state_class: SensorStateClass | str | None,
            native_unit_of_measurement: str | None,
            device_class: SensorDeviceClass | str | None,
            icon: str | None,
            key_main: str,
            key_pack_nr: int,
            key_sub: str | None,
            key_sub_nr: int | None,
            entry_id: str,
            initial_result: PylontechStack
    ) -> None:
        """Stack summery value."""
        if not coordinator is None:
            super().__init__(coordinator)
        self._hass = hass
        self._result = initial_result

        self._key_main = key_main
        self._key_pack_nr = key_pack_nr
        self._key_sub = key_sub
        self._key_sub_nr = key_sub_nr
        self._entry_id = entry_id

        # result = await hass.async_add_executor_job(hub.update)
        self._attr_native_value = str(self.get_key_result())
        print('initial result ', self._attr_native_value)

        self._attr_name = name
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_available = True
        self._attr_should_poll = True

    def get_key_result(self):
        if self._result is None:
            return None
        if self._key_sub is None:
            return self._result[self._key_main][self._key_pack_nr - 1]
        if self._key_sub_nr is None:
            return self._result[self._key_main][self._key_pack_nr - 1][self._key_sub]
        return self._result[self._key_main][self._key_pack_nr - 1][self._key_sub][self._key_sub_nr-1]

    @property
    def unique_id(self) -> str:
        """Device Uniqueid."""
        return "pylontech_stack_" + self._entry_id + "_" + str(self._attr_name)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # self._attr_is_on = self.coordinator.data[self.idx]["state"]
        # self.async_write_ha_state()
        self._result = self._hass.data[DOMAIN][self._entry_id].get_result()
        # result = await hass.async_add_executor_job(hub.update)
        self._attr_native_value = self.get_key_result()

        # super()._handle_coordinator_update()
        self._attr_available = True
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Poll battery stack."""
        await self.coordinator.async_request_refresh()

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        # self._sensor.enabled = True

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        # self._sensor.enabled = False


def pylon_to_sensors(data: PylontechStack, hass=None) -> List[SensorEntity]:
    print('----- pylon_to_sensors -----')
    return_list = []
    pack_count = 1
    for d in data['SerialNumbers']:
        print(d)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_Serial'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=None,
            device_class="serial_number",  # SensorDeviceClass.,
            icon="mdi:numeric",
            key_main='SerialNumbers',
            key_sub=None,
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        pack_count = pack_count + 1
    pack_count = 1
    for d in data['AnalogList']:
        print(d)
        element_count=1
        for v in d['CellVoltages']:
            sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_CellVoltage_' + str(element_count)
            sensor = PylontechPackSensor(
                hass=None, coordinator=None,
                name=str(sensor_name),
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement='V',
                device_class= SensorDeviceClass.VOLTAGE,
                icon="mdi:lightning-bolt",
                key_main='AnalogList',
                key_sub='CellVoltages',
                key_sub_nr=element_count,
                key_pack_nr=pack_count,
                entry_id=sensor_name,
                initial_result=data
            )
            element_count=element_count+1
            return_list.append(sensor)
        element_count = 1
        for t in d['Temperatures']:
            sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_Temperature' + str(element_count)
            sensor = PylontechPackSensor(
                hass=None, coordinator=None,
                name=str(sensor_name),
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement='?C',
                device_class=SensorDeviceClass.TEMPERATURE,
                icon="mdi:thermometer",
                key_main='AnalogList',
                key_sub='Temperatures',
                key_sub_nr=element_count,
                key_pack_nr=pack_count,
                entry_id=sensor_name,
                initial_result=data
            )
            element_count=element_count+1
            return_list.append(sensor)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_Current'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement='A',
            device_class=SensorDeviceClass.CURRENT,
            icon="mdi:current-dc",
            key_main='AnalogList',
            key_sub='Current',
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        return_list.append(sensor)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_Voltage'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement='V',
            device_class=SensorDeviceClass.VOLTAGE,
            icon="mdi:lightning-bolt",
            key_main='AnalogList',
            key_sub='Voltage',
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        return_list.append(sensor)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_RemainCapacity'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement='Ah',
            device_class='capacity',
            icon="mdi:battery",
            key_main='AnalogList',
            key_sub='RemainCapacity',
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        return_list.append(sensor)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_ModuleTotalCapacity'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement='Ah',
            device_class='capacity',
            icon="mdi:battery",
            key_main='AnalogList',
            key_sub='ModuleTotalCapacity',
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        return_list.append(sensor)
        sensor_name = 'Pylontech_PackNr_' + str(pack_count), '_CycleNumber'
        sensor = PylontechPackSensor(
            hass=None, coordinator=None,
            name=str(sensor_name),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=None,
            device_class='capacity',
            icon="mdi:battery",
            key_main='AnalogList',
            key_sub='CycleNumber',
            key_sub_nr=None,
            key_pack_nr=pack_count,
            entry_id=sensor_name,
            initial_result=data
        )
        return_list.append(sensor)
        pack_count = pack_count + 1

    return return_list


try:
    #x = PylontechStack("/dev/ttyUSB0", baud=115200, manualBattcountLimit=7)
    x = PylontechStack("socket://10.10.4.13:23", baud=115200, manualBattcountLimit=7)

    x.battcount
    x.pylonData
    x.update()

    print(pylon_to_sensors(data=x.pylonData))

    # print(x.pylonData['Calculated'])
    # print(x.pylonData['SerialNumbers'])
    # print(x.pylonData['AnalogList'])
    # print(x.pylonData['ChargeDischargeManagementList'])
    # print(x.pylonData['AlarmInfoList'])

#    for key in x.pylonData.keys():
#        print(key)

#    print(x.pylonData)
except:
    print("exception")
