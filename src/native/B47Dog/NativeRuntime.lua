-- Explicit event installation for a configured server. No spawn/init/UI or network
-- endpoint. Native load is a one-shot boundary; live tables cannot promote a save.
local Guard=require "B47Dog/Guard"
local Codec=require "B47Dog/Codec"
local Identity=require "B47Dog/Identity"
local Checkpoint=require "B47Dog/NativeCheckpoint"
local Session=require "B47Dog/NativeSession"
local NativeRuntime={}
local installed=setmetatable({},{__mode="k"})

function NativeRuntime.install(config,api)
    api=api or _G
    if not Identity.keys(config,{namespace=true,allowedTypes=true}) or type(api)~="table"
        or type(config.namespace)~="string" or #config.namespace>64
        or not config.namespace:match("^[A-Za-z][A-Za-z0-9_]*$") or not Guard.plain(config.allowedTypes)
        or type(api.isServer)~="function" or type(api.isClient)~="function" or type(api.Events)~="table" then
        return nil,"Unavailable"
    end
    local encoded=Codec.encode(config);if not encoded then return nil,"Invalid" end
    config=Codec.decode(encoded)
    local function server()
        local ok,result=pcall(function() return api.isServer()==true and api.isClient()==false end)
        return ok and result
    end
    if not server() then return nil,"Unavailable" end
    for _,name in ipairs({"OnInitGlobalModData","OnServerStarted","OnCharacterDeath"}) do
        if type(api.Events[name])~="table" or type(api.Events[name].Add)~="function" then return nil,"Unavailable" end
    end
    installed[api]=installed[api] or {}
    if installed[api][config.namespace] then return nil,"AlreadyInstalled" end
    local count=0;for _ in pairs(installed[api]) do count=count+1 end
    if count>=8 then return nil,"Capacity" end
    local phase,reason="WAITING_NATIVE_LOAD",nil
    local loaded=false
    local started=false
    local checkpoint,session
    local controller={}
    local function fail(code) phase="RECOVERY";reason=code end
    function controller.status()
        return {phase=phase,reason=reason,serverStarted=started}
    end
    function controller.observe(animal)
        if not server() or not session or phase~="RECOVERED" then return {status="Unavailable"} end
        if not checkpoint.unchanged() then fail("AnchorChanged");return {status="Unavailable"} end
        return session.observe(animal)
    end
    function controller.census()
        if not server() or not started or not session or phase~="RECOVERED" then return nil,"Unavailable" end
        if not checkpoint.unchanged() then fail("AnchorChanged");return nil,"AnchorChanged" end
        local ok,result=pcall(function()
            -- getAnimals scans native objectList. Called once at startup or by an
            -- explicit server recovery action, never by a tick/update callback.
            local cell=api.getCell();if cell==nil then return nil end
            local animals=cell:getAnimals();if animals==nil then return nil end
            local size=animals:size()
            if not Guard.integer(size,0) or size>1024 then return nil end
            local seen={}
            for index=0,size-1 do
                local observed=session.observe(animals:get(index))
                if observed.status=="CAPACITY" then return nil end
                if observed.dogId then seen[observed.dogId]=true end
            end
            local statuses={}
            for id in pairs(seen) do statuses[id]=session.status(id) end
            return {status="OBSERVED_LOADED_ONLY",animalsRead=size,dogs=statuses}
        end)
        if not ok or not result then fail("CensusUnavailable");return nil,"Unavailable" end
        return result
    end
    function controller.prepareOwnership(animal,context,intent)
        if not server() or not started or phase~="RECOVERED" or not session then return nil,"Unavailable" end
        if not checkpoint.unchanged() then fail("AnchorChanged");return nil,"AnchorChanged" end
        local prepared,why=session.prepareOwnership(animal,context,intent)
        if not prepared then
            if why=="WriteFailed" or why=="ReadbackFailed" or why=="ChangedOnDisk" then fail(why) end
            return nil,why
        end
        if prepared.status=="UNCHANGED" then return prepared end
        local published;published,why=checkpoint.publish(prepared)
        if not published then fail(why);return nil,why end
        phase="WAITING_NATIVE_RELOAD"
        return published
    end
    local function onLoaded()
        if loaded then return end -- duplicate events cannot promote an in-memory anchor
        loaded=true
        if started then fail("NativeLoadNotObserved");return end
        if not server() then fail("Unavailable");return end
        local ok=pcall(function()
            checkpoint,reason=Checkpoint.capture(config.namespace,api)
            if not checkpoint then fail(reason);return end
            local pairing=checkpoint.pairing()
            session,reason=Session.open({namespace=config.namespace,worldId=pairing.worldId,
                pairing=pairing,allowedTypes=config.allowedTypes},api)
            if not session then fail(reason);return end
            phase="RECOVERED";reason=nil
        end)
        if not ok then fail("LoadFailed") end
    end
    local function onStarted()
        if started then return end
        started=true
        if not loaded then fail("NativeLoadNotObserved");return end
        if phase=="RECOVERED" then controller.census() end
    end
    local function onDeath(animal)
        if not server() or not session then return end
        -- Native reader rechecks isDead; event arguments confer no authority.
        local ok=pcall(session.observeDeath,animal)
        if not ok then fail("ObservationFailed") end
    end
    -- Reserve before registering: partial registration must not be retried and
    -- duplicated. A failed installation needs a fresh process, not live recovery.
    installed[api][config.namespace]=controller
    local ok=pcall(function()
        api.Events.OnInitGlobalModData.Add(onLoaded)
        api.Events.OnServerStarted.Add(onStarted)
        api.Events.OnCharacterDeath.Add(onDeath)
    end)
    if not ok then fail("RegistrationFailed");loaded=true;return nil,"RegistrationFailed" end
    return controller
end

return NativeRuntime
