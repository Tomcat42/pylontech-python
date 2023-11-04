ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 py3-pip

RUN pip3 install pyserial ha_mqtt_discoverable paho-mqtt homeassistant setuptools StrEnum pydantic~=1.10.12

# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
WORKDIR /data

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh
COPY ./ /pylontech/
RUN chmod a+x /pylontech/examples/mqtt/PylontechMqtt.py

RUN pip3 install /pylontech

CMD [ "/run.sh" ]
