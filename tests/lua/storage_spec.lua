local Codec=require "B47Dog/Codec"
local Snapshot=require "B47Dog/Snapshot"
local Store=require "B47Dog/PrivateStore"
local Identity=require "B47Dog/Identity"
local PZCache=require "B47Dog/PZCache"
local Native=require "B47Dog/NativeAnimal"
local S=require "storage_support"
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,message=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1; failures[#failures+1]=name..": "..tostring(message) end
end
local function equal(a,b) assert(a==b,"expected "..tostring(b)..", got "..tostring(a)) end
local function refused(value,reason,wanted) equal(value,nil); equal(reason,wanted) end

test("canonical Unicode JSON is ASCII and roundtrips literal data",function()
    local value={z=false,a="Éclair 🐕\n\0\\\"",nested={negative=-17,zero=0}}
    local bytes=assert(Codec.encode(value)); assert(not bytes:find("[\128-\255]"))
    equal(Codec.encode(assert(Codec.decode(bytes))),bytes)
    equal(Codec.decode(bytes).a,value.a)
    equal(Codec.encode({b=1,a=2}),'{"a":2,"b":1}')
    equal(Codec.checksum("Wikipedia"),"11e60398")
end)

for _,bytes in ipairs({'{"a":1,"a":2}','{"b":1,"a":2}','{"a":null}','[1,2]',
    '{"a":1.5}','{"a":1e2}','{"a":2147483648}','{"a":-2147483648}',
    '{"a":01}','{"a":-0}','{"a":1} trailing',' {"a":1}',
    '{"a":"\\ud800"}','{"a":"\\udc00"}','{"a":"\\ud800\\u0041"}',
    '{"a":"\\uZZZZ"}','{"a":"\n"}','{"a":"é"}','{"a":false,}','{"a":',
    string.rep('{"a":',18)..'0'..string.rep('}',18)}) do
    test("malformed/noncanonical JSON refused "..#bytes,function() equal(Codec.decode(bytes),nil) end)
end

test("cycles, floats, invalid UTF8 and excessive strings refused",function()
    local cycle={};cycle.self=cycle
    for _,value in ipairs({cycle,{a=0/0},{a=math.huge},{a=1.5},{a=string.char(192,175)},
        {a=string.rep("x",Codec.MAX_STRING+1)},setmetatable({},{})}) do equal(Codec.encode(value),nil) end
    equal(Codec.decode(string.rep("x",Codec.MAX_BYTES+1)),nil)
end)

test("ownership and hidden data roundtrip without projection",function()
    local meta,payload=S.fixture(); local bytes=assert(Snapshot.seal(meta,payload))
    local loaded=assert(Snapshot.open(bytes,S.WORLD,"fixture-save"))
    equal(loaded.payload.records[S.DOG].ownership.name,"Éclair 🐕")
    equal(loaded.payload.records[S.DOG].privateHistory.retained,"HIDDEN_FIXTURE")
    equal(loaded.meta.recordCount,1); equal(loaded.meta.payloadBytes,#Codec.encode(payload))
end)

for _,field in ipairs({"sequence","checkpoint","previous","recordCount","payloadBytes","payloadChecksum"}) do
    test("metadata corruption detected "..field,function()
        local meta,payload=S.fixture(); local doc=Codec.decode(Snapshot.seal(meta,payload))
        doc.body[field]=type(doc.body[field])=="number" and doc.body[field]+1 or "altered"
        equal(Snapshot.open(Codec.encode(doc),S.WORLD,"fixture-save"),nil)
    end)
end

test("future schema, extra fields and foreign store refused",function()
    local meta,payload=S.fixture(); local bytes=Snapshot.seal(meta,payload); local doc=Codec.decode(bytes)
    doc.schema=2; local v,r=Snapshot.open(Codec.encode(doc),S.WORLD,"fixture-save"); refused(v,r,"FutureSchema")
    doc.schema=1; doc.extra=true; equal(Snapshot.open(Codec.encode(doc),S.WORLD,"fixture-save"),nil)
    v,r=Snapshot.open(bytes,S.WORLD,"other-save"); refused(v,r,"ForeignStore")
    v,r=Snapshot.open(bytes,S.NEXT,"fixture-save"); refused(v,r,"ForeignStore")
end)

test("ownership world, ID and generation mismatch cannot be sealed",function()
    for _,field in ipairs({"worldId","dogId","generation"}) do
        local meta,payload=S.fixture(); payload.records[S.DOG].ownership[field]=field=="generation" and 2 or S.NEXT
        equal(Snapshot.seal(meta,payload),nil)
    end
end)

test("exact paired checkpoint selects and returns detached copies",function()
    local io,files=S.memory(); local session=assert(Store.open(io,S.pair()))
    local loaded=session.read(); loaded.payload.records[S.DOG].ownership.name="changed"
    equal(session.read().payload.records[S.DOG].ownership.name,"Éclair 🐕")
    local v,r=Store.open(io,S.pair(S.NEXT)); refused(v,r,"Unpaired")
    equal(files.a,files.b)
end)

test("prepare changes only inactive slot and requires new pairing",function()
    local io,files,calls,payload=S.memory(); local original=files.a
    local session=assert(Store.open(io,S.pair())); payload.records[S.DOG].ownership.name="Rex"; payload.records[S.DOG].ownership.revision=4
    local prepared=assert(session.prepare(payload,S.NEXT,1))
    equal(prepared.status,"PREPARED_READBACK"); equal(calls.writes,1); equal(files.a,original)
    equal(session.read().payload.records[S.DOG].ownership.name,"Éclair 🐕")
    local v,r=session.prepare(payload,S.LATER,1); refused(v,r,"Recovery")
    v,r=Store.open(io,S.pair()); refused(v,r,"PreparedPending")
    local reopened=assert(Store.open(io,S.pair(S.NEXT)))
    equal(reopened.read().payload.records[S.DOG].ownership.name,"Rex")
end)

for _,mutation in ipairs({"missing","truncated","future","unrelated","sameCheckpointDifferentData"}) do
    test("ambiguous slot preserved "..mutation,function()
        local io,files,calls=S.memory()
        if mutation=="missing" then files.b=nil
        elseif mutation=="truncated" then files.b=files.b:sub(1,100)
        elseif mutation=="future" then local doc=Codec.decode(files.b);doc.schema=2;files.b=Codec.encode(doc)
        else
            local meta,payload=S.fixture()
            if mutation=="unrelated" then meta.checkpoint=S.LATER else payload.records[S.DOG].ownership.name="Changed" end
            files.b=Snapshot.seal(meta,payload)
        end
        local before=files.b; equal(Store.open(io,S.pair()),nil); equal(files.b,before); equal(calls.writes,0)
    end)
end

test("both missing never initializes",function()
    local io,files,calls=S.memory();files.a=nil;files.b=nil
    equal(Store.open(io,S.pair()),nil);equal(calls.writes,0)
end)

test("disk changes invalidate session before overwrite",function()
    local io,files,calls,payload=S.memory(); local session=Store.open(io,S.pair())
    files.b="changed externally"
    local v,r=session.prepare(payload,S.NEXT,1);refused(v,r,"ChangedOnDisk");equal(calls.writes,0)
end)

test("partial write preserves current slot and locks retry",function()
    local io,files,calls,payload=S.memory(); local old=files.a
    io.write=function(slot,bytes) calls.writes=calls.writes+1;files[slot]=bytes:sub(1,100);return true end
    local session=Store.open(io,S.pair());local v,r=session.prepare(payload,S.NEXT,1)
    refused(v,r,"ReadbackFailed");equal(files.a,old)
    equal(session.prepare(payload,S.LATER,1),nil);equal(calls.writes,1)
end)

test("no allocation rollback or checkpoint reuse",function()
    local io,files,calls,payload=S.memory();local session=Store.open(io,S.pair())
    equal(session.prepare(payload,S.NEXT,0),nil);equal(session.prepare(payload,S.FIRST,1),nil);equal(calls.writes,0)
end)

test("older binding token is independent of current store checkpoint",function()
    local meta,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    local obj={};equal(registry.observe(obj,S.observation()).status,"MATCHED")
    equal(S.observation().marker.bindingToken,S.BINDING_ID);assert(S.BINDING_ID~=meta.checkpoint)
end)

test("duplicate marker quarantines both references without picking first",function()
    local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    local first,second={},{}
    equal(registry.observe(first,S.observation()).status,"MATCHED")
    equal(registry.observe(second,S.observation()).status,"QUARANTINED")
    equal(registry.observe(first,S.observation()).status,"QUARANTINED");equal(registry.status(S.DOG),"QUARANTINED")
end)

for field,value in pairs({worldId=S.NEXT,bindingToken=S.NEXT,bindingGeneration=2,dogId=S.NEXT}) do
    test("foreign binding quarantined "..field,function()
        local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
        local observation=S.observation();observation.marker[field]=value
        equal(registry.observe({},observation).status,"QUARANTINED")
    end)
end

test("registry owns its record copy; native hint never proves identity",function()
    local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    payload.records[S.DOG].binding.acceptedTokens[S.NEXT]=true
    local obs=S.observation();obs.marker.bindingToken=S.NEXT;obs.nativeId=42
    equal(registry.observe({},obs).status,"QUARANTINED")
end)

test("native observation uses actual type test, role and narrow marker",function()
    local api,flags=S.api();local animal,data=S.animal()
    local reader=Native.new("FixtureDogs",{FixtureCanine={FixtureShepherd=true}},api)
    local before=Codec.encode(data);local observation=reader.observe(animal)
    equal(observation.status,"OBSERVED");equal(observation.unrelated,nil)
    observation.marker.dogId=S.NEXT;equal(data.FixtureDogs.dogId,S.DOG);equal(Codec.encode(data),before)
    flags.client=true;equal(reader.observe(animal).status,"Unavailable")
    flags.client=false;flags.server=false;equal(reader.observe(animal).status,"Unavailable")
    flags.server=true;animal.fixtureNative=false;equal(reader.observe(animal).status,"Unavailable")
end)

test("native missing/unknown/private marker fields never adopted",function()
    local api=S.api();local animal,data=S.animal();local reader=Native.new("FixtureDogs",{FixtureCanine={FixtureShepherd=true}},api)
    data.FixtureDogs.ownerAccount="Alice";equal(reader.observe(animal).status,"InvalidMarker")
    data.FixtureDogs=nil;equal(reader.observe(animal).status,"UNBOUND");equal(data.FixtureDogs,nil)
    animal.exists=false;equal(reader.observe(animal).status,"Detached")
end)

test("real temporary files exercise native adapter's calls and close paths",function()
    local payload=S.seed();local api,flags,calls=S.api();local io=PZCache.new("FixtureDogs",S.WORLD,api)
    local session=assert(Store.open(io,S.pair()));local original=io.read("a")
    payload.records[S.DOG].ownership.name="Persisted"; payload.records[S.DOG].ownership.revision=4
    equal(session.prepare(payload,S.NEXT,1).status,"PREPARED_READBACK")
    equal(io.read("a"),original);equal(calls.writes,1);equal(calls.writerClosed,1)
    local recovered=assert(Store.open(io,S.pair(S.NEXT)))
    equal(recovered.read().payload.records[S.DOG].ownership.name,"Persisted")
    equal(calls.reads,calls.readerClosed)
end)

for _,fault in ipairs({"partialWrite","swallowWrite","writeFailure","writerCloseFailure"}) do
    test("file adapter failure preserves previous slot "..fault,function()
        local payload=S.seed();local api,flags,calls=S.api();local io=PZCache.new("FixtureDogs",S.WORLD,api)
        local session=Store.open(io,S.pair());local original=io.read("a");flags[fault]=true
        equal(session.prepare(payload,S.NEXT,1),nil);equal(io.read("a"),original)
        equal(calls.writerClosed,1);equal(session.prepare(payload,S.LATER,1),nil);equal(calls.writes,1)
    end)
end

for _,fault in ipairs({"readFailure","readerCloseFailure"}) do
    test("reader closes on failure "..fault,function()
        S.seed();local api,flags,calls=S.api();local io=PZCache.new("FixtureDogs",S.WORLD,api)
        flags[fault]=true;equal(io.read("a"),nil);equal(calls.readerClosed,1);equal(calls.writes,0)
    end)
end

test("path traversal, client role, save switches and arbitrary slots refused",function()
    S.seed();local api,flags,calls=S.api()
    equal(PZCache.new("../bad",S.WORLD,api),nil);equal(PZCache.new("FixtureDogs","../../world",api),nil)
    flags.client=true;equal(PZCache.new("FixtureDogs",S.WORLD,api),nil);flags.client=false
    local io=PZCache.new("FixtureDogs",S.WORLD,api)
    equal(io.read("../a"),nil);equal(io.write("x","{}"),nil)
    flags.locator="other-save";equal(io.read("a"),nil);equal(io.write("a","{}"),nil);equal(calls.writes,0)
end)

test("extra lines and nil reader do not become empty stores",function()
    S.seed();local api,_,calls=S.api();local io=PZCache.new("FixtureDogs",S.WORLD,api)
    testfs_write("FixtureDogs/"..S.WORLD.."/slot-a.json","{}\n{}")
    equal(io.read("a"),nil);equal(calls.readerClosed,1)
    api.getFileReader=function() return nil end;equal(Store.open(io,S.pair()),nil);equal(calls.writes,0)
end)

for _,change in ipairs({"deleteRecord","dropHistory","lowerRevision","lowerGeneration","changePhase","extraRecord","rewriteLedger"}) do
    test("ownership preparation cannot smuggle retained-state change "..change,function()
        local io,files,calls,payload=S.memory()
        if change=="rewriteLedger" then
            local meta=S.fixture();payload.checkpointLedger={[S.FIRST]=true}
            files.a=Snapshot.seal(meta,payload);files.b=files.a
        end
        local session=Store.open(io,S.pair());local original=files.a
        if change=="deleteRecord" then payload.records[S.DOG]=nil
        elseif change=="dropHistory" then payload.records[S.DOG].privateHistory=nil
        elseif change=="lowerRevision" then payload.records[S.DOG].ownership.revision=2
        elseif change=="lowerGeneration" then payload.records[S.DOG].ownership.generation=0
        elseif change=="changePhase" then payload.records[S.DOG].ownership.phase="TERMINAL"
        elseif change=="extraRecord" then payload.records[S.NEXT]=S.copy(payload.records[S.DOG])
        else payload.checkpointLedger[S.FIRST]=false end
        equal(session.prepare(payload,S.NEXT,1),nil);equal(calls.writes,0);equal(files.a,original)
    end)
end

test("dead animal and refused observation revoke prior match",function()
    local api=S.api();local animal=S.animal();local reader=Native.new("FixtureDogs",{FixtureCanine={FixtureShepherd=true}},api)
    local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    equal(registry.observe(animal,reader.observe(animal)).status,"MATCHED")
    animal.dead=true;equal(reader.observe(animal).status,"Dead")
    equal(registry.observe(animal,reader.observe(animal)).status,"KNOWN_DEAD")
    local obs=S.observation();obs.status="Detached"
    equal(registry.observe({},obs).status,"UNBOUND")
end)

test("native read stops at configured bound before allocating a whole line",function()
    local api,_,calls=S.api();local io=PZCache.new("FixtureDogs",S.WORLD,api)
    testfs_write("FixtureDogs/"..S.WORLD.."/slot-a.json",string.rep("x",Codec.MAX_BYTES+100))
    equal(io.read("a"),nil);equal(calls.charactersRead,Codec.MAX_BYTES+1);equal(calls.readerClosed,1)
end)

test("native session prepares authenticated-context rename with private history",function()
    local Session=require "B47Dog/NativeSession"
    S.seed();local api,_,calls=S.api();local animal,data=S.animal()
    local session=assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
        allowedTypes={FixtureCanine={FixtureShepherd=true}}},api))
    local ctx={worldId=S.WORLD,sessionId="fixture-session",visible=true,reachable=true,ownershipEnabled=true,
        actor={accountId="Alice",episodeId="alice-1",connected=true,alive=true},
        config={revision=1,HandlerPermissionMode="OwnerAndGranted",OwnerAfterCharacterDeath="RetainAccountAccess"}}
    local intent={protocol=1,worldId=S.WORLD,sessionId="fixture-session",dogId=S.DOG,generation=1,
        revision=3,configRevision=1,action="RenameDog",name="Native fixture"}
    local before=Codec.encode(data)
    equal(session.prepareOwnership(animal,ctx,intent).status,"PREPARED_READBACK")
    equal(Codec.encode(data),before);equal(ctx.bindingVerified,nil);equal(calls.writes,1)
    local loaded=assert(Store.open(assert(PZCache.new("FixtureDogs",S.WORLD,api)),S.pair(S.NEXT))).read()
    equal(loaded.payload.records[S.DOG].ownership.name,"Native fixture")
    equal(loaded.payload.records[S.DOG].privateHistory.retained,"HIDDEN_FIXTURE")
    equal(loaded.payload.ownershipEvents[S.NEXT].event.actorAccount,"Alice")
    equal(data.FixtureDogs.ownerAccount,nil)
    equal(session.prepareOwnership(animal,ctx,intent),nil);equal(calls.writes,1)
end)

