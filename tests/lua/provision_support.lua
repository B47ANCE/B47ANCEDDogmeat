local S=require "storage_support"
local P=require "pairing_support"
local Admission=require "B47Dog/NativeAdmissionGuard"
local F={counter=0}
function F.fixture(namespace,withoutGuard)
    F.counter=F.counter+1
    local api,flags,calls,fire=P.fixture()
    local config={namespace=namespace or "ProvisionFixture"..F.counter,nativeType="FixtureCanine",breed="FixtureShepherd"}
    flags.anchor=nil;flags.animals={};flags.now=100000;flags.allowed=true
    calls.spawns=0;calls.creates=0;calls.uuid=0
    api.cacheFileExists=function(path) return testfs_exists(path)==true end
    api.getTimestampMs=function() return flags.now end
    api.getRandomUUID=function()
        calls.uuid=calls.uuid+1
        return string.format("00000000-0000-4000-8000-%012d",flags.duplicateUUID and 1 or calls.uuid)
    end
    api.ModData={get=function(name) assert(name==config.namespace);return flags.anchor end,
        create=function(name)
            assert(name==config.namespace);calls.creates=calls.creates+1
            if flags.anchor~=nil then return nil end
            flags.anchor={};return flags.anchor
        end}
    api.SandboxVars={B47ANCEDDogmeat={PersistenceTestMode=true}}
    api.Capability={AnimalCheats="AnimalCheats"}
    local square={getX=function() return 100 end,getY=function() return 200 end,getZ=function() return flags.z or 0 end}
    local player={fixturePlayer=true,isDead=function() return flags.playerDead or false end,
        getCurrentSquare=function() return square end,
        getRole=function() return {hasCapability=function() return flags.allowed end} end}
    local nativeInstanceof=api.instanceof
    api.instanceof=function(value,name)
        if name=="IsoPlayer" then return type(value)=="table" and value.fixturePlayer==true end
        return nativeInstanceof(value,name)
    end
    api.AnimalDefinitions={getDef=function(kind)
        if flags.noDefinition then return nil end
        assert(kind==config.nativeType)
        return {getBreedByName=function(_,breed) assert(breed==config.breed);return {fixtureBreed=true} end}
    end}
    api.addAnimal=function(_,x,y,z,kind,breed)
        calls.spawns=calls.spawns+1
        assert(x==100 and y==200 and z==0 and kind==config.nativeType and breed.fixtureBreed)
        if flags.spawnThrow then error("uncertain constructor") end
        local animal,data=S.animal();animal.exists=false
        function animal:addToWorld()
            self.exists=true;flags.animals={self}
            if flags.afterSpawn then flags.afterSpawn(self,data) end
        end
        flags.spawned=animal;flags.spawnedData=data
        return animal
    end
    if not withoutGuard then
        assert(Admission.install({namespace=config.namespace,allowedTypes={[config.nativeType]={[config.breed]=true}}},api))
    end
    return api,flags,calls,fire,config,player
end
return F
