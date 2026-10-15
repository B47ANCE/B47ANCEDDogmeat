local A=require "admission_support"
local S=require "storage_support"
local P=require "pairing_support"
local F=require "provision_support"
local Admission=require "B47Dog/NativeAdmissionGuard"
local Runtime=require "B47Dog/NativeRuntime"
local Provision=require "B47Dog/NativeProvision"
local Session=require "B47Dog/NativeSession"
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,why=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(why) end
end
local function eq(a,b) assert(a==b,tostring(a).." ~= "..tostring(b)) end
local function fixture()
    local api,flags,calls=S.api()
    local guard=assert(Admission.install(P.config(),api))
    return api,flags,calls,guard
end
local function foreign()
    local animal=S.animal()
    animal.getAnimalType=function() return "VanillaRaccoon" end
    return animal
end
for _,name in ipairs(A.names) do
    test("refuse managed carrier before "..name,function()
        local api,flags,calls,guard=fixture()
        local animal,data=S.animal();animal.dead=true;animal.exists=false;data.FixtureDogs=nil
        eq(api[name].complete(A.action(name,animal)),false)
        eq(calls.actions[name],nil);eq(guard.check(),true);eq(calls.writes,0)
    end)
    test("delegate unrelated carrier once "..name,function()
        local api,flags,calls,guard=fixture()
        local action=A.action(name,foreign())
        eq(api[name].complete(action),true);eq(calls.actions[name],1);eq(guard.check(),true)
    end)
end
test("generic nonanimal items keep vanilla completion",function()
    local api,flags,calls=fixture()
    for _,name in ipairs({"ISDropWorldItemAction","ISDropVehicleItemAction"}) do
        eq(api[name].complete({item=A.item()}),true);eq(calls.actions[name],1)
    end
end)
test("native corpse trailer behavior is preserved",function()
    local api,flags,calls=fixture()
    for _,name in ipairs({"ISAddAnimalInTrailer","ISRemoveAnimalFromTrailer"}) do
        eq(api[name].complete({animal={fixtureCorpse=true}}),true);eq(calls.actions[name],1)
    end
end)
test("hutch integer animal keys are not bounded as list positions",function()
    local api,flags,calls=fixture()
    for _,key in ipairs({9999,2147483647}) do
        local action=A.action("ISHutchGrabAnimal",foreign());action.index=key
        action.hutch.getAnimal=function(_,index) eq(index,key);return action.animal end
        eq(api.ISHutchGrabAnimal.complete(action),true)
    end
    eq(calls.actions.ISHutchGrabAnimal,2)
end)
test("constructors retain identity and cached constructors see current completion",function()
    local api,flags,calls=S.api();local saved={}
    for _,name in ipairs(A.names) do saved[name]=api[name].new end
    local guard=assert(Admission.install(P.config(),api))
    for _,name in ipairs(A.names) do eq(api[name].new,saved[name]) end
    local action=saved.ISPickupAnimal(api.ISPickupAnimal,{fixturePlayer=true});action.animal=S.animal()
    eq(action:complete(),false);eq(calls.actions.ISPickupAnimal,nil)
end)
test("missing hook changes no completion and cannot be retried",function()
    local api=S.api();local before=api.ISPickupAnimal.complete
    local missing=api.ISDropVehicleItemAction;api.ISDropVehicleItemAction=nil
    local guard,why=Admission.install(P.config(),api);eq(guard,nil);eq(why,"GuardMissingHook")
    eq(api.ISPickupAnimal.complete,before)
    api.ISDropVehicleItemAction=missing
    eq(Admission.install(P.config(),api),nil)
    eq(Admission.current(P.config(),api).check(),nil)
    local alias=setmetatable({},{__index=api})
    local result,code=Admission.install(P.config(),alias)
    eq(result,nil);eq(code,"GuardProcessReserved")
end)
test("inherited completion does not satisfy exact hook contract",function()
    local api=S.api();local class=api.ISPickupAnimal;local original=class.complete
    class.complete=nil;setmetatable(class,{__index={complete=original}})
    eq(Admission.install(P.config(),api),nil)
end)
test("aliased action classes fail before any completion replacement",function()
    local api=S.api();local class=api.ISPickupAnimal;local before=class.complete
    api.ISAttachAnimalToPlayer=class
    local guard,why=Admission.install(P.config(),api)
    eq(guard,nil);eq(why,"GuardAliasedHook");eq(class.complete,before)
end)
test("duplicate install is refused without nesting wrappers",function()
    local api,flags,calls,guard=fixture();local wrapper=api.ISPickupAnimal.complete
    eq(Admission.install(P.config(),api),nil);eq(api.ISPickupAnimal.complete,wrapper);eq(guard.check(),true)
end)
test("a second API alias cannot wrap already guarded classes",function()
    local api,flags,calls,guard=fixture();local alias=setmetatable({},{__index=api})
    local wrapper=api.ISPickupAnimal.complete
    local other,why=Admission.install(P.config(),alias)
    eq(other,nil);eq(why,"GuardProcessReserved");eq(api.ISPickupAnimal.complete,wrapper);eq(guard.check(),true)
end)
test("different authority adapter cannot take already owned action classes",function()
    local api,flags,calls,guard=fixture();local alias=setmetatable({isServer=function() return true end},{__index=api})
    local other,why=Admission.install(P.config(),alias)
    eq(other,nil);eq(why,"GuardHookOwned");eq(guard.check(),true)
end)
for _,what in ipairs({"class","new","complete"}) do
    test("displaced "..what.." closes every remaining guard permanently",function()
        local api,flags,calls,guard=fixture();local class=api.ISPickupAnimal
        local original=what=="class" and class or class[what]
        if what=="class" then api.ISPickupAnimal={} else class[what]=function() return true end end
        eq(api.ISAttachAnimalToPlayer.complete({animal=foreign()}),false)
        eq(calls.actions.ISAttachAnimalToPlayer,nil);eq(guard.status().reason,"GuardDisplaced")
        if what=="class" then api.ISPickupAnimal=original else class[what]=original end
        eq(guard.check(),nil)
    end)
