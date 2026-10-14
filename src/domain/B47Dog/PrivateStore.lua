local Guard=require "B47Dog/Guard"
local Codec=require "B47Dog/Codec"
local Identity=require "B47Dog/Identity"
local Snapshot=require "B47Dog/Snapshot"
local PrivateStore={}

local function equal(a,b)
    local encoded=Codec.encode(a)
    return encoded~=nil and encoded==Codec.encode(b)
end

local function appendOnly(before,after)
    if before==nil and after==nil then return true end
    if not Guard.plain(after) or before~=nil and not Guard.plain(before) then return false end
    for key,value in pairs(before or {}) do if not equal(value,after[key]) then return false end end
    return true
end

-- This slice can prepare ownership only. Lifecycle, allocation, deletion, migration
-- and retention require their own operation; never smuggle them into a checkpoint.
local function validTransition(before,after)
    if not Guard.plain(after) or not Guard.plain(after.records) then return false end
    local mutable={records=true,ownershipEvents=true,checkpointLedger=true}
    for key,value in pairs(before) do if not mutable[key] and not equal(value,after[key]) then return false end end
    for key in pairs(after) do if not mutable[key] and before[key]==nil then return false end end
    if not appendOnly(before.ownershipEvents,after.ownershipEvents)
        or not appendOnly(before.checkpointLedger,after.checkpointLedger) then return false end
    for id,old in pairs(before.records) do
        local new=after.records[id]
        if not Guard.plain(new) or not Guard.state(new.ownership) then return false end
        for key,value in pairs(old) do if key~="ownership" and not equal(value,new[key]) then return false end end
        for key in pairs(new) do if key~="ownership" and old[key]==nil then return false end end
        local a,b=old.ownership,new.ownership
        for _,key in ipairs({"schema","worldId","dogId","generation","phase"}) do if a[key]~=b[key] then return false end end
        local aclChanged=a.ownerAccount~=b.ownerAccount or a.ownerEpisode~=b.ownerEpisode or not equal(a.handlers,b.handlers)
        local changed=aclChanged or a.name~=b.name
        if b.revision~=a.revision+(changed and 1 or 0)
            or b.aclRevision~=a.aclRevision+(aclChanged and 1 or 0) then return false end
    end
    for id in pairs(after.records) do if before.records[id]==nil then return false end end
    return true
end

-- Pairing is a trusted operator assertion for an externally verified paired save.
-- No client anchor, newest-sequence guess, initialization or native-save hook here.
function PrivateStore.open(transport,pairing)
    if type(transport)~="table" or type(transport.read)~="function" or type(transport.write)~="function"
        or not Guard.plain(pairing) or pairing.kind~="OperatorPaired"
        or not Identity.uuid(pairing.worldId) or not Identity.uuid(pairing.checkpoint)
        or not Guard.id(pairing.saveLocator) then return nil,"Recovery" end
    local worldId,locator,checkpoint=pairing.worldId,pairing.saveLocator,pairing.checkpoint
    local raw,snapshots={},{}
    for _,slot in ipairs({"a","b"}) do
        local ok,bytes=pcall(transport.read,slot)
        if not ok or type(bytes)~="string" then return nil,"Unavailable" end
        raw[slot]=bytes
        local snapshot,reason=Snapshot.open(bytes,worldId,locator)
        if not snapshot then return nil,reason end
        snapshots[slot]=snapshot
    end
    local selected
    for _,slot in ipairs({"a","b"}) do
        if snapshots[slot].meta.checkpoint==checkpoint then
            if selected and raw[selected]~=raw[slot] then return nil,"Ambiguous" end
            selected=selected or slot
        end
    end
    if not selected then return nil,"Unpaired" end
    local inactive=selected=="a" and "b" or "a"
    local current,other=snapshots[selected],snapshots[inactive]
    if other.meta.checkpoint~=checkpoint then
        if other.meta.sequence==current.meta.sequence+1 and other.meta.previous==checkpoint then
            return nil,"PreparedPending"
        end
        if current.meta.sequence~=other.meta.sequence+1 or current.meta.previous~=other.meta.checkpoint
            or current.meta.allocationEpoch~=other.meta.allocationEpoch
            or current.meta.allocationHighwater<other.meta.allocationHighwater then return nil,"Ambiguous" end
    end
    local locked=false
    local session={}
    function session.read()
        -- Detached copy; callers cannot mutate the selected in-memory baseline.
        return Snapshot.open(raw[selected],worldId,locator)
    end
    function session.prepare(payload,nextCheckpoint,allocationHighwater)
        if locked then return nil,"Recovery" end
        if not Identity.uuid(nextCheckpoint) or nextCheckpoint==current.meta.checkpoint
            or nextCheckpoint==other.meta.checkpoint or not Guard.integer(allocationHighwater,0)
            or allocationHighwater~=current.meta.allocationHighwater or current.meta.sequence==Guard.MAX_COUNTER
            or not validTransition(current.payload,payload) then
            return nil,"Recovery"
        end
        for _,slot in ipairs({"a","b"}) do
            local ok,bytes=pcall(transport.read,slot)
            if not ok or bytes~=raw[slot] then locked=true; return nil,"ChangedOnDisk" end
        end
        local bytes,reason=Snapshot.seal({worldId=worldId,saveLocator=locator,checkpoint=nextCheckpoint,
            previous=current.meta.checkpoint,sequence=current.meta.sequence+1,
            allocationEpoch=current.meta.allocationEpoch,allocationHighwater=allocationHighwater},payload)
        if not bytes then return nil,reason end
        -- Lock BEFORE I/O. Failure can leave forensic evidence in the inactive slot.
        locked=true
        local ok,written=pcall(transport.write,inactive,bytes)
        if not ok or written~=true then return nil,"WriteFailed" end
        local readOK,readback=pcall(transport.read,inactive)
        if not readOK or readback~=bytes then return nil,"ReadbackFailed" end
        local verified=Snapshot.open(readback,worldId,locator)
        if not verified then return nil,"ReadbackFailed" end
        return {status="PREPARED_READBACK",checkpoint=nextCheckpoint,sequence=current.meta.sequence+1,slot=inactive}
    end
    return session
end

return PrivateStore
