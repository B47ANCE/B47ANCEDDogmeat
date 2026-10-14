local S=require "storage_support"
local P=require "pairing_support"
local Codec=require "B47Dog/Codec"
local Identity=require "B47Dog/Identity"
local Runtime=require "B47Dog/NativeRuntime"
local passed,failed,failures=0,0,{}
local function equal(actual,expected) assert(actual==expected,tostring(actual).." ~= "..tostring(expected)) end
local function test(name,fn)
    local ok,err=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(err) end
end
local function recovered()
    S.seed();local api,flags,calls,fire,callbacks=P.fixture()
    flags.server=false;api.B47DogSinglePlayer=true
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData",false);fire("OnGameStart")
    equal(runtime.status().phase,"RECOVERED")
    return runtime,api,flags,calls,fire,callbacks
end

test("event installation reads nothing until native load; no implicit initialization",function()
    local api,flags,calls,fire,callbacks=P.fixture()
    flags.anchor=nil
    local runtime=assert(Runtime.install(P.config(),api))
    equal(runtime.status().phase,"WAITING_NATIVE_LOAD");equal(calls.modReads,0);equal(calls.reads,0)
    equal(#callbacks.OnInitGlobalModData,1);equal(#callbacks.OnServerStarted,1);equal(#callbacks.OnCharacterDeath,1)
    equal(#callbacks.OnSave,0);equal(#callbacks.OnPostSave,0);equal(#callbacks.OnReceiveGlobalModData,0)
    fire("OnInitGlobalModData",true)
    equal(runtime.status().reason,"MissingAnchor");equal(calls.writes,0);equal(flags.anchor,nil)
end)

for _,bad in ipairs({"future","privateField","foreignWorld","unknownCheckpoint","badUuid","missing"}) do
    test("invalid loaded native anchor preserves files "..bad,function()
        S.seed();local api,flags,calls,fire=P.fixture()
        if bad=="future" then flags.anchor.schema=2
        elseif bad=="privateField" then flags.anchor.ownerAccount="Alice"
        elseif bad=="foreignWorld" then flags.anchor.worldId=S.LATER
        elseif bad=="unknownCheckpoint" then flags.anchor.checkpoint=S.LATER
        elseif bad=="badUuid" then flags.anchor.checkpoint="../../invalid"
        else flags.anchor=nil end
        local before=Codec.encode(flags.anchor or {})
        local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData",true)
        equal(runtime.status().phase,"RECOVERY");equal(calls.writes,0);equal(Codec.encode(flags.anchor or {}),before)
    end)
end

test("loaded exact anchor recovers and startup census uses current native handles",function()
    local runtime,api,flags,calls,fire=recovered()
    equal(calls.census,1);equal(calls.censusReads,1);equal(calls.writes,0)
    equal(runtime.observe(flags.animals[1]).status,"MATCHED")
    fire("OnServerStarted");equal(calls.census,1)
    local census=runtime.census();equal(census.status,"OBSERVED_LOADED_ONLY")
    equal(census.dogs[S.DOG],"MATCHED");equal(calls.census,2)
end)

test("prepared file publishes only nonsecret checkpoint and remains pending",function()
    local runtime,api,flags,calls,fire,callbacks=recovered();local ctx,intent=P.request()
    local result=assert(runtime.prepareOwnership(flags.animals[1],ctx,intent))
    equal(result.status,"WAITING_NATIVE_RELOAD");equal(runtime.status().phase,"WAITING_NATIVE_RELOAD")
    equal(flags.anchor.checkpoint,S.NEXT);equal(calls.writes,1)
    equal(Codec.encode(flags.anchor),Codec.encode({schema=1,worldId=S.WORLD,checkpoint=S.NEXT}))
    fire("OnSave");fire("OnPostSave");fire("OnInitGlobalModData",false);fire("OnServerStarted")
    equal(runtime.status().phase,"WAITING_NATIVE_RELOAD")
    equal(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil);equal(calls.writes,1)
end)

test("client receive payload never installs a native anchor",function()
    local runtime,api,flags,calls,fire=recovered()
    local original=flags.anchor;local before=Codec.encode(original)
    fire("OnReceiveGlobalModData","FixtureDogs",{schema=1,worldId=S.WORLD,checkpoint=S.NEXT})
    equal(flags.anchor,original);equal(Codec.encode(flags.anchor),before)
    equal(runtime.status().phase,"RECOVERED");equal(calls.writes,0)
end)

for _,change in ipairs({"replacedTable","checkpoint","world","save","client","server"}) do
    test("anchor or role drift refuses before private writes "..change,function()
        local runtime,api,flags,calls=recovered();local ctx,intent=P.request()
        if change=="replacedTable" then flags.anchor=S.copy(flags.anchor)
        elseif change=="checkpoint" then flags.anchor.checkpoint=S.LATER
        elseif change=="world" then flags.anchor.worldId=S.LATER
        elseif change=="save" then flags.locator="different-save"
        elseif change=="client" then flags.client=true else flags.server=true end
        equal(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil);equal(calls.writes,0)
    end)
end

test("anchor mutation during preparation cannot publish or discard prepared data",function()
    local runtime,api,flags,calls=recovered();local ctx,intent=P.request()
    api.getRandomUUID=function() flags.anchor.checkpoint=S.LATER;return S.NEXT end
    equal(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil)
    equal(runtime.status().reason,"AnchorChanged");equal(flags.anchor.checkpoint,S.LATER);equal(calls.writes,1)
end)

for _,failure in ipairs({"partialWrite","swallowWrite","writeFailure","writerCloseFailure"}) do
    test("failed private preparation never advances native anchor "..failure,function()
        local runtime,api,flags,calls=recovered();local ctx,intent=P.request();flags[failure]=true
        equal(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil)
        equal(flags.anchor.checkpoint,S.FIRST);equal(runtime.status().phase,"RECOVERY")
        equal(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil);equal(calls.writes,1)
    end)
end

test("same handle survives detachment and full revalidation without new identity",function()
    local runtime,api,flags,calls=recovered();local animal=flags.animals[1]
    animal.exists=false;equal(runtime.observe(animal).status,"DETACHED_PENDING")
    local ctx,intent=P.request();equal(runtime.prepareOwnership(animal,ctx,intent),nil);equal(calls.writes,0)
    animal.exists=true;equal(runtime.observe(animal).status,"MATCHED")
    equal(runtime.observe(animal).dogId,S.DOG)
end)

test("new handle after detachment still quarantines both observed representations",function()
    local runtime,api,flags,calls=recovered();local old=flags.animals[1]
    old.exists=false;equal(runtime.observe(old).status,"DETACHED_PENDING")
    equal(runtime.observe(S.animal()).status,"QUARANTINED")
    old.exists=true;equal(runtime.observe(old).status,"QUARANTINED");equal(calls.writes,0)
end)

test("native death is rechecked, idempotent and sticky even when detached",function()
    local runtime,api,flags,calls,fire=recovered();local animal=flags.animals[1]
    fire("OnCharacterDeath",animal);equal(runtime.observe(animal).status,"MATCHED")
    animal.exists=false;animal.dead=true
    fire("OnCharacterDeath",animal);fire("OnCharacterDeath",animal)
    equal(runtime.observe(animal).status,"KNOWN_DEAD")
    animal.exists=true;animal.dead=false;equal(runtime.observe(animal).status,"KNOWN_DEAD")
    local ctx,intent=P.request();equal(runtime.prepareOwnership(animal,ctx,intent),nil);equal(calls.writes,0)
end)

test("death event cannot bind unknown living animal",function()
    S.seed();local api,flags,calls,fire=P.fixture();flags.animals={}
    local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData",false);fire("OnServerStarted")
    local animal=S.animal();fire("OnCharacterDeath",animal)
    animal.dead=true;equal(runtime.observe(animal).status,"UNBOUND");equal(calls.writes,0)
end)

test("duplicate census results reflect final quarantine, never an earlier match",function()
    S.seed();local api,flags,calls,fire=P.fixture();flags.animals={S.animal(),(S.animal())}
    local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData",false);fire("OnServerStarted")
    local result=assert(runtime.census());equal(result.dogs[S.DOG],"QUARANTINED");equal(calls.writes,0)
end)

for _,failure in ipairs({"large","missingCell","fractional"}) do
    test("unavailable or oversized census blocks preparation "..failure,function()
        S.seed();local api,flags,calls,fire=P.fixture()
        if failure=="large" then flags.animalCount=1025
        elseif failure=="fractional" then flags.animalCount=0.5 else flags.missingCell=true end
        local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData",false);fire("OnServerStarted")
        equal(runtime.status().reason,"CensusUnavailable");equal(calls.censusReads,0);equal(calls.writes,0)
    end)
end

test("duplicate installation and partial registration cannot accumulate callbacks",function()
    local api,flags,calls,fire,callbacks=P.fixture()
    assert(Runtime.install(P.config(),api));equal(Runtime.install(P.config(),api),nil)
    equal(#callbacks.OnInitGlobalModData,1)
    local other,otherFlags,_,otherFire,otherCallbacks=P.fixture();otherFlags.registrationFailure="OnServerStarted"
    equal(Runtime.install(P.config(),other),nil);equal(Runtime.install(P.config(),other),nil)
    equal(#otherCallbacks.OnInitGlobalModData,1);otherFire("OnInitGlobalModData",true)
    equal(otherFlags.anchor.checkpoint,S.FIRST)
end)

test("late native load cannot recover after server already started",function()
    S.seed();local api,flags,calls,fire=P.fixture();local runtime=assert(Runtime.install(P.config(),api))
    fire("OnServerStarted");fire("OnInitGlobalModData",false)
    equal(runtime.status().phase,"RECOVERY");equal(runtime.status().reason,"NativeLoadNotObserved")
    equal(calls.reads,0);equal(calls.writes,0)
end)

test("client or unavailable events refuse installation",function()
    local api,flags=P.fixture();flags.client=true;equal(Runtime.install(P.config(),api),nil)
    flags.client=false;api.Events.OnCharacterDeath=nil;equal(Runtime.install(P.config(),api),nil)
end)

test("invalid native booleans cannot manufacture death or legitimate detachment",function()
    for _,field in ipairs({"dead","exists"}) do
        local runtime,api,flags,calls=recovered();local animal=flags.animals[1]
        animal[field]=nil
        equal(runtime.observe(animal).status,"QUARANTINED")
        animal[field]=field=="exists"
        equal(runtime.observe(animal).status,"QUARANTINED");equal(calls.writes,0)
    end
end)

return {passed=passed,failed=failed,failures=failures}