end
for _,what in ipairs({"__index","metatable"}) do
    test("changed action lookup "..what.." closes every remaining guard",function()
        local api,flags,calls,guard=fixture()
        if what=="__index" then api.ISPickupAnimal.__index={}
        else setmetatable(api.ISPickupAnimal,{__index={}}) end
        eq(api.ISAttachAnimalToPlayer.complete({animal=foreign()}),false)
        eq(guard.status().reason,"GuardDisplaced");eq(calls.actions.ISAttachAnimalToPlayer,nil)
    end)
end
test("custom action index fails installation before any completion replacement",function()
    local api=S.api();local before=api.ISPickupAnimal.complete
    api.ISAttachAnimalToPlayer.__index=function() end
    local result,why=Admission.install(P.config(),api)
    eq(result,nil);eq(why,"GuardClassShape");eq(api.ISPickupAnimal.complete,before)
end)
test("client process installs nothing",function()
    local api,flags=S.api();flags.client=true;local before=api.ISPickupAnimal.complete
    eq(Admission.install(P.config(),api),nil);eq(api.ISPickupAnimal.complete,before)
end)
test("authority loss closes completion and cannot resume",function()
    local api,flags,calls,guard=fixture();flags.client=true
    eq(api.ISPickupAnimal.complete({animal=foreign()}),false);eq(calls.actions.ISPickupAnimal,nil)
    flags.client=false;eq(guard.check(),nil)
end)
for _,method in ipairs({"isServer","isClient","instanceof"}) do
    test("replacement native authority API "..method.." closes guard",function()
        local api,flags,calls,guard=fixture();local original=api[method]
        api[method]=function(...) return original(...) end
        eq(api.ISPickupAnimal.complete({animal=foreign()}),false)
        eq(guard.status().reason,"GuardAuthorityLost");eq(calls.actions.ISPickupAnimal,nil)
    end)
