-- Exercise the installed runtime, native reader, real private files, registry and
-- policy together. These fake engine objects are not native lifecycle evidence.
local S=require "storage_support"
local P=require "pairing_support"
local F=require "provision_support"
local Runtime=require "B47Dog/NativeRuntime"
local Cache=require "B47Dog/PZCache"
local Store=require "B47Dog/PrivateStore"
local Codec=require "B47Dog/Codec"
local Service=require "B47Dog/NativeTestService"
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,err=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(err) end
end
local function eq(a,b) assert(a==b,tostring(a).." ~= "..tostring(b)) end
local function fixture(setup)
    S.seed();local api,flags,calls,fire=P.fixture()
    if setup then setup(api,flags,calls) end
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    return runtime,api,flags,calls,fire
end
local function unchanged(calls)
    eq(calls.writes,0)
    local raw=testfs_read("FixtureDogs/"..S.WORLD.."/slot-a.json")
    local snapshot=assert(require("B47Dog/Snapshot").open(raw,S.WORLD,"fixture-save"))
    local record=snapshot.payload.records[S.DOG]
    eq(record.ownership.ownerAccount,"Alice");eq(record.ownership.revision,3)
    eq(record.privateHistory.retained,"HIDDEN_FIXTURE");eq(record.admission,nil)
end
for _,route in ipairs({"world_load","save_load","chunk_reentry","reconnect","admin_spawn","privileged_action","inspect"}) do
    test("matching carrier stays quarantined through "..route,function()
        local runtime,api,flags,calls=fixture()
        local result=runtime.assessAdmission(flags.animals[1],route)
        eq(result.decision,"QUARANTINE");eq(result.reason,"NativeProvenanceUnverified")
        eq(result.dogId,S.DOG);eq(result.bindingVerified,false);unchanged(calls)
    end)
end
for _,route in ipairs({"inventory_release","trailer_release","vehicle_load","hutch_release","growth","death"}) do
    test("live carrier cannot authorize unsupported "..route,function()
        local runtime,api,flags,calls=fixture()
        local result=runtime.assessAdmission(flags.animals[1],route)
        eq(result.decision,"REJECT");eq(result.reason,"ManagedTransitionUnsupported");unchanged(calls)
    end)
end
test("copy first never wins and later original cannot clear conflict",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local clone=S.animal();local original=S.animal()
    eq(runtime.assessAdmission(clone,"world_load").decision,"QUARANTINE")
    eq(runtime.assessAdmission(original,"world_load").decision,"REJECT")
    eq(runtime.assessAdmission(clone,"world_load").decision,"REJECT");unchanged(calls)
end)
test("forged token fails without changing the canonical owner",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local animal,data=S.animal();data.FixtureDogs.bindingToken=S.LATER
    local result=runtime.assessAdmission(animal,"world_load")
    eq(result.decision,"REJECT");eq(result.reason,"IdentityConflict");unchanged(calls)
end)
test("earlier world generation does not select the private dog ID",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local animal,data=S.animal();data.FixtureDogs.worldId=S.LATER
    local result=runtime.assessAdmission(animal,"save_load")
    eq(result.decision,"REJECT");eq(result.reason,"ForeignWorld");eq(result.dogId,nil);unchanged(calls)
end)
test("unknown private dog marker cannot invent a canonical record",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local animal,data=S.animal();data.FixtureDogs.dogId=S.LATER
    local result=runtime.assessAdmission(animal,"world_load")
    eq(result.decision,"REJECT");eq(result.reason,"MissingPrivateRecord");eq(result.dogId,nil);unchanged(calls)
end)
test("unregistered animal remains separate from an orphan candidate",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local animal,data=S.animal();data.FixtureDogs=nil
    local result=runtime.assessAdmission(animal,"admin_spawn")
    eq(result.decision,"REJECT");eq(result.reason,"UnregisteredCarrier");eq(result.dogId,nil)
    local census=assert(runtime.census());eq(census.retained,1);eq(census.dogId,S.DOG)
    eq(runtime.assessAdmission(nil,"world_load").decision,"DEFER");unchanged(calls)
end)
test("repeated requests remain diagnostic with no write or allocation",function()
    local runtime,api,flags,calls=fixture()
    for _=1,20 do eq(runtime.assessAdmission(flags.animals[1],"inspect").decision,"QUARANTINE") end
    unchanged(calls)
end)
test("native integer collision cannot authenticate a copied carrier",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.animals={} end)
    local animal,_,observation=S.animal();observation.nativeId=2147483647
    eq(runtime.assessAdmission(animal,"save_load").decision,"QUARANTINE");unchanged(calls)
