#!/usr/bin/env python3
import argparse
import sys
import time
from pprint import pprint
from threading import Event
import paho.mqtt.client as mqtt
from pylontech import PylontechStack
import os

import pickle

from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo, Sensor, SensorInfo
from MqttStackDevice import MqttStackDevice
from MqttPackDevice import MqttPackDevice

#TODO: rename 'AnaloglList' to 'AnalogList'


parser = argparse.ArgumentParser(description='Pylontech RS485 to MQTT bridge.')

parser.add_argument('--pylon', type=ascii, dest='pylon_port', action='store',
                    help= "Pylontech port. (serial oder network)")
parser.add_argument('--baud', type=int, dest='pylon_baud', action='store',
                    help= "Pylontech serial baudrate. (default=115200)", default=115200)
parser.add_argument('--packs', type=int, dest='pylon_packs', action='store',
                    help= "Pylontech number ob packs in stack. (default=16)", default=16)
parser.add_argument('--mqtt', type=ascii, dest='mqtt_host', action='store',
                    help= "MQTT Server name or IP")
parser.add_argument('--port', type=int, dest='pylon_baud', action='store',
                    help= "MQTT Port (optional)", default=1883)
parser.add_argument('--user', type=ascii, dest='mqtt_user', action='store',
                    help= "MQTT Username")
parser.add_argument('--pass', type=ascii, dest='mqtt_pass', action='store',
                    help= "MQTT Password")

args = parser.parse_args()
pprint(args)

with open("sample_data.pkl", "rb") as infile:
    test_data = pickle.load(infile)

pprint(test_data.keys())
pprint(test_data['SystemParameter'])
# for e in test_data['Calculated']:
#    pprint(e)


if args.mqtt_host is None:
    print("Please provide MQTT Server name.")
    sys.exit(1)

mqtt_settings = None
if args.mqtt_user is None and args.mqtt_pass is None:
    print("Connecting MQTT with username and password.")
    mqtt_settings = Settings.MQTT(
        host=args.mqtt_host.replace('\'', ''),
        username=args.mqtt_user.replace('\'', ''),
        password=args.mqtt_pass.replace('\'', '')
    )
else:
    print("Connecting MQTT anonymous.")
    mqtt_settings = Settings.MQTT(
        host=args.mqtt_host.replace('\'', '')
    )

pprint(mqtt_settings)
# Configure the required parameters for the MQTT broker
# stack=MqttStackDevice(mqtt_settings)
# stack.update_sensors(test_data)

packs = []
number = 0
for sn in test_data['SerialNumbers']:
    # get individual array sizes for each pack, if the stack uses different types of packs.
    cell_count = test_data['AnaloglList'][number]['CellCount']
    temperature_count = test_data['AnaloglList'][number]['TemperatureCount']
    packs.append(MqttPackDevice(mqtt_settings, sn, number, cell_count, temperature_count))
    number = number + 1

for i in range(len(test_data['SerialNumbers'])):
    packs[i].update_analog_sensors(test_data['AnaloglList'][i])

exit(0)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


class MqttConnection:
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.connected = True
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected with result code " + str(rc))

    def on_log(self, client, userdata, level, buf):
        print("Log: " + str(buf))

    def __init__(self):
        self.connected = False
        clientId = "pylontech_mqtt_" + str(os.getpid())
        self.client = mqtt.Client(client_id=clientId, clean_session=True, userdata=None)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = on_message
        self.client.connect(args.mqtt_host, port=1883, keepalive=30)
        self.client.publish("test/test", clientId)
        self.client.disconnect()

    def update(self):
        time.sleep(60)


# mc = MqttConnection()


exit(0)

# Port examples: "/dev/ttyUSB0", "socket://10.10.4.13:23", "rfc2217://10.10.4.13:23"

print('evaluating the stack of batteries (0..n batteries)')
# x = PylontechStack('/dev/ttyUSB0', baud=115200, manualBattcountLimit=7)
x = PylontechStack(args.pylon_port, baud=args.pylon_port, manualBattcountLimit=args.pylon_packs)
print('number of batteries found: {}'.format(x.battcount))
print('received data:')
print(x.pylonData)

# while 1:
try:
    starttime = time.time()
    x.update()
    with open('sample_data.pkl', "wb") as outfile:
        pickle.dump(x.pylonData, outfile)
    pprint(x.pylonData['Calculated'])
    time.sleep((starttime + 30) - time.time())
    # Event.wait(1)

except Exception as err:
    print("Timeout ", err)
