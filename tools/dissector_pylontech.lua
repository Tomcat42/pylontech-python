-- you may like to copy this file to ~/.local/lib/wireshark/plugins
--
-- dissector for Pylontech,
--  Source: PYLON low voltage Protocol RS485 V3.3 2018/08/21
--
--
-- declare our protocol
pylontech_proto = Proto("pylontech_rs485","Pylontech RS-485 serial")

-- create a function to dissect it
function pylontech_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "Pylontech"
    local subtree = tree:add(pylontech_proto,buffer(),"pylontech frame")
    if buffer(0,1):uint() == 0x7e then
        -- ok, startbyte
        -- hint on buffer: buffer(pos, Length)
        subtree:add(buffer(0,1),"SOI / '~' = Start bit mark")
        -- check protocol version
        -- V2.1, VER = 21H (see page 13, response VER); in request: arbitrary value
        local version_mayor;
        local version_minor;
        version_minor = buffer(1,1):uint() % 16
        version_mayor = math.floor(buffer(1,1):uint() / 16)
        local version;
        version = "Version of protocol: V" .. version_mayor .. "." .. version_minor
        subtree:add(buffer(1,1),version)
        local address;
        address = string.char(buffer(2,1):uint(),buffer(3,1):uint())
        subtree:add(buffer(2,2),"Address 0x" .. address .. " (0..255)" )
        subtree:add(buffer(4,1),"CID1")
        subtree:add(buffer(5,1),"CID2")
        subtree:add(buffer(6,2),"Length")
    else
        subtree:add(buffer(0,1),"wrong start byte")
    end
end

-- register_dissector ("Pylontech", pylontech_proto);

register_postdissector(pylontech_proto)