end)
test("same handle unload/reload defers and remains unverified",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1]
    animal.exists=false;flags.animals={}
    eq(runtime.assessAdmission(animal,"chunk_reentry").decision,"DEFER")
    eq(runtime.census().retained,1)
    animal.exists=true;flags.animals={animal}
    eq(runtime.assessAdmission(animal,"chunk_reentry").decision,"QUARANTINE");unchanged(calls)
end)
test("new handle after unload cannot inherit admission",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1]
    animal.exists=false;eq(runtime.assessAdmission(animal,"chunk_reentry").decision,"DEFER")
    eq(runtime.assessAdmission(S.animal(),"chunk_reentry").decision,"REJECT");unchanged(calls)
end)
test("simulated growth replacement loses authority even if integer survives",function()
    local runtime,api,flags,calls=fixture();local grown,data=S.animal()
    data.FixtureDogs=nil
    eq(runtime.assessAdmission(grown,"growth").decision,"REJECT");unchanged(calls)
end)
test("death and attempted live return do not revive session authority",function()
    local runtime,api,flags,calls,fire=fixture();local animal=flags.animals[1]
    animal.dead=true;fire("OnCharacterDeath",animal)
    eq(runtime.assessAdmission(animal,"death").reason,"KnownDead")
    animal.dead=false;eq(runtime.assessAdmission(animal,"world_load").decision,"REJECT");unchanged(calls)
end)
test("previous-session native checkpoint mismatch quarantines",function()
    local runtime,api,flags,calls=fixture(function(_,f) f.anchor.checkpoint=S.NEXT end)
    eq(runtime.assessAdmission(S.animal(),"save_load").reason,"PrivateRecoveryUnavailable");unchanged(calls)
end)
test("private-only prepared save is preserved and never admitted",function()
    local runtime,api,flags,calls=fixture(function(a,_,c)
        local store=assert(Store.open(assert(Cache.new("FixtureDogs",S.WORLD,a)),S.pair()))
        local payload=store.read().payload
        payload.records[S.DOG].ownership.name="Prepared private fixture"
        payload.records[S.DOG].ownership.revision=4
        assert(store.prepare(payload,S.NEXT,1));c.writes=0
    end)
    local before=testfs_read("FixtureDogs/"..S.WORLD.."/slot-b.json")
    eq(runtime.assessAdmission(S.animal(),"save_load").decision,"QUARANTINE")
    eq(testfs_read("FixtureDogs/"..S.WORLD.."/slot-b.json"),before);unchanged(calls)
end)
test("interrupted private save is preserved without repair",function()
    local broken="interrupted fixture bytes"
    local runtime,api,flags,calls=fixture(function() testfs_write("FixtureDogs/"..S.WORLD.."/slot-b.json",broken) end)
    eq(runtime.assessAdmission(S.animal(),"save_load").decision,"QUARANTINE")
    eq(testfs_read("FixtureDogs/"..S.WORLD.."/slot-b.json"),broken);unchanged(calls)
end)
test("coordinated paired backup rollback is not prior-session proof",function()
    local runtime,api,flags,calls=fixture(function(a,f,c)
        local aPath="FixtureDogs/"..S.WORLD.."/slot-a.json"
        local bPath="FixtureDogs/"..S.WORLD.."/slot-b.json"
        local oldA,oldB=testfs_read(aPath),testfs_read(bPath)
        local store=assert(Store.open(assert(Cache.new("FixtureDogs",S.WORLD,a)),S.pair()))
        local payload=store.read().payload;payload.records[S.DOG].ownership.name="Later fixture"
        payload.records[S.DOG].ownership.revision=4;assert(store.prepare(payload,S.NEXT,1))
        f.anchor.checkpoint=S.NEXT
        testfs_write(aPath,oldA);testfs_write(bPath,oldB);f.anchor.checkpoint=S.FIRST;c.writes=0
    end)
    eq(runtime.status().phase,"RECOVERED")
    eq(runtime.assessAdmission(flags.animals[1],"save_load").decision,"QUARANTINE");unchanged(calls)
end)
test("reentrant admission defers before reading or changing registry again",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData();local nested
    animal.getModData=function()
        nested=runtime.assessAdmission(animal,"inspect");return data
    end
    eq(runtime.assessAdmission(animal,"inspect").decision,"QUARANTINE")
    eq(nested.decision,"DEFER");eq(nested.reason,"AdmissionBusy");unchanged(calls)
end)
test("anchor drift during native inspection quarantines before result",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData()
    animal.getModData=function() flags.anchor.checkpoint=S.NEXT;return data end
    eq(runtime.assessAdmission(animal,"inspect").reason,"AnchorChanged")
    eq(runtime.status().phase,"RECOVERY");unchanged(calls)
end)
test("guard drift during native inspection quarantines before result",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData()
    animal.getModData=function() api.ISPickupAnimal.complete=function() end;return data end
    eq(runtime.assessAdmission(animal,"inspect").reason,"GuardIntegrityUnavailable");unchanged(calls)
end)
test("reentrant census refuses without poisoning the outer diagnostic",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData()
    local nested,why
    animal.getModData=function() nested,why=runtime.census();return data end
    local census=assert(runtime.census())
    eq(nested,nil);eq(why,"Busy");eq(census.admission.QUARANTINE,1)
    eq(runtime.status().phase,"RECOVERED");unchanged(calls)
end)
test("admission requested during census defers before a second read",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData();local nested
    animal.getModData=function() nested=runtime.assessAdmission(animal,"inspect");return data end
    eq(runtime.census().admission.ADMIT,0);eq(nested.reason,"AdmissionBusy");unchanged(calls)
end)
test("census cannot return a result after getter changes the loaded anchor",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1];local data=animal:getModData()
    animal.getModData=function() flags.anchor.checkpoint=S.NEXT;return data end
    local result,why=runtime.census()
    eq(result,nil);eq(why,"AnchorChanged");eq(runtime.status().phase,"RECOVERY");unchanged(calls)
