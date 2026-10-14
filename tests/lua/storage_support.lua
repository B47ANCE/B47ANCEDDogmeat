local Codec=require "B47Dog/Codec"
local Snapshot=require "B47Dog/Snapshot"
local Support={}
Support.WORLD="11111111-1111-4111-8111-111111111111"
Support.DOG="22222222-2222-4222-8222-222222222222"
Support.BINDING_ID="33333333-3333-4333-8333-333333333333"
Support.EPOCH="44444444-4444-4444-8444-444444444444"
Support.FIRST="55555555-5555-4555-8555-555555555555"
Support.NEXT="66666666-6666-4666-8666-666666666666"
Support.LATER="77777777-7777-4777-8777-777777777777"

function Support.copy(value) return assert(Codec.decode(assert(Codec.encode(value)))) end

function Support.fixture()
    local meta={worldId=Support.WORLD,saveLocator="fixture-save",checkpoint=Support.FIRST,previous="ROOT",
        sequence=1,allocationEpoch=Support.EPOCH,allocationHighwater=1}
    local payload={records={}}
    payload.records[Support.DOG]={
        ownership={schema=1,worldId=Support.WORLD,dogId=Support.DOG,generation=1,revision=3,aclRevision=2,
            phase="LIVE",name="Éclair 🐕",ownerAccount="Alice",ownerEpisode="alice-1",handlers={Bob=true}},
        binding={generation=1,nativeType="FixtureCanine",breed="FixtureShepherd",acceptedTokens={[Support.BINDING_ID]=true}},
        privateHistory={retained="HIDDEN_FIXTURE"}}
    return meta,payload
end

function Support.pair(checkpoint)
    return {kind="OperatorPaired",worldId=Support.WORLD,saveLocator="fixture-save",checkpoint=checkpoint or Support.FIRST}
end

function Support.memory()
    local meta,payload=Support.fixture()
    local raw=assert(Snapshot.seal(meta,payload)); local files={a=raw,b=raw}; local calls={writes=0}
    local transport={read=function(slot) return files[slot] end,
        write=function(slot,bytes) calls.writes=calls.writes+1; files[slot]=bytes; return true end}
    return transport,files,calls,payload
end

function Support.observation()
    return {status="OBSERVED",nativeType="FixtureCanine",breed="FixtureShepherd",nativeId=42,
        marker={schema=1,worldId=Support.WORLD,dogId=Support.DOG,bindingGeneration=1,bindingToken=Support.BINDING_ID}}
end

function Support.animal()
    local obs=Support.observation(); local data={FixtureDogs=Support.copy(obs.marker),unrelated={keep="untouched"}}
    local animal={fixtureNative=true,exists=true,dead=false}
    function animal:isExistInTheWorld() return self.exists end
    function animal:isDead() return self.dead end
    function animal:getAnimalType() return obs.nativeType end
    function animal:getBreed() return {getName=function() return obs.breed end} end
    function animal:getAnimalID() return obs.nativeId end
    function animal:getModData() return data end
    return animal,data,obs
end

-- These are explicit fake engine functions backed by a disposable real directory.
-- Python callbacks cannot access the game, cache or player save directories.
function Support.api()
    local flags={server=true,client=false,locator="fixture-save"}
    local calls={reads=0,writes=0,readerClosed=0,writerClosed=0,charactersRead=0}
    local api={isServer=function() return flags.server end,isClient=function() return flags.client end,
        getCurrentSaveName=function() return flags.locator end,getRandomUUID=function() return Support.NEXT end,
        instanceof=function(value,name) return type(value)=="table" and value.fixtureNative==true and name=="IsoAnimal" end}
    function api.getFileReader(path,create)
        assert(create==false); calls.reads=calls.reads+1
        local bytes=testfs_read(path)
        if bytes==nil then return nil end
        local reader={position=1}
        function reader:read()
            calls.charactersRead=calls.charactersRead+1
            if flags.readFailure then error("fixture read failure") end
            local code=bytes:byte(self.position); self.position=self.position+1
            return code or -1
        end
        function reader:readLine()
            if flags.readFailure then error("fixture read failure") end
            if self.position>#bytes then return nil end
            local finish=bytes:find("\n",self.position,true)
            local line=bytes:sub(self.position,finish and finish-1 or #bytes)
            self.position=finish and finish+1 or #bytes+1
            if line:sub(-1)=="\r" then line=line:sub(1,-2) end
            return line
        end
        function reader:close()
            calls.readerClosed=calls.readerClosed+1
            if flags.readerCloseFailure then error("fixture close failure") end
        end
        return reader
    end
    function api.getFileWriter(path,create,append)
        assert(create==true and append==false); calls.writes=calls.writes+1
        local writer={}
        function writer:write(bytes)
            if flags.writeFailure then error("fixture write failure") end
            if flags.swallowWrite then return end
            if flags.partialWrite then bytes=bytes:sub(1,math.floor(#bytes/2)) end
            testfs_write(path,bytes)
        end
        function writer:close()
            calls.writerClosed=calls.writerClosed+1
            if flags.writerCloseFailure then error("fixture close failure") end
        end
        return writer
    end
    return api,flags,calls
end

function Support.seed()
    local meta,payload=Support.fixture(); local bytes=assert(Snapshot.seal(meta,payload))
    for _,slot in ipairs({"a","b"}) do testfs_write("FixtureDogs/"..Support.WORLD.."/slot-"..slot..".json",bytes) end
    return payload
end

return Support
