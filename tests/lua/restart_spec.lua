-- Run in two separate Lua VMs sharing only a disposable directory of JSON files.
local S=require "storage_support"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
if RESTART_PHASE=="prepare" then
    local payload=S.seed();local transport=assert(Cache.new("FixtureDogs",S.WORLD,S.api()))
    local session=assert(Store.open(transport,S.pair()))
    payload.records[S.DOG].ownership.name="After restart"; payload.records[S.DOG].ownership.revision=4
    assert(session.prepare(payload,S.NEXT,1).status=="PREPARED_READBACK")
else
    local transport=assert(Cache.new("FixtureDogs",S.WORLD,S.api()))
    local value,reason=Store.open(transport,S.pair())
    assert(value==nil and reason=="PreparedPending")
    -- Explicit simulated operator pairing. This is NOT native-save completion proof.
    local session=assert(Store.open(transport,S.pair(S.NEXT)))
    assert(session.read().payload.records[S.DOG].ownership.name=="After restart")
    assert(session.read().payload.records[S.DOG].privateHistory.retained=="HIDDEN_FIXTURE")
end
return {passed=1,failed=0,failures={}}
