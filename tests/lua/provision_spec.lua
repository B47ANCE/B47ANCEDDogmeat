local F=require "provision_support"
local S=require "storage_support"
local P=require "pairing_support"
local Provision=require "B47Dog/NativeProvision"
local Service=require "B47Dog/NativeTestService"
local Runtime=require "B47Dog/NativeRuntime"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
local Codec=require "B47Dog/Codec"
local passed,failed,failures=0,0,{}
local function eq(a,b) assert(a==b,tostring(a).." ~= "..tostring(b)) end
local function test(name,fn)
    local ok,err=pcall(fn);if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(err) end
end
local function broker()
    local api,flags,calls,fire,config,player=F.fixture()
    local runtime=assert(Runtime.install({namespace=config.namespace,allowedTypes={[config.nativeType]={[config.breed]=true}}},api))
    fire("OnInitGlobalModData",true);fire("OnServerStarted")
    return Service.new(config,runtime,api),api,flags,calls,config,player,runtime
end
test("root writes precede constructor, exact public marker and anchor only",function()
    local api,flags,calls,_,config,player=F.fixture()
    local provision=assert(Provision.new(config,api))
    local spawn=api.addAnimal
    api.addAnimal=function(...) eq(calls.writes,3);eq(flags.anchor,nil);return spawn(...) end
    local result=assert(provision.create(flags.locator,player))
    eq(result.status,"WAITING_INITIAL_NATIVE_RELOAD");eq(calls.spawns,1);eq(calls.creates,1)
    local anchor=flags.anchor
    local store=assert(Store.open(assert(Cache.new(config.namespace,anchor.worldId,api)),
        {kind="NativeLoaded",worldId=anchor.worldId,saveLocator=flags.locator,checkpoint=anchor.checkpoint}))
    eq(store.read().payload.records[result.dogId].ownership.name,"Persistence test carrier")
    eq(flags.spawnedData[config.namespace].dogId,result.dogId)
    eq(flags.spawnedData[config.namespace].privateHistory,nil)
    eq(Codec.encode(anchor),Codec.encode({schema=1,worldId=anchor.worldId,checkpoint=anchor.checkpoint}))
    eq(provision.create(flags.locator,player),nil);eq(calls.spawns,1)
    eq(Provision.new(config,api).available(),false)
end)
for _,reason in ipairs({"client","wrongLocator","occupied","badAnchor","receipt","directory","uuid","definition","upstairs"}) do
    test("initialization refuses "..reason,function()
        local api,flags,calls,_,config,player=F.fixture()
        local locator=flags.locator
        if reason=="client" then flags.client=true
        elseif reason=="wrongLocator" then locator="wrong"
        elseif reason=="occupied" then flags.anchor={schema=1}
        elseif reason=="badAnchor" then flags.anchor="invalid"
        elseif reason=="receipt" then testfs_write(config.namespace.."/provision-"..Codec.checksum(locator).."/slot-a.json","")
        elseif reason=="directory" then testfs_write(config.namespace.."/00000000-0000-4000-8000-000000000001/unknown","keep")
        elseif reason=="uuid" then flags.duplicateUUID=true
        elseif reason=="definition" then flags.noDefinition=true
        else flags.z=1 end
        eq(Provision.new(config,api).create(locator,player),nil);eq(calls.spawns,0);eq(calls.writes,0)
    end)
end
for _,phase in ipairs({1,2,3}) do
    for _,failure in ipairs({"throw","partial","close"}) do
        test("preserve failed write "..phase.." "..failure,function()
            local api,flags,calls,_,config,player=F.fixture();local writer=api.getFileWriter
            api.getFileWriter=function(...)
                local out=writer(...);local write=out.write;local close=out.close
                function out:write(bytes)
                    if calls.writes==phase then
                        if failure=="throw" then error("write failed") end
                        if failure=="partial" then bytes=bytes:sub(1,10) end
                    end
                    return write(self,bytes)
                end
                function out:close() if calls.writes==phase and failure=="close" then error("close failed") end;return close(self) end
                return out
            end
            local provision=Provision.new(config,api)
            eq(provision.create(flags.locator,player),nil);eq(calls.spawns,0);eq(calls.creates,0)
            local writes=calls.writes;eq(provision.create(flags.locator,player),nil);eq(calls.writes,writes)
        end)
    end
end
for _,mutation in ipairs({"marker","slot","receipt","anchor","role","locator","dead"}) do
    test("post-constructor drift preserves uncertain animal "..mutation,function()
        local api,flags,calls,_,config,player=F.fixture()
        flags.afterSpawn=function(animal,data)
            local marker=data[config.namespace]
            if mutation=="marker" then marker.bindingToken=S.LATER
            elseif mutation=="slot" then testfs_write(config.namespace.."/"..marker.worldId.."/slot-a.json","changed")
            elseif mutation=="receipt" then testfs_write(config.namespace.."/provision-"..Codec.checksum(flags.locator).."/slot-a.json","changed")
            elseif mutation=="anchor" then flags.anchor={foreign=true}
            elseif mutation=="role" then flags.client=true
            elseif mutation=="locator" then flags.locator="other"
            else animal.dead=true end
        end
        local provision=Provision.new(config,api)
        eq(provision.create(flags.locator,player),nil);eq(calls.spawns,1);eq(calls.creates,0)
        eq(provision.create(flags.locator,player),nil);eq(calls.spawns,1);assert(flags.spawned)
    end)
