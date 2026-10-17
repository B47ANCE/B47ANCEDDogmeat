-- Separate VMs and real disposable private files; no actual PZ serialization.
local S=require "storage_support"
local Session=require "B47Dog/NativeSession"
local P=require "pairing_support"
local api,_,calls=S.api()
if RESTART_PHASE=="prepare" then S.seed() end
local session=assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
    allowedTypes={FixtureCanine={FixtureShepherd=true}}},api))
local summary=session.identitySummary()
assert(summary.dogId==S.DOG and summary.retained==1 and summary.bindingVerified==false)
if RESTART_PHASE=="prepare" then
    session.observe(S.animal())
    assert(session.observe(S.animal()).status=="QUARANTINED")
elseif RESTART_PHASE=="recover" then
    local clone=S.animal() -- only replayed marker visible in new VM
    assert(session.observe(clone).status=="MATCHED")
    local ctx,intent=P.request();local result,reason=session.prepareOwnership(clone,ctx,intent)
    assert(result==nil and reason=="UntrustedNativeMarker")
else error("unknown fixture phase") end
assert(calls.writes==0)
return {passed=1,failed=0,failures={}}