end
test("malformed remote requests do not reach native code or poison valid guards",function()
    local api,flags,calls,guard=fixture()
    for _,action in ipairs({{}, {animal={}}, {animal=false}}) do
        eq(api.ISPickupAnimal.complete(action),false)
    end
    eq(api.ISPickupAnimal.complete(nil),false)
    eq(api.ISPutAnimalInHutch.complete({character={}}),false)
    eq(api.ISHutchGrabAnimal.complete({hutch={fixtureHutch=true},index=math.huge}),false)
    eq(api.ISDropWorldItemAction.complete({item={}}),false)
    eq(guard.check(),true);eq(next(calls.actions),nil)
end)
test("failed native inspection refuses without delegating",function()
    local api,flags,calls,guard=fixture();local animal=S.animal()
    animal.getAnimalType=function() error("fixture invalid native handle") end
    eq(api.ISPickupAnimal.complete({animal=animal}),false);eq(calls.actions.ISPickupAnimal,nil)
    eq(guard.check(),true)
end)
test("full set rechecked after native inspection before mutation",function()
    local api,flags,calls,guard=fixture();local animal=foreign()
    animal.getAnimalType=function() api.ISAttachAnimalToTree.complete=function() end;return "VanillaRaccoon" end
    eq(api.ISPickupAnimal.complete({animal=animal}),false);eq(calls.actions.ISPickupAnimal,nil)
    eq(guard.status().reason,"GuardDisplaced")
end)
test("exception after delegated side effect remains visible and latches failure",function()
    local api,flags,calls,guard=fixture();local effects=0
    local action={animal=foreign(),fixtureComplete=function() effects=effects+1;error("fixture native mutation failed") end}
    local ok,why=pcall(api.ISPickupAnimal.complete,action)
    eq(ok,false);assert(tostring(why):find("fixture native mutation failed",1,true));eq(effects,1)
    eq(guard.status().reason,"GuardMutationFailed")
    eq(api.ISPickupAnimal.complete(action),false);eq(effects,1)
end)
test("displacement during delegated mutation does not report success or retry",function()
    local api,flags,calls,guard=fixture();local effects=0
    local action={animal=foreign(),fixtureComplete=function()
        effects=effects+1;api.ISAttachAnimalToTree.complete=function() end;return true
    end}
    eq(api.ISPickupAnimal.complete(action),false);eq(effects,1);eq(guard.check(),nil)
    eq(api.ISPickupAnimal.complete(action),false);eq(effects,1)
end)
test("false and nil vanilla completions remain false and nil",function()
    local api,flags,calls=fixture()
    eq(api.ISPickupAnimal.complete({animal=foreign(),fixtureComplete=function() return false end}),false)
    eq(api.ISPickupAnimal.complete({animal=foreign(),fixtureComplete=function() return nil end}),nil)
end)
test("guard status is detached and never certifies physical ownership",function()
    local api,flags,calls,guard=fixture();local status=guard.status()
    eq(status.ownershipReady,false);eq(status.coverage,"LUA_ACTIONS_ONLY");eq(status.guardedActions,9)
    status.ownershipReady=true;status.phase="RECOVERY"
    eq(guard.status().ownershipReady,false);eq(guard.check(),true)
    eq(Admission.current({namespace="Foreign",allowedTypes=P.config().allowedTypes},api),nil)
end)
test("configuration cannot assert a coverage or ownership bypass",function()
    local api=S.api();local config=P.config();config.ownershipReady=true
    eq(Admission.install(config,api),nil)
end)
test("original configuration mutation cannot relax managed types",function()
    local api,flags,calls=S.api();local config=P.config()
    local guard=assert(Admission.install(config,api));config.allowedTypes.FixtureCanine=nil
    eq(api.ISPickupAnimal.complete({animal=S.animal()}),false);eq(calls.actions.ISPickupAnimal,nil)
    eq(guard.check(),true)
end)
test("guard inspection exceptions close the process without native mutation",function()
    local api,flags,calls,guard=fixture()
    local wrapper=api.ISAttachAnimalToPlayer.complete
    api.ISPickupAnimal=nil
    setmetatable(api,{__index=function(_,key) if key=="ISPickupAnimal" then error("fixture lookup failure") end end})
    eq(wrapper({animal=foreign()}),false);eq(guard.status().reason,"GuardInspectionFailed")
    eq(calls.actions.ISAttachAnimalToPlayer,nil)
end)
test("authority API lookup exception closes guard without escaping into mutation",function()
    local api,flags,calls,guard=fixture();local wrapper=api.ISPickupAnimal.complete
    api.instanceof=nil
    setmetatable(api,{__index=function(_,key) if key=="instanceof" then error("fixture API lookup failure") end end})
    eq(wrapper({animal=foreign()}),false);eq(guard.status().reason,"GuardAuthorityLost")
    eq(calls.actions.ISPickupAnimal,nil)
end)
test("runtime refuses missing hook before private recovery or event registration",function()
    local api,flags,calls,fire,callbacks=P.fixture();api.ISPickupAnimal=nil
    eq(Runtime.install(P.config(),api),nil);eq(calls.reads,0);eq(calls.writes,0)
    eq(#callbacks.OnInitGlobalModData,0)
end)
test("runtime guard displacement closes recovery without private writes",function()
    S.seed();local api,flags,calls,fire=P.fixture();local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    api.ISPickupAnimal.complete=function() return true end
    eq(runtime.status().phase,"RECOVERY");eq(runtime.status().reason,"GuardDisplaced")
    eq(runtime.census(),nil);local ctx,intent=P.request()
    eq(runtime.prepareOwnership(flags.animals[1],ctx,intent),nil);eq(calls.writes,0)
end)
test("provisioning requires a fully installed guard",function()
    local api,flags,calls,fire,config,player=F.fixture()
    api.ISPickupAnimal.complete=function() return true end
    local service=assert(Provision.new(config,api))
    eq(service.available(),false);eq(service.create(flags.locator,player),nil)
    eq(calls.spawns,0);eq(calls.writes,0);eq(flags.anchor,nil)
end)
test("provisioning without any guard performs no writes or native construction",function()
    local api,flags,calls,fire,config,player=F.fixture(nil,true)
    local service=assert(Provision.new(config,api))
    eq(service.available(),false);eq(service.create(flags.locator,player),nil)
    eq(calls.spawns,0);eq(calls.writes,0);eq(flags.anchor,nil)
end)
test("uncertain constructor cannot publish anchor after guard displacement",function()
    local api,flags,calls,fire,config,player=F.fixture();local add=api.addAnimal
    api.addAnimal=function(...)
        local animal=add(...);api.ISPickupAnimal.complete=function() return true end;return animal
    end
    local provision=assert(Provision.new(config,api))
    eq(provision.create(flags.locator,player),nil);eq(calls.spawns,1);eq(flags.anchor,nil)
    eq(calls.creates,0);eq(provision.available(),false)
    eq(provision.create(flags.locator,player),nil);eq(calls.spawns,1)
    assert(testfs_exists(config.namespace.."/provision-"..require("B47Dog/Codec").checksum(flags.locator).."/slot-a.json"))
end)
test("guarded runtime still refuses dedicated ownership before any private write",function()
    S.seed();local api,flags,calls,fire=P.fixture();local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    local ctx,intent=P.request();ctx.bindingVerified=true;ctx.storeRecovered=true
    local result,why=runtime.prepareOwnership(flags.animals[1],ctx,intent)
    eq(result,nil);eq(why,"UntrustedNativeMarker");eq(calls.writes,0)
    eq(runtime.status().admission.ownershipReady,false)
end)
return {passed=passed,failed=failed,failures=failures}
