# capture from a second RS-485 adapter to a pipe to be used by wireshark
mkfifo /tmp/wspipe
wireshark -X "lua_script:dissector_pylontech.lua" -k -i /tmp/wspipe &
mono SerialPCAP_pylon.exe -o /tmp/wspipe --pipe --baud=115200 --parity=N --stopbits=1  /dev/ttyUSB1 &

