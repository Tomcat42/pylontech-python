#!/usr/bin/env python3
import argparse
import sys
import time

from ha_mqtt_discoverable import Settings

from MqttPackDevice import MqttPackDevice
from MqttStackDevice import MqttStackDevice
from pylontech import PylontechStack


def main(_pylon_stack, _mqtt_settings):
    print("Initial data poll.")
    _pylon_stack.update()
    data = _pylon_stack.pylonData
    ha_stack = MqttStackDevice(_mqtt_settings)
    ha_stack.update_sensors(data)

    packs = []
    number = 0
    for sn in data['SerialNumbers']:
        # get individual array sizes for each pack, if the stack uses different types of packs.
        cell_count = data['AnalogList'][number]['CellCount']
        temperature_count = data['AnalogList'][number]['TemperatureCount']
        packs.append(MqttPackDevice(_mqtt_settings, sn, number, cell_count, temperature_count))
        number = number + 1
        time.sleep(2)

    print("Entering main loop")
    while 1:
        try:
            start_time = time.time()
            try:
                _pylon_stack.update()
            except Exception as err:
                print("Pylontech update exception: ", err)

            data = _pylon_stack.pylonData
            ha_stack.update_sensors(data)
            for i in range(len(data['SerialNumbers'])):
                packs[i].update_analog_sensors(data['AnalogList'][i])
                packs[i].update_alarm_sensors(data['AlarmInfoList'][i])
                packs[i].update_charge_management_sensors(data['ChargeDischargeManagementList'][i])
                sleep_time = (start_time + 30) - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except Exception as err:
            print("Main loop exception: ", err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pylontech RS485 to MQTT bridge.')

    parser.add_argument('--pylon', type=str, dest='pylon_port', action='store',
                        help="Pylontech port. (serial oder network)")
    parser.add_argument('--baud', type=int, dest='pylon_baud', action='store',
                        help="Pylontech serial baudrate. (default=115200)", default=115200)
    parser.add_argument('--packs', type=int, dest='pylon_packs', action='store',
                        help="Pylontech number ob packs in stack. (default=16)", default=16)
    parser.add_argument('--mqtt', type=str, dest='mqtt_host', action='store',
                        help="MQTT Server name or IP")
    parser.add_argument('--port', type=int, dest='pylon_baud', action='store',
                        help="MQTT Port (optional)", default=1883)
    parser.add_argument('--user', type=str, dest='mqtt_user', action='store',
                        help="MQTT Username")
    parser.add_argument('--pass', type=str, dest='mqtt_pass', action='store',
                        help="MQTT Password")

    args = parser.parse_args()

    # Port examples: "/dev/ttyUSB0", "socket://10.10.4.13:23", "rfc2217://10.10.4.13:23"
    pylonStack = PylontechStack(args.pylon_port, baud=args.pylon_baud, manualBattcountLimit=args.pylon_packs)

    if args.mqtt_host is None:
        print("Please provide MQTT Server name.")
        sys.exit(1)

    mqtt_settings = None
    if (args.mqtt_user is not None) and (args.mqtt_pass is not None):
        print("Connecting MQTT with username and password.")
        mqtt_settings = Settings.MQTT(
            host=args.mqtt_host,
            username=args.mqtt_user,
            password=args.mqtt_pass
        )
    else:
        print("Connecting MQTT anonymous.")
        mqtt_settings = Settings.MQTT(
            host=args.mqtt_host.replace('\'', '')
        )

    main(pylonStack, mqtt_settings)
