local S=require "storage_support"
local P=require "pairing_support"
local Runtime=require "B47Dog/NativeRuntime"
if RESTART_PHASE=="prepare" then S.seed() end
local api,flags,calls,fire=P.fixture()
local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData");fire("OnServerStarted")
local result=runtime.assessAdmission(flags.animals[1],"save_load")
assert(result.decision=="QUARANTINE" and result.dogId==S.DOG and result.bindingVerified==false)
if RESTART_PHASE=="prepare" then
    api.ISPickupAnimal.complete=function() end
    assert(runtime.status().phase=="RECOVERY")
elseif RESTART_PHASE=="recover" then
    -- The fresh process has intact hooks but no attestation about its predecessor.
    assert(runtime.status().admission.ownershipReady==false)
    local context,intent=P.request()
    assert(runtime.prepareOwnership(flags.animals[1],context,intent)==nil)
else error("Missing restart phase") end
assert(calls.writes==0)
return {passed=1,failed=0,failures={}}