test("native session refuses death, duplicate and unauthenticated role before writes",function()
    local Session=require "B47Dog/NativeSession"
    for _,failure in ipairs({"dead","duplicate","notOwner"}) do
        S.seed();local api,_,calls=S.api();local animal=S.animal()
        local session=assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
            allowedTypes={FixtureCanine={FixtureShepherd=true}}},api))
        local ctx={worldId=S.WORLD,sessionId="fixture-session",visible=true,reachable=true,ownershipEnabled=true,
            actor={accountId=failure=="notOwner" and "Bob" or "Alice",episodeId="alice-1",connected=true,alive=true},
            config={revision=1,HandlerPermissionMode="OwnerAndGranted",OwnerAfterCharacterDeath="RetainAccountAccess"}}
        local intent={protocol=1,worldId=S.WORLD,sessionId="fixture-session",dogId=S.DOG,generation=1,
            revision=3,configRevision=1,action="RenameDog",name="Refused"}
        if failure=="dead" then animal.dead=true
        elseif failure=="duplicate" then session.observe(S.animal());session.observe(animal) end
        equal(session.prepareOwnership(animal,ctx,intent),nil);equal(calls.writes,0)
    end
end)

test("one handle cannot grow quarantine without a bound",function()
    local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    local handle={};local observation=S.observation()
    equal(registry.observe(handle,observation).status,"MATCHED")
    for i=1,1023 do
        observation.marker.dogId=string.format("%08x-0000-4000-8000-000000000000",i)
        equal(registry.observe(handle,observation).status,"QUARANTINED")
    end
    observation.marker.dogId=S.NEXT
    equal(registry.observe(handle,observation).status,"CAPACITY")
    equal(registry.observe(handle,S.observation()).status,"CAPACITY")
    equal(registry.status(S.DOG),"CAPACITY")
end)

