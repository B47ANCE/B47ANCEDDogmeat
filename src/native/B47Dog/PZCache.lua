-- Source-verified native file adapter. Inert until explicitly constructed/called.
-- Requires dedicated server role; no automatic recovery, world creation or hooks.
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Codec=require "B47Dog/Codec"
local PZCache={}

function PZCache.new(namespace,worldId,api)
    api=api or _G
    if type(namespace)~="string" or #namespace>64 or not namespace:match("^[A-Za-z][A-Za-z0-9_]*$")
        or not Identity.uuid(worldId) or type(api)~="table" then return nil,"Unavailable" end
    for _,name in ipairs({"isServer","isClient","getCurrentSaveName","getFileReader","getFileWriter"}) do
        if type(api[name])~="function" then return nil,"Unavailable" end
    end
    local function server()
        local ok,allowed=pcall(function() return api.isServer()==true and api.isClient()==false end)
        return ok and allowed
    end
    if not server() then return nil,"Unavailable" end
    local locatorOK,locator=pcall(api.getCurrentSaveName)
    if not locatorOK or not Guard.id(locator) then return nil,"Unavailable" end
    local function path(slot)
        if slot~="a" and slot~="b" then return nil end
        if not server() then return nil end
        local ok,current=pcall(api.getCurrentSaveName)
        if not ok or current~=locator then return nil end
        return namespace.."/"..worldId.."/slot-"..slot..".json"
    end
    local transport={saveLocator=locator,worldId=worldId}
    function transport.read(slot)
        local filename=path(slot)
        if not filename then return nil,"Unavailable" end
        local ok,reader=pcall(api.getFileReader,filename,false)
        if not ok or reader==nil then return nil,"Unavailable" end
        local readOK,line=pcall(function()
            local chunks,chunk={},{}
            for position=1,Codec.MAX_BYTES+1 do
                local code=reader:read()
                if code==-1 then
                    chunks[#chunks+1]=table.concat(chunk)
                    return table.concat(chunks)
                end
                if position>Codec.MAX_BYTES or type(code)~="number" or code<32 or code>126 or code~=math.floor(code) then
                    error("Corrupt",0)
                end
                chunk[#chunk+1]=string.char(code)
                if #chunk==1024 then chunks[#chunks+1]=table.concat(chunk);chunk={} end
            end
            error("Corrupt",0)
        end)
        local closed=pcall(function() reader:close() end)
        if not readOK or not closed or type(line)~="string" or #line==0 then
            return nil,"Corrupt"
        end
        -- Strict ASCII canonical bytes, including EOF. Never allocate an unbounded line.
        return line
    end
    function transport.write(slot,bytes)
        local filename=path(slot)
        if not filename or type(bytes)~="string" or #bytes>Codec.MAX_BYTES
            or bytes:find("[\r\n]") or bytes:find("[\128-\255]") then return nil,"Unavailable" end
        local ok,writer=pcall(api.getFileWriter,filename,true,false)
        if not ok or writer==nil then return nil,"WriteFailed" end
        local written=pcall(function() writer:write(bytes) end)
        local closed=pcall(function() writer:close() end)
        if not written or not closed then return nil,"WriteFailed" end
        -- PrintWriter can swallow errors. The store MUST reopen and compare readback.
        return true
    end
    return transport
end

return PZCache
