# pylontech-python
Functions to communicate to Pylontech Batteries using RS-485 serial communication

3 Layer model - each can be used as lib:
  1. pylontech_base.py - Communication layer, RS485 to pylontech with raw frame support
  2. pylontech_decode.py and pylontech_encode.py for decodeing and encoding the frame content
  3. pylontech_stack.py high level abstraction for the whole stack.
     It iterates over batteries and calculates overall results and combines battery results to lists.
     Some detail information from layer 2 might not be implemented in this layer.


Installation using setup.py:

run 'python3 ./setup.py install'


Example:
an example to use pylontech-python:

  >>> from pylontech import PylontechStack
  >>> x = PylontechStack("/dev/ttyUSB0",baud=115200,manualBattcountLimit=5)
  >>> x.battcount
  2

A big "Thanks" to Daniel Schramm for his contibution!
