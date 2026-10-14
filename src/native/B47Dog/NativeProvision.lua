-- One explicit first-store transaction. No automatic initialization or retry.
local Guard=require "B47Dog/Guard"
local Codec=require "B47Dog/Codec"
local Identity=require "B47Dog/Identity"
local Snapshot=require "B47Dog/Snapshot"
local Cache=require "B47Dog/PZCache"
local Authority=require "B47Dog/NativeAuthority"
local Provision={}

function Provision.new(config,api)
    if not Identity.keys(config,{namespace=true,nativeType=true,breed=true})
        or not Guard.id(config.nativeType) or not Guard.id(config.breed) then return nil,"Unavailable" end
    local used=false
    local service={}
    local function ready(locator)
        return Authority.allowed(api) and api.getCurrentSaveName()==locator
            and api.ModData.get(config.namespace)==nil
    end
    function service.available()
        local ok,result=pcall(function()
            local locator=api.getCurrentSaveName()
            if used or not Guard.id(locator) or not ready(locator) then return false end
            return api.cacheFileExists(config.namespace.."/provision-"..Codec.checksum(locator))==false
        end)
        return ok and result==true
    end
    function service.create(locator,player)
        if not service.available() then return nil,"Recovery" end
        -- The broker authenticates the player and consumes its challenge first.
        -- The process latch closes before any write or constructor side effect.
        used=true
        local ok,result,why=pcall(function()
            if not ready(locator) then return nil,"Recovery" end
            local square=player:getCurrentSquare()
            if square==nil or square:getZ()~=0 or player:isDead()~=false then return nil,"Unavailable" end
            local def=api.AnimalDefinitions.getDef(config.nativeType)
            local breed=def and def:getBreedByName(config.breed)
            if breed==nil then return nil,"Registration" end
            local ids,seen={},{}
            for _,key in ipairs({"world","dog","binding","checkpoint","epoch"}) do
                local id=api.getRandomUUID()
                if not Identity.uuid(id) or seen[id] then return nil,"Recovery" end
                ids[key]=id;seen[id]=true
            end
            if api.cacheFileExists(config.namespace.."/"..ids.world)~=false then return nil,"Recovery" end
            local store=assert(Cache.new(config.namespace,ids.world,api))
            local receipt=assert(Cache.receipt(config.namespace,locator,api))
            local record={ownership={schema=1,worldId=ids.world,dogId=ids.dog,generation=1,
                revision=0,aclRevision=0,phase="LIVE",handlers={},name="Persistence test carrier"},
                binding={generation=1,nativeType=config.nativeType,breed=config.breed,acceptedTokens={[ids.binding]=true}},
                privateHistory={origin="EXPLICIT_RACCOON_TEST",initialCheckpoint=ids.checkpoint}}
            local bytes=assert(Snapshot.seal({worldId=ids.world,saveLocator=locator,checkpoint=ids.checkpoint,
                previous="ROOT",sequence=1,allocationEpoch=ids.epoch,allocationHighwater=1},
                {records={[ids.dog]=record}}))
            local receiptBytes=assert(Codec.encode({schema=1,saveLocator=locator,worldId=ids.world,
                dogId=ids.dog,checkpoint=ids.checkpoint,state="PROVISIONING_ATTEMPT"}))
            if not ready(locator) or not receipt.absent() then return nil,"Recovery" end
            if receipt.write("a",receiptBytes)~=true or receipt.read("a")~=receiptBytes then return nil,"WriteFailed" end
            if not store.absent() then return nil,"Recovery" end
            for _,slot in ipairs({"a","b"}) do
                if not ready(locator) or receipt.read("a")~=receiptBytes or not store.absent(slot) then return nil,"Recovery" end
                if store.write(slot,bytes)~=true or store.read(slot)~=bytes then return nil,"WriteFailed" end
            end
            if not ready(locator) or store.read("a")~=bytes or store.read("b")~=bytes
                or receipt.read("a")~=receiptBytes or player:getCurrentSquare()~=square
                or player:isDead()~=false then return nil,"Recovery" end
            -- Constructor may register an instance even if it later throws. Never retry.
            local animal=api.addAnimal(api.getCell(),square:getX(),square:getY(),0,config.nativeType,breed)
            if api.instanceof(animal,"IsoAnimal")~=true or animal:isDead()~=false
                or animal:getAnimalType()~=config.nativeType or animal:getBreed():getName()~=config.breed then
                return nil,"Recovery"
            end
            local data=animal:getModData()
            if type(data)~="table" or data[config.namespace]~=nil then return nil,"Recovery" end
            local marker={schema=1,worldId=ids.world,dogId=ids.dog,bindingGeneration=1,bindingToken=ids.binding}
            local markerBytes=Codec.encode(marker)
            data[config.namespace]=marker
            animal:addToWorld()
            if animal:isExistInTheWorld()~=true or animal:isDead()~=false
                or animal:getAnimalType()~=config.nativeType or animal:getBreed():getName()~=config.breed
                or Codec.encode(animal:getModData()[config.namespace])~=markerBytes
                or not ready(locator) or store.read("a")~=bytes or store.read("b")~=bytes
                or receipt.read("a")~=receiptBytes then return nil,"Recovery" end
            local anchor=api.ModData.create(config.namespace)
            if type(anchor)~="table" or next(anchor)~=nil then return nil,"Recovery" end
            anchor.schema=1;anchor.worldId=ids.world;anchor.checkpoint=ids.checkpoint
            if api.ModData.get(config.namespace)~=anchor then return nil,"Recovery" end
            return {status="WAITING_INITIAL_NATIVE_RELOAD",dogId=ids.dog}
        end)
        if not ok then return nil,"Recovery" end
        return result,why
    end
    return service
end
return Provision
