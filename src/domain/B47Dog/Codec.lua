-- Original bounded canonical JSON subset: objects, UTF-8 strings, booleans,
-- signed 31-bit integers. No arrays/null/floats, executable code or dependencies.
local Codec = { MAX_BYTES=1048576, MAX_STRING=16384, MAX_NODES=8192, MAX_DEPTH=16 }

local function fail() error("InvalidData", 0) end
local function utf8(point)
    if point < 128 then return string.char(point) end
    if point < 2048 then return string.char(192+math.floor(point/64),128+point%64) end
    if point < 65536 then return string.char(224+math.floor(point/4096),128+math.floor(point/64)%64,128+point%64) end
    return string.char(240+math.floor(point/262144),128+math.floor(point/4096)%64,
        128+math.floor(point/64)%64,128+point%64)
end

local function quoted(value)
    if #value > Codec.MAX_STRING then fail() end
    local parts, index = {'"'}, 1
    while index <= #value do
        local first = value:byte(index)
        local length, point, minimum
        if first < 128 then length,point,minimum=1,first,0
        elseif first >= 194 and first <= 223 then length,point,minimum=2,first-192,128
        elseif first >= 224 and first <= 239 then length,point,minimum=3,first-224,2048
        elseif first >= 240 and first <= 244 then length,point,minimum=4,first-240,65536
        else fail() end
        for offset=1,length-1 do
            local byte=value:byte(index+offset)
            if not byte or byte<128 or byte>191 then fail() end
            point=point*64+byte-128
        end
        if point<minimum or point>1114111 or (point>=55296 and point<=57343) then fail() end
        if point==34 then parts[#parts+1]='\\"'
        elseif point==92 then parts[#parts+1]='\\\\'
        elseif point>=32 and point<127 then parts[#parts+1]=string.char(point)
        elseif point<=65535 then parts[#parts+1]=string.format('\\u%04x',point)
        else
            local pair=point-65536
            parts[#parts+1]=string.format('\\u%04x\\u%04x',55296+math.floor(pair/1024),56320+pair%1024)
        end
        index=index+length
    end
    parts[#parts+1]='"'
    return table.concat(parts)
end

function Codec.encode(value)
    local function run()
        local parts, active, nodes, size = {}, {}, 0, 0
        local function add(text)
            size=size+#text; if size>Codec.MAX_BYTES then fail() end
            parts[#parts+1]=text
        end
        local emit
        emit=function(item, depth)
            nodes=nodes+1; if nodes>Codec.MAX_NODES or depth>Codec.MAX_DEPTH then fail() end
            local kind=type(item)
            if kind=="string" then add(quoted(item))
            elseif kind=="boolean" then add(item and "true" or "false")
            elseif kind=="number" then
                if item~=item or item < -2147483647 or item>2147483647 or item~=math.floor(item) then fail() end
                add(item==0 and "0" or string.format("%.0f",item))
            elseif kind=="table" and getmetatable(item)==nil and not active[item] then
                active[item]=true
                local keys={}
                for key in pairs(item) do
                    if type(key)~="string" or #key>256 then fail() end
                    keys[#keys+1]=key; if #keys>Codec.MAX_NODES then fail() end
                end
                table.sort(keys); add("{")
                for position,key in ipairs(keys) do
                    if position>1 then add(",") end
                    add(quoted(key)); add(":"); emit(item[key],depth+1)
                end
                add("}"); active[item]=nil
            else fail() end
        end
        emit(value,1)
        return table.concat(parts)
    end
    local ok, result=pcall(run)
    if not ok then return nil,"InvalidData" end
    return result
end

function Codec.decode(text)
    if type(text)~="string" or #text>Codec.MAX_BYTES then return nil,"InvalidData" end
    local function run()
        local index,nodes=1,0
        local function hex()
            local digits=text:sub(index,index+3)
            if #digits~=4 or not digits:match("^[0-9a-fA-F]+$") then fail() end
            index=index+4; return tonumber(digits,16)
        end
        local function stringValue()
            index=index+1
            local parts,size={},0
            while index<=#text do
                local byte=text:byte(index); index=index+1
                if byte==34 then return table.concat(parts) end
                local piece
                if byte==92 then
                    local escape=text:sub(index,index); index=index+1
                    if escape=='"' or escape=='\\' then piece=escape
                    elseif escape=='u' then
                        local point=hex()
                        if point>=55296 and point<=56319 then
                            if text:sub(index,index+1)~='\\u' then fail() end
                            index=index+2; local low=hex()
                            if low<56320 or low>57343 then fail() end
                            point=65536+(point-55296)*1024+low-56320
                        elseif point>=56320 and point<=57343 then fail() end
                        piece=utf8(point)
                    else fail() end
                elseif byte>=32 and byte<127 then piece=string.char(byte)
                else fail() end
                size=size+#piece; if size>Codec.MAX_STRING then fail() end
                parts[#parts+1]=piece
            end
            fail()
        end
        local parse
        parse=function(depth)
            nodes=nodes+1; if nodes>Codec.MAX_NODES or depth>Codec.MAX_DEPTH then fail() end
            local first=text:sub(index,index)
            if first=='"' then return stringValue() end
            if first=='{' then
                index=index+1; local result={}
                if text:sub(index,index)=='}' then index=index+1; return result end
                while true do
                    if text:sub(index,index)~='"' then fail() end
                    local key=stringValue()
                    if #key>256 or result[key]~=nil or text:sub(index,index)~=':' then fail() end
                    index=index+1; result[key]=parse(depth+1)
                    local separator=text:sub(index,index); index=index+1
                    if separator=='}' then return result end
                    if separator~=',' then fail() end
                end
            end
            for word,value in pairs({["true"]=true,["false"]=false}) do
                if text:sub(index,index+#word-1)==word then index=index+#word; return value end
            end
            local start,finish=text:find("%-?%d+",index)
            if start~=index then fail() end
            local value=tonumber(text:sub(start,finish)); index=finish+1
            if not value or value < -2147483647 or value>2147483647 then fail() end
            return value
        end
        local value=parse(1)
        if index~=#text+1 or Codec.encode(value)~=text then fail() end
        return value
    end
    local ok,value=pcall(run)
    if not ok then return nil,"InvalidData" end
    return value
end

-- Adler-32, corruption detection only. Not authentication or a cryptographic hash.
function Codec.checksum(text)
    if type(text)~="string" or #text>Codec.MAX_BYTES then return nil end
    local a,b=1,0
    for index=1,#text do a=(a+text:byte(index))%65521; b=(b+a)%65521 end
    return string.format("%04x%04x",b,a)
end

return Codec