test("exhausted handle capacity blocks the whole registry",function()
    local _,payload=S.fixture();local registry=Identity.newRegistry(S.WORLD,payload.records)
    local handle={};equal(registry.observe(handle,S.observation()).status,"MATCHED")
    for _=1,1023 do equal(registry.observe({},S.observation()).status,"QUARANTINED") end
    equal(registry.observe({},S.observation()).status,"CAPACITY")
    equal(registry.observe(handle,S.observation()).status,"CAPACITY")
end)

test("native reobservation refuses identity changes during preparation",function()
    local Session=require "B47Dog/NativeSession"
    for _,failure in ipairs({"death","marker"}) do
        S.seed();local api,_,calls=S.api();local animal,data=S.animal()
        api.getRandomUUID=function()
            if failure=="death" then animal.dead=true else data.FixtureDogs.dogId=S.LATER end
            return S.NEXT
        end
        local session=assert(Session.open({namespace="FixtureDogs",worldId=S.WORLD,pairing=S.pair(),
            allowedTypes={FixtureCanine={FixtureShepherd=true}}},api))
        local ctx={worldId=S.WORLD,sessionId="fixture-session",visible=true,reachable=true,ownershipEnabled=true,
            actor={accountId="Alice",episodeId="alice-1",connected=true,alive=true},
            config={revision=1,HandlerPermissionMode="OwnerAndGranted",OwnerAfterCharacterDeath="RetainAccountAccess"}}
        local intent={protocol=1,worldId=S.WORLD,sessionId="fixture-session",dogId=S.DOG,generation=1,
            revision=3,configRevision=1,action="RenameDog",name="Refused"}
        equal(session.prepareOwnership(animal,ctx,intent),nil);equal(calls.writes,0)
    end
end)

return {passed=passed,failed=failed,failures=failures}
