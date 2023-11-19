# pylontech-python
Functions to communicate to Pylontech Batteries using RS-485 serial communication

3 Layer model - each can be used as lib:
  1. pylontech_base.py - Communication layer, RS485 to pylontech with raw frame support
  2. pylontech_decode.py and pylontech_encode.py for decodeing and encoding the frame content
  3. pylontech_stack.py high level abstraction for the whole stack.
     It iterates over batteries and calculates overall results and combines battery results to lists.
     Some detail information from layer 2 might not be implemented in this layer.

Installation using pypi.org:
- run 'pip install pylontech-python'


build and Installation from source using pip:

- build requires pip to be installed
- run 'pip wheel -r requirements.txt' (installs e.g. pyserial)
  this downloads the required packages
- run 'pip wheel .'
  this builds the wheel package
- run 'pip install --force-reinstall ./*.whl'
  this installs the packages (both downloaded and build)
  --force-reinstall is used if you like to modify, rebuild and reinstall it.


Example:
an example to use pylontech-python:

  >>> from pylontech import PylontechStack
  >>> x = PylontechStack("/dev/ttyUSB0",baud=115200,manualBattcountLimit=5)
  >>> x.battcount
  2

Application examples:

A new example has been added to show how to publish data from a single stack
and all its battery packs via MQTT to HomeAssistant.

