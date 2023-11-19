#!/usr/bin/with-contenv bashio
bashio::log.info "Starting PylontechMqtt.py..."

PYLON=$(bashio::config 'pylon')
BAUD=$(bashio::config 'baud')
PACKS=$(bashio::config 'packs')
MQTT_IP=$(bashio::config 'mqtt_ip')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'username')
MQTT_PASS=$(bashio::config 'password')

cd /pylontech/examples/mqtt/
python3 PylontechMqtt.py --user $MQTT_USER --pass $MQTT_PASS --mqtt $MQTT_IP --port $MQTT_PORT --pylon $PYLON --packs $PACKS --baud $BAUD