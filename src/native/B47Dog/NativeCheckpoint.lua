-- Called only by the server's native-load event coordinator. Never receive/import
-- client ModData. A published in-memory anchor is pending, not a completed save.
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Authority=require "B47Dog/NativeAuthority"
local NativeCheckpoint={}

local function valid(anchor)
    return Identity.keys(anchor,{schema=true,worldId=true,checkpoint=true}) and anchor.schema==1
        and Identity.uuid(anchor.worldId) and Identity.uuid(anchor.checkpoint)
end

function NativeCheckpoint.capture(namespace,api)
    if type(namespace)~="string" or #namespace>64 or not namespace:match("^[A-Za-z][A-Za-z0-9_]*$")
        or type(api)~="table" or type(api.isServer)~="function" or type(api.isClient)~="function"
        or type(api.getCurrentSaveName)~="function" or type(api.ModData)~="table"
        or type(api.ModData.get)~="function" then return nil,"Unavailable" end
    local ok,anchor,locator=pcall(function()
        if not Authority.allowed(api) then return nil end
        return api.ModData.get(namespace),api.getCurrentSaveName()
    end)
    if not ok or not Guard.id(locator) then return nil,"Unavailable" end
    if anchor==nil then return nil,"MissingAnchor" end
    if not valid(anchor) then return nil,"InvalidAnchor" end
    local worldId,checkpoint=anchor.worldId,anchor.checkpoint
    local pending=false
    local captured={}
    function captured.pairing()
        return {kind="NativeLoaded",worldId=worldId,saveLocator=locator,checkpoint=checkpoint}
    end
    function captured.unchanged()
        local checked,result=pcall(function()
            return not pending and Authority.allowed(api)
                and api.getCurrentSaveName()==locator and api.ModData.get(namespace)==anchor
                and valid(anchor) and anchor.worldId==worldId and anchor.checkpoint==checkpoint
        end)
        return checked and result==true
    end
    function captured.publish(prepared)
        if not captured.unchanged() then return nil,"AnchorChanged" end
        if not Identity.keys(prepared,{status=true,checkpoint=true,sequence=true,slot=true})
            or prepared.status~="PREPARED_READBACK" or not Identity.uuid(prepared.checkpoint)
            or prepared.checkpoint==checkpoint or not Guard.integer(prepared.sequence,2)
            or (prepared.slot~="a" and prepared.slot~="b") then return nil,"Recovery" end
        -- Both private slots are retained by PrivateStore. The coordinator refuses
        -- further writes even if a save event fires or this live table is read again.
        pending=true
        anchor.checkpoint=prepared.checkpoint
        return {status="WAITING_NATIVE_RELOAD",checkpoint=prepared.checkpoint}
    end
    return captured
end

return NativeCheckpoint
