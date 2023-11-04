ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 py3-pip

RUN pip3 install pip install --no-binary pydantic pydantic~=1.10.10
RUN pip3 install pyserial~=3.5 paho-mqtt~=1.6.1 homeassistant~=2023.10.5 setuptools~=68.2.0 StrEnum~=0.4.15 ha-mqtt-discoverable~=0.10.0

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
