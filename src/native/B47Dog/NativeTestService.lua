-- Narrow admin test protocol. Never forwards client context into ownership code.
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Authority=require "B47Dog/NativeAuthority"
local Provision=require "B47Dog/NativeProvision"
local Service={}
function Service.new(config,runtime,api)
    local provision=assert(Provision.new(config,api))
    local clients=setmetatable({},{__mode="k"})
    local initialResult
    local service={}
    local function authorized(player)
        local ok,result=pcall(function()
            if not Authority.allowed(api) or api.instanceof(player,"IsoPlayer")~=true
                or player:isDead()~=false then return false end
            return api.B47DogSinglePlayer==true or player:getRole():hasCapability(api.Capability.AnimalCheats)==true
        end)
        return ok and result==true
    end
    function service.handle(player,command,args)
        if not authorized(player) then return nil end -- no private response to unauthorized clients
        local settings=api.SandboxVars and api.SandboxVars.B47ANCEDDogmeat
        if not settings or settings.PersistenceTestMode~=true then return {status="Disabled"} end
        if command~="Inspect" and command~="Provision" then return {status="Invalid"} end
        if not Identity.keys(args,command=="Inspect" and {protocol=true} or {protocol=true,challenge=true,ack=true})
            or args.protocol~=1 then return {status="Invalid"} end
        local now=api.getTimestampMs()
        if type(now)~="number" or now~=now or now<0 or now==math.huge then return {status="Unavailable"} end
        local client=clients[player]
        if not client then
            local count=0;for _ in pairs(clients) do count=count+1 end
            if count>=128 then return {status="Unavailable"} end
            client={};clients[player]=client
        end
        if command=="Inspect" and client.last and now-client.last<1000 then return {status="Busy"} end
        client.last=now
        local state=runtime.status()
        if not state.serverStarted then return {status="Unavailable"} end
        if initialResult then return {status=initialResult} end
        if command=="Provision" then
            local challenge=client.challenge;client.challenge=nil
            if not challenge or args.challenge~=challenge.id or args.ack~="NEW_DISPOSABLE_WORLD"
                or now<challenge.created or now-challenge.created>120000
                or api.getCurrentSaveName()~=challenge.locator
                or state.phase~="RECOVERY" or state.reason~="MissingAnchor" then return {status="Recovery"} end
            initialResult="Recovery" -- latch even an uncertain transaction
            local result=provision.create(challenge.locator,player)
            if result then initialResult=result.status end
            return {status=initialResult}
        end
        client.challenge=nil
        if state.phase=="RECOVERY" and state.reason=="MissingAnchor" and provision.available() then
            local id=api.getRandomUUID();local locator=api.getCurrentSaveName()
            if not Identity.uuid(id) or not Guard.id(locator) then return {status="Unavailable"} end
            client.challenge={id=id,locator=locator,created=now}
            return {status="NeedsInitialization",challenge=id}
        end
        if state.phase~="RECOVERED" then return {status=state.phase=="WAITING_NATIVE_RELOAD" and state.phase or "Recovery"} end
        local census=runtime.census()
        if not census then return {status="Recovery"} end
        local matched,other=0,0
        for _,status in pairs(census.dogs) do
            if status=="MATCHED" then matched=matched+1 else other=other+1 end
        end
        -- The displayed ID is recovered privately, never selected by a marker.
        return {status="Loaded",matched=matched,other=other,dogId=census.dogId,
            retained=census.retained,bindingVerified=false,admission=census.admission}
    end
    return service
end
return Service
