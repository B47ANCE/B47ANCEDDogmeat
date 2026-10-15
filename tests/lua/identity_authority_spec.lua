-- Adversarial fixtures for the authority boundary, not a native packet exploit.
local Session=require "B47Dog/NativeSession"
local Runtime=require "B47Dog/NativeRuntime"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
local S=require "storage_support"
local P=require "pairing_support"
local F=require "provision_support"
local Service=require "B47Dog/NativeTestService"
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,why=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(why) end
end
local function eq(a,b) assert(a==b,"expected "..tostring(b)..", got "..tostring(a)) end
local function open(api)
    return assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
        allowedTypes={FixtureCanine={FixtureShepherd=true}}},api))
end
local function unchanged(api,calls,original)
    eq(calls.writes,0)
    local cache=assert(Cache.new("FixtureDogs",S.WORLD,api))
    eq(cache.read("a"),original);eq(cache.read("b"),original)
    local record=assert(Store.open(cache,S.pair())).read().payload.records[S.DOG]
    eq(record.ownership.ownerAccount,"Alice")
    eq(record.privateHistory.retained,"HIDDEN_FIXTURE")
end

for _,attack in ipairs({"transplanted","highNativeId","erased","foreign","duplicate","dead","detached"}) do
    test("private identity survives "..attack.." without ownership admission",function()
        S.seed();local api,flags,calls=S.api();local session=open(api)
        local cache=assert(Cache.new("FixtureDogs",S.WORLD,api));local original=cache.read("a")
        local animal,data,observation=S.animal()
        -- For transplanted/highNativeId only the alleged replacement is visible.
        if attack=="highNativeId" then observation.nativeId=2147483647 end
        if attack=="erased" then data.FixtureDogs=nil end
        if attack=="foreign" then data.FixtureDogs.dogId=S.LATER end
        if attack=="duplicate" then session.observe(S.animal()) end
        if attack=="dead" then animal.dead=true end
        if attack=="detached" then animal.exists=false end
        local observed=session.observe(animal)
        eq(observed.bindingVerified,false)
        if attack=="transplanted" or attack=="highNativeId" then eq(observed.status,"MATCHED") end
        local summary=session.identitySummary()
        eq(summary.retained,1);eq(summary.dogId,S.DOG);eq(summary.bindingVerified,false)
        eq(summary.ownerAccount,nil);eq(summary.privateHistory,nil)
        -- Caller-supplied trust assertions cannot override the native MP fence.
        local context,intent=P.request();context.bindingVerified=true;context.storeRecovered=true
        local result,reason=session.prepareOwnership(animal,context,intent)
        eq(result,nil);eq(reason,"UntrustedNativeMarker")
        unchanged(api,calls,original)
    end)
end

test("summary mutation cannot change private records",function()
    S.seed();local api=S.api();local session=open(api)
    local summary=session.identitySummary();summary.dogId=S.LATER;summary.retained=0;summary.bindingVerified=true
    local again=session.identitySummary()
    eq(again.dogId,S.DOG);eq(again.retained,1);eq(again.bindingVerified,false)
end)

test("empty loaded census still reports retained identity",function()
    S.seed();local api,flags,calls,fire=P.fixture();flags.animals={}
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    local census=assert(runtime.census())
    eq(census.animalsRead,0);eq(next(census.dogs),nil)
    eq(census.retained,1);eq(census.dogId,S.DOG);eq(census.bindingVerified,false);eq(calls.writes,0)
end)

test("carrier unload removes census matches without losing private identity",function()
    S.seed();local api,flags,calls,fire=P.fixture()
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    eq(runtime.census().dogs[S.DOG],"MATCHED")
    flags.animals={}
    local census=assert(runtime.census())
    eq(census.animalsRead,0);eq(next(census.dogs),nil)
    eq(census.retained,1);eq(census.dogId,S.DOG);eq(census.bindingVerified,false);eq(calls.writes,0)
end)

test("new recovery session cannot turn lost quarantine into permission",function()
    S.seed();local api,_,calls=S.api();local first=open(api)
    first.observe(S.animal());eq(first.observe(S.animal()).status,"QUARANTINED")
    local nextSession=open(api);local clone=S.animal()
    local observed=nextSession.observe(clone)
    eq(observed.status,"MATCHED");eq(observed.bindingVerified,false)
    local context,intent=P.request()
    eq(nextSession.prepareOwnership(clone,context,intent),nil);eq(calls.writes,0)
    eq(nextSession.identitySummary().dogId,S.DOG)
end)

test("diagnostic broker takes identity from private recovery, not observed marker IDs",function()
    local api,flags,_,_,config,player=F.fixture("IdentityDiagnosticFixture")
    local fakeRuntime={status=function() return {phase="RECOVERED",serverStarted=true} end,
        census=function() return {dogs={[S.LATER]="MATCHED"},retained=1,dogId=S.DOG,bindingVerified=false} end}
    local result=assert(Service.new(config,fakeRuntime,api)).handle(player,"Inspect",{protocol=1})
    eq(result.dogId,S.DOG);eq(result.retained,1);eq(result.matched,1);eq(result.bindingVerified,false)
    flags.allowed=false
    eq(assert(Service.new(config,fakeRuntime,api)).handle(player,"Inspect",{protocol=1}),nil)
end)

test("ambiguous retained roster has no arbitrary single ID",function()
    local Snapshot=require "B47Dog/Snapshot"
    local meta,payload=S.fixture();local other=S.copy(payload.records[S.DOG])
    other.ownership.dogId=S.LATER;payload.records[S.LATER]=other
    local bytes=assert(Snapshot.seal(meta,payload))
    for _,slot in ipairs({"a","b"}) do testfs_write("FixtureDogs/"..S.WORLD.."/slot-"..slot..".json",bytes) end
    local api=S.api();local summary=open(api).identitySummary()
    eq(summary.retained,2);eq(summary.dogId,nil);eq(summary.bindingVerified,false)
end)
return {passed=passed,failed=failed,failures=failures}
