Example to use the library to publish data to HomeAssistant.
The library https://github.com/unixorn/ha-mqtt-discoverable
is used for pushing the values.

Currently, the text based sensors do not push data.
This seems to be a limitation of ha-mqtt-discoverable and 
might need rework after this is merged:
https://github.com/unixorn/ha-mqtt-discoverable/pull/75