local Guard=require "B47Dog/Guard"
local Codec=require "B47Dog/Codec"
local Identity={}

function Identity.uuid(value)
    return type(value)=="string" and #value==36 and value:sub(9,9)=="-" and value:sub(14,14)=="-"
        and value:sub(19,19)=="-" and value:sub(24,24)=="-"
        and #value:gsub("-","")==32 and value:gsub("-",""):match("^[0-9a-f]+$")~=nil
end

function Identity.keys(value, allowed)
    if not Guard.plain(value) then return false end
    for key in pairs(value) do if not allowed[key] then return false end end
    return true
end

function Identity.marker(marker)
    return Identity.keys(marker,{schema=true,worldId=true,dogId=true,bindingGeneration=true,bindingToken=true})
        and marker.schema==1 and Identity.uuid(marker.worldId) and Identity.uuid(marker.dogId)
        and Identity.uuid(marker.bindingToken) and Guard.integer(marker.bindingGeneration,1)
end

function Identity.binding(binding)
    if not Identity.keys(binding,{generation=true,nativeType=true,breed=true,acceptedTokens=true})
        or not Guard.integer(binding.generation,1) or not Guard.id(binding.nativeType)
        or not Guard.id(binding.breed) or not Guard.plain(binding.acceptedTokens) then return false end
    local count=0
    for key,value in pairs(binding.acceptedTokens) do
        count=count+1
        if count>64 or not Identity.uuid(key) or value~=true then return false end
    end
    return count>0
end

-- Tracks observed references only; it cannot certify absence of unloaded duplicates.
-- Quarantine is sticky for the life of this recovery session. No automatic adoption.
function Identity.newRegistry(worldId, records)
    if not Identity.uuid(worldId) or not Guard.plain(records) then return nil,"Recovery" end
    local encoded=Codec.encode(records)
    if not encoded then return nil,"Recovery" end
    records=Codec.decode(encoded)
    local dogs, handles, quarantine, handleCount, dogCount={}, {}, {}, 0, 0
    local exhausted=false
    local registry={}
    function registry.observe(handle, observation)
        if exhausted then return {status="CAPACITY"} end
        if type(handle)~="table" and type(handle)~="userdata" then return {status="UNBOUND"} end
        if not Guard.plain(observation) or observation.status~="OBSERVED" or not Identity.marker(observation.marker) then
            local known=handles[handle]
            if known then quarantine[known]=true end
            return {status=known and "QUARANTINED" or "UNBOUND",dogId=known}
        end
        local marker=observation.marker; local id=marker.dogId
        -- Both axes are bounded: one handle can present many different IDs.
        -- Stop the whole session on exhaustion, preserving all existing evidence.
        if (not handles[handle] and handleCount>=1024) or (not dogs[id] and dogCount>=1024) then
            exhausted=true
            return {status="CAPACITY"}
        end
        if not dogs[id] then dogCount=dogCount+1 end
        if not handles[handle] then
            handleCount=handleCount+1
        end
        if handles[handle] and handles[handle]~=id then quarantine[handles[handle]]=true; quarantine[id]=true end
        handles[handle]=id
        local record=records[id]
        if marker.worldId~=worldId or not Guard.plain(record) or not Guard.state(record.ownership)
            or not Identity.binding(record.binding) or record.ownership.worldId~=worldId
            or record.ownership.dogId~=id or record.ownership.phase~="LIVE"
            or record.ownership.generation~=marker.bindingGeneration
            or record.binding.generation~=marker.bindingGeneration
            or not record.binding.acceptedTokens[marker.bindingToken]
            or observation.nativeType~=record.binding.nativeType or observation.breed~=record.binding.breed then
            quarantine[id]=true
        end
        if dogs[id] and dogs[id]~=handle then quarantine[id]=true end
        dogs[id]=handle
        return {status=quarantine[id] and "QUARANTINED" or "MATCHED",dogId=id,generation=marker.bindingGeneration}
    end
    function registry.status(dogId)
        if exhausted then return "CAPACITY" end
        return quarantine[dogId] and "QUARANTINED" or dogs[dogId] and "MATCHED" or "UNOBSERVED"
    end
    return registry
end

return Identity
