-- you may like to copy this file to ~/.local/lib/wireshark/plugins
--
-- dissector for Pylontech,
--  Source: PYLON low voltage Protocol RS485 V3.3 2018/08/21
--
--

OR, XOR, AND = 1, 3, 4

function bitoper(a, b, oper)
    -- for non-negative 32-bit integers
    local r, m, s = 0, 2^31
    repeat
        s,a,b = a+b+m, a%m, b%m
        r,m = r + m*oper%(s-a-b), m/2
    until m < 1
    return r
end

-- declare our protocol
pylontech_proto = Proto("pylontech_rs485","Pylontech RS-485 serial")


-- create a function to dissect it
function pylontech_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "Pylontech"
    local yesno_types = {
        [0] = "No",
        [1] = "Yes"
    }
    local subtree = tree:add(pylontech_proto,buffer(),"pylontech frame")
    if buffer(0,1):uint() == 0x7e then
        local pos;
        pos = 0
        -- ok, startbyte
        -- hint on buffer: buffer(pos, Length)
        subtree:add(buffer(pos,1),"SOI / '~' = Start bit mark")
        pos = pos + 1
        -- check protocol version
        -- V2.1, VER = 21H (see page 13, response VER); in request: arbitrary value
        local version;
        version = tonumber(string.char(buffer(pos,1):uint(), buffer(pos +1,1):uint()),16)
        version_mayor = math.floor(version / 16)
        version_minor = version % 16
        subtree:add(buffer(pos,2),"Version of protocol: V" .. version_mayor .. "." .. version_minor)
        pos = pos + 2
        local address;
        address = string.char(buffer(pos,1):uint(), buffer(pos +1,1):uint())
        subtree:add(buffer(pos,2),"Address 0x" .. address .. " (0..255)" )
        pos = pos + 2
        local cid1;
        cid1 = string.char(buffer(pos,1):uint(), buffer(pos + 1,1):uint())
        subtree:add(buffer(pos,2),"CID1: 0x" .. cid1)
        pos = pos + 2
        local cid2;
        cid2 = string.char(buffer(pos,1):uint(), buffer(pos +1,1):uint())
        subtree:add(buffer(pos,2),"CID2: 0x" .. cid2)
        pos = pos + 2
        local length;
        length = string.char(buffer(pos + 1,1):uint(), buffer(pos + 2,1):uint(), buffer(pos + 3,1):uint())
        length = tonumber(length,16)
        lchksum_given =  tonumber(string.char(buffer(pos,1):uint()),16)
        lchksum_calc = ( tonumber(string.char(buffer(pos + 1,1):uint()),16)
                       + tonumber(string.char(buffer(pos + 2,1):uint()),16)
                       + tonumber(string.char(buffer(pos + 3,1):uint()),16) ) % 16
        lchksum_calc = bitoper(lchksum_calc,0xf,XOR) + 1
        if lchksum_given == lchksum_calc then
            length_str = "Length: " .. length
        else
            length_str = "Length: " .. length .. " Checksum wrong: " .. lchksum_given .. " <-> " .. lchksum_calc
        end
        subtree:add(buffer(pos,4),length_str)
        pos = pos + 4
        local datapos;
        datapos = pos
        chksumpos = datapos + length
        local info;
        info = string.char(buffer(pos,1):uint(), buffer(pos + 1,1):uint())
        subtree:add(buffer(pos,2),"Info: " .. info)
        pos = pos + 2
        -- checksum is at the end of the frame
        local chksum;
        pos = chksumpos
        chksum = string.char(buffer(pos,1):uint(), buffer(pos + 1,1):uint(), buffer(pos + 2,1):uint(), buffer(pos + 3,1):uint())
        subtree:add(buffer(pos,4),"Checksum: 0x" .. chksum)
        pos = pos + 4
        subtree:add(buffer(pos,1),"EOF (End of Frame)")
    else
        subtree:add(buffer(0,1),"wrong start byte")
    end
end

-- register_dissector ("Pylontech", pylontech_proto);

register_postdissector(pylontech_proto)

