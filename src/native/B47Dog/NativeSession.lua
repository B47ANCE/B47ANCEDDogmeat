-- Explicit server-side coordinator, not a network endpoint or event handler.
-- It prepares private ownership changes only; it does not commit native gameplay.
local Codec=require "B47Dog/Codec"
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Ownership=require "B47Dog/Ownership"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
local Animal=require "B47Dog/NativeAnimal"
local NativeSession={}

function NativeSession.open(config,api)
    api=api or _G
    if not Guard.plain(config) or type(api)~="table" or type(api.getRandomUUID)~="function"
        or not Guard.plain(config.pairing) or config.pairing.worldId~=config.worldId then return nil,"Unavailable" end
    local transport,reason=Cache.new(config.namespace,config.worldId,api)
    if not transport then return nil,reason end
    if config.pairing.saveLocator~=transport.saveLocator then return nil,"ForeignStore" end
    local store; store,reason=Store.open(transport,config.pairing)
    if not store then return nil,reason end
    local reader;reader,reason=Animal.new(config.namespace,config.allowedTypes,api)
    if not reader then return nil,reason end
    local baseline=store.read()
    local registry;registry,reason=Identity.newRegistry(config.worldId,baseline.payload.records)
    if not registry then return nil,reason end
    local busy=false
    local session={}
    function session.observe(animal)
        return registry.observe(animal,reader.observe(animal))
    end
    function session.status(dogId)
        return registry.status(dogId)
    end
    function session.observeDeath(animal)
        local observation=reader.observe(animal)
        if observation.status~="Dead" then return {status="Unavailable"} end
        return registry.observe(animal,observation)
    end
    function session.prepareOwnership(animal,context,intent)
        if busy then return nil,"Busy" end
        busy=true
        local ok,result,errorCode=pcall(function()
            local matched=session.observe(animal)
            if matched.status~="MATCHED" then return nil,"Recovery" end
            if not Guard.context(context) or context.worldId~=baseline.meta.worldId then return nil,"Unavailable" end
            -- Caller supplies authenticated actor/episode and current interaction facts.
            -- Never call this API with client args as context; no such adapter exists yet.
            local encoded=Codec.encode(context)
            if not encoded then return nil,"Invalid" end
            local trusted=Codec.decode(encoded)
            trusted.bindingVerified=true;trusted.storeRecovered=true
            local record=baseline.payload.records[matched.dogId]
            local proposal=Ownership.propose(record.ownership,trusted,intent)
            if not proposal.ok then return nil,proposal.reason end
            if not proposal.changed then return {status="UNCHANGED"} end
            local payload=store.read().payload
            for _,field in ipairs({"ownershipEvents","checkpointLedger"}) do
                if payload[field]~=nil and not Guard.plain(payload[field]) then return nil,"Recovery" end
                payload[field]=payload[field] or {}
            end
            local checkpoint
            for _=1,16 do
                local candidate=api.getRandomUUID()
                if not Identity.uuid(candidate) then return nil,"Recovery" end
                if candidate~=baseline.meta.checkpoint and not payload.checkpointLedger[candidate]
                    and not payload.ownershipEvents[candidate] then checkpoint=candidate;break end
            end
            if not checkpoint then return nil,"Recovery" end
            -- Reobserve after UUID/caller-facing work, immediately before preparation.
            local fresh=session.observe(animal)
            if fresh.status~="MATCHED" or fresh.dogId~=matched.dogId then return nil,"Recovery" end
            payload.records[matched.dogId].ownership=proposal.state
            payload.checkpointLedger[baseline.meta.checkpoint]=true
            payload.checkpointLedger[checkpoint]=true
            payload.ownershipEvents[checkpoint]={kind="OWNERSHIP_PREPARED",dogId=matched.dogId,
                generation=matched.generation,previousRevision=record.ownership.revision,event=proposal.event}
            return store.prepare(payload,checkpoint,baseline.meta.allocationHighwater)
        end)
        busy=false
        if not ok then return nil,"Recovery" end
        return result,errorCode
    end
    return session
end

return NativeSession
