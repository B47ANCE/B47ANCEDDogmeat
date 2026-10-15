-- Separate VM phases prove that a fresh hook install is NOT prior-session proof.
local S=require "storage_support"
local P=require "pairing_support"
local Admission=require "B47Dog/NativeAdmissionGuard"
local Session=require "B47Dog/NativeSession"
local api,flags,calls=S.api()
if RESTART_PHASE=="prepare" then S.seed() end
local guard=assert(Admission.install(P.config(),api))
local session=assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
    allowedTypes=P.config().allowedTypes},api))
if RESTART_PHASE=="prepare" then
    api.ISPickupAnimal.complete=function() return true end
    assert(guard.check()==nil)
    assert(session.identitySummary().dogId==S.DOG and calls.writes==0)
elseif RESTART_PHASE=="recover" then
    assert(guard.check()==true and guard.status().ownershipReady==false)
    assert(session.identitySummary().dogId==S.DOG)
    local clone=S.animal();local context,intent=P.request()
    context.bindingVerified=true;context.storeRecovered=true
    local result,why=session.prepareOwnership(clone,context,intent)
    assert(result==nil and why=="UntrustedNativeMarker" and calls.writes==0)
    local snapshot=assert(require("B47Dog/Snapshot").open(
        testfs_read("FixtureDogs/"..S.WORLD.."/slot-a.json"),S.WORLD,"fixture-save"))
    local record=snapshot.payload.records[S.DOG]
    assert(record.ownership.ownerAccount=="Alice" and record.ownership.revision==3)
    assert(record.privateHistory.retained=="HIDDEN_FIXTURE" and record.admission==nil)
else error("Missing restart phase") end
return {passed=1,failed=0,failures={}}