end)
test("unknown route rejects before native reads",function()
    local runtime,api,flags,calls=fixture();local animal=flags.animals[1]
    animal.getModData=function() error("must not read malformed route") end
    eq(runtime.assessAdmission(animal,{bindingVerified=true}).reason,"UnsupportedRoute");unchanged(calls)
end)
test("unauthorized process cannot read private admission results",function()
    local runtime,api,flags,calls=fixture();flags.client=true
    local result=runtime.assessAdmission(flags.animals[1],"inspect")
    eq(result.decision,"REJECT");eq(result.reason,"AuthorityUnavailable");eq(result.dogId,nil);unchanged(calls)
end)
test("managed census classifies while unrelated vanilla animals stay outside counts",function()
    local runtime,api,flags,calls=fixture();local valid=flags.animals[1]
    local unregistered,data=S.animal();data.FixtureDogs=nil
    local foreign=S.animal();foreign.getAnimalType=function() return "VanillaRaccoon" end
    local wrongBreed=S.animal();wrongBreed.getBreed=function() return {getName=function() return "OtherBreed" end} end
    flags.animals={valid,unregistered,foreign,wrongBreed}
    local result=assert(runtime.census())
    eq(result.admission.ADMIT,0);eq(result.admission.QUARANTINE,1);eq(result.admission.REJECT,2)
    eq(result.admission.DEFER,0);unchanged(calls)
end)
test("actual admin test broker returns counts without private owner/history",function()
    S.seed();local api,flags,calls,fire,config,player=F.fixture("FixtureDogs")
    flags.anchor={schema=1,worldId=S.WORLD,checkpoint=S.FIRST};flags.animals={S.animal()}
    local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData");fire("OnServerStarted")
    local broker=assert(Service.new(config,runtime,api))
    local reply=broker.handle(player,"Inspect",{protocol=1})
    eq(reply.status,"Loaded");eq(reply.admission.ADMIT,0);eq(reply.admission.QUARANTINE,1)
    local encoded=assert(Codec.encode(reply));assert(not encoded:find("HIDDEN_FIXTURE",1,true))
    assert(not encoded:find("ownerAccount",1,true));unchanged(calls)
end)
test("network broker has no admit endpoint and unauthorized requests are silent",function()
    local api,flags,calls,fire,config,player=F.fixture()
    local runtime=assert(Runtime.install({namespace=config.namespace,allowedTypes={[config.nativeType]={[config.breed]=true}}},api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    local broker=assert(Service.new(config,runtime,api));flags.allowed=false
    eq(broker.handle(player,"Inspect",{protocol=1}),nil)
    eq(broker.handle(player,"Admit",{protocol=1,bindingVerified=true}),nil)
    flags.allowed=true;eq(broker.handle(player,"Admit",{protocol=1}).status,"Invalid")
    eq(calls.writes,0);eq(calls.spawns,0)
end)
return {passed=passed,failed=failed,failures=failures}