end
test("new directory appearing during receipt write is preserved",function()
    local api,flags,calls,_,config,player=F.fixture();local writer=api.getFileWriter
    api.getFileWriter=function(...)
        local out=writer(...);local close=out.close
        function out:close()
            close(self)
            testfs_write(config.namespace.."/00000000-0000-4000-8000-000000000001/unknown","preserve")
        end
        return out
    end
    eq(Provision.new(config,api).create(flags.locator,player),nil);eq(calls.writes,1);eq(calls.spawns,0)
end)
test("constructor failure never retries across process receipt boundary",function()
    local api,flags,calls,_,config,player=F.fixture();flags.spawnThrow=true
    eq(Provision.new(config,api).create(flags.locator,player),nil);eq(calls.spawns,1)
    flags.spawnThrow=false
    eq(Provision.new(config,api).create(flags.locator,player),nil);eq(calls.spawns,1)
end)
for _,reason in ipairs({"unauthorized","client","dead","fake","disabled"}) do
    test("broker rejects "..reason.." with no disk I/O",function()
        local service,api,flags,calls,_,player=broker()
        if reason=="unauthorized" then flags.allowed=false elseif reason=="client" then flags.client=true
        elseif reason=="dead" then flags.playerDead=true elseif reason=="fake" then player={}
        else api.SandboxVars.B47ANCEDDogmeat.PersistenceTestMode=false end
        local result=service.handle(player,"Inspect",{protocol=1})
        if reason=="disabled" then eq(result.status,"Disabled") else eq(result,nil) end
        eq(calls.writes,0);eq(calls.spawns,0)
    end)
end
test("network challenge binds player, locator, acknowledgement and single use",function()
    local service,api,flags,calls,_,player=broker()
    local result=service.handle(player,"Inspect",{protocol=1});eq(result.status,"NeedsInitialization")
    eq(result.saveLocator,nil);flags.now=flags.now+2000
    local other={fixturePlayer=true,isDead=player.isDead,getRole=player.getRole,getCurrentSquare=player.getCurrentSquare}
    eq(service.handle(other,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}).status,"Recovery")
    eq(calls.writes,0)
    eq(service.handle(player,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}).status,"WAITING_INITIAL_NATIVE_RELOAD")
    flags.now=flags.now+2000
    eq(service.handle(player,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}).status,"WAITING_INITIAL_NATIVE_RELOAD")
    eq(calls.spawns,1)
end)
test("immediate confirmation is accepted once without an artificial wait",function()
    local service,api,flags,calls,_,player=broker()
    local result=service.handle(player,"Inspect",{protocol=1})
    eq(service.handle(player,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}).status,
        "WAITING_INITIAL_NATIVE_RELOAD")
    eq(calls.spawns,1)
end)
test("anchor introduced after challenge refuses before writes",function()
    local service,api,flags,calls,_,player=broker()
    local result=service.handle(player,"Inspect",{protocol=1});flags.anchor={foreign=true}
    eq(service.handle(player,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}).status,"Recovery")
    eq(calls.writes,0);eq(calls.spawns,0);eq(flags.anchor.foreign,true)
end)
for _,slot in ipairs({"a","b"}) do
    test("corrupt initial slot after restart never reinitializes "..slot,function()
        local api,flags,calls,fire,config,player=F.fixture()
        assert(Provision.new(config,api).create(flags.locator,player))
        testfs_write(config.namespace.."/"..flags.anchor.worldId.."/slot-"..slot..".json","corrupt")
        local writes=calls.writes
        local runtime=assert(Runtime.install({namespace=config.namespace,allowedTypes={[config.nativeType]={[config.breed]=true}}},api))
        fire("OnInitGlobalModData");fire("OnServerStarted")
        eq(runtime.status().phase,"RECOVERY");eq(calls.writes,writes);eq(calls.spawns,1)
        eq(Provision.new(config,api).available(),false)
    end)
end
for _,reason in ipairs({"expiry","locator","ack","extra","protocol","clock"}) do
    test("challenge rejects "..reason,function()
        local service,api,flags,calls,_,player=broker()
        local result=service.handle(player,"Inspect",{protocol=1});flags.now=flags.now+2000
        local args={protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"}
        if reason=="expiry" then flags.now=flags.now+120001 elseif reason=="locator" then flags.locator="other"
        elseif reason=="ack" then args.ack="wrong" elseif reason=="extra" then args.x=100
        elseif reason=="protocol" then args.protocol=2 else flags.now=0 end
        assert(service.handle(player,"Provision",args).status~="WAITING_INITIAL_NATIVE_RELOAD")
        eq(calls.writes,0);eq(calls.spawns,0)
    end)
end
test("dedicated marker match never authorizes ownership mutation",function()
    S.seed();local api,flags,calls,fire=P.fixture()
    local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData");fire("OnServerStarted")
    eq(runtime.observe(flags.animals[1]).status,"MATCHED")
    local context,intent=P.request();local result,reason=runtime.prepareOwnership(flags.animals[1],context,intent)
    eq(result,nil);eq(reason,"UntrustedNativeMarker");eq(calls.writes,0)
end)
test("explicit SP bootstrap events recover without dedicated startup",function()
    S.seed();local api,flags,calls,fire=P.fixture();flags.server=false;api.B47DogSinglePlayer=true
    local runtime=assert(Runtime.install(P.config(),api));fire("OnInitGlobalModData");fire("OnServerStarted")
    eq(runtime.status().serverStarted,false);fire("OnGameStart");eq(runtime.status().serverStarted,true)
    eq(calls.census,1)
end)
return {passed=passed,failed=failed,failures=failures}
