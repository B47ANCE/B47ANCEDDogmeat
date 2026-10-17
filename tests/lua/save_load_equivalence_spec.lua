-- Two fresh VMs supply indistinguishable observed histories to the REAL Lua
-- boundary. Fake bodies are not native serialization, a packet exploit or PZ
-- restart proof. Source inspection supplies the missing-provenance premise.
local S=require "storage_support"
local P=require "pairing_support"
local Runtime=require "B47Dog/NativeRuntime"
local Reader=require "B47Dog/NativeAnimal"
local Codec=require "B47Dog/Codec"
local witnessPath="option-a-observation-witness.json"
local slot="FixtureDogs/"..S.WORLD.."/slot-a.json"
if RESTART_PHASE=="honest" then S.seed() end
local privateBefore=assert(testfs_read(slot))
local api,flags,calls,fire=P.fixture()
flags.animals={}
local animal=S.animal()
-- UID is a per-construction value in the inspected native superclass; neither
-- value is in the animal save format or the recovered private binding.
function animal:getUID() return RESTART_PHASE=="honest" and "fixture-uid-one" or "fixture-uid-two" end
local runtime=assert(Runtime.install(P.config(),api))
fire("OnInitGlobalModData");fire("OnServerStarted")
local reader=assert(Reader.new("FixtureDogs",P.config().allowedTypes,api))
local observation=assert(Codec.encode(reader.observe(animal)))
local result=runtime.assessAdmission(animal,"save_load")
assert(result.decision=="QUARANTINE" and result.reason=="NativeProvenanceUnverified")
assert(result.dogId==S.DOG and result.bindingVerified==false)
local context,intent=P.request()
context.actor.accountId="Mallory";context.actor.episodeId="mallory-1"
local prepared,why=runtime.prepareOwnership(animal,context,intent)
assert(prepared==nil and why=="UntrustedNativeMarker")
assert(testfs_read(slot)==privateBefore and calls.writes==0)
local witness={observation=observation,privateBytes=privateBefore,anchor=flags.anchor,
    decision=result,uid=animal:getUID()}
if RESTART_PHASE=="honest" then
    testfs_write(witnessPath,assert(Codec.encode(witness)))
else
    assert(RESTART_PHASE=="copy")
    local previous=assert(Codec.decode(assert(testfs_read(witnessPath))))
    assert(previous.observation==witness.observation)
    assert(previous.privateBytes==witness.privateBytes)
    assert(Codec.encode(previous.anchor)==Codec.encode(witness.anchor))
    assert(Codec.encode(previous.decision)==Codec.encode(witness.decision))
    assert(previous.uid~=witness.uid) -- new object handles/UIDs do not pick a winner
end
return {passed=1,failed=0,failures={}}
