local Codec=require "B47Dog/Codec"
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Snapshot={}
local fields={worldId=true,saveLocator=true,checkpoint=true,previous=true,sequence=true,
    allocationEpoch=true,allocationHighwater=true,recordCount=true,payloadBytes=true,payloadChecksum=true,payload=true}

local function metadata(body)
    return Identity.keys(body,fields) and Identity.uuid(body.worldId) and Guard.id(body.saveLocator)
        and Identity.uuid(body.checkpoint) and (Identity.uuid(body.previous) or body.previous=="ROOT")
        and Guard.integer(body.sequence,1) and Identity.uuid(body.allocationEpoch)
        and Guard.integer(body.allocationHighwater,0)
        and ((body.sequence==1 and body.previous=="ROOT") or (body.sequence>1 and body.previous~="ROOT"))
        and body.checkpoint~=body.previous
end

local function recordCount(payload,worldId)
    if not Guard.plain(payload) or not Guard.plain(payload.records) then return nil end
    local count=0
    for dogId,record in pairs(payload.records) do
        count=count+1
        if count>256 or not Identity.uuid(dogId) or not Guard.plain(record) or not Guard.state(record.ownership)
            or record.ownership.worldId~=worldId or record.ownership.dogId~=dogId then return nil end
        if record.binding~=nil and (not Identity.binding(record.binding)
            or record.binding.generation~=record.ownership.generation) then return nil end
        if record.ownership.phase=="LIVE" and record.binding==nil then return nil end
    end
    return count
end

function Snapshot.seal(meta,payload)
    if not metadata(meta) then return nil,"Recovery" end
    local count=recordCount(payload,meta.worldId)
    local encoded=Codec.encode(payload)
    if not count or not encoded then return nil,"Recovery" end
    local body={worldId=meta.worldId,saveLocator=meta.saveLocator,checkpoint=meta.checkpoint,
        previous=meta.previous,sequence=meta.sequence,allocationEpoch=meta.allocationEpoch,
        allocationHighwater=meta.allocationHighwater,recordCount=count,payloadBytes=#encoded,
        payloadChecksum=Codec.checksum(encoded),payload=payload}
    local bytes=Codec.encode(body)
    if not bytes then return nil,"Capacity" end
    return Codec.encode({schema=1,body=body,checksum=Codec.checksum(bytes)})
end

function Snapshot.open(bytes,worldId,saveLocator)
    local envelope=Codec.decode(bytes)
    if not Guard.plain(envelope) then return nil,"Corrupt" end
    if envelope.schema~=1 then return nil,"FutureSchema" end
    if not Identity.keys(envelope,{schema=true,body=true,checksum=true}) or not metadata(envelope.body) then return nil,"Corrupt" end
    local body=envelope.body
    if body.worldId~=worldId or body.saveLocator~=saveLocator then return nil,"ForeignStore" end
    local canonical=Codec.encode(body)
    local payload=body.payload
    local payloadBytes=Codec.encode(payload)
    if not canonical or envelope.checksum~=Codec.checksum(canonical) or not payloadBytes
        or body.payloadBytes~=#payloadBytes or body.payloadChecksum~=Codec.checksum(payloadBytes) then return nil,"Corrupt" end
    local count=recordCount(payload,worldId)
    if count==nil or count~=body.recordCount then return nil,"Corrupt" end
    return {meta=body,payload=payload}
end

return Snapshot
