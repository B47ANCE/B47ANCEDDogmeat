-- Actual files + fresh Lua VM; native serialization is explicitly simulated.
local F=require "provision_support"
local S=require "storage_support"
local Codec=require "B47Dog/Codec"
local Provision=require "B47Dog/NativeProvision"
local Runtime=require "B47Dog/NativeRuntime"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
local api,flags,calls,fire,config,player=F.fixture("ProvisionRestart")
if RESTART_PHASE=="prepare" then
    assert(Provision.new(config,api).create(flags.locator,player))
    testfs_write("provision-fake-native.json",assert(Codec.encode({anchor=flags.anchor,marker=flags.spawnedData[config.namespace]})))
else
    local disk=assert(Codec.decode(testfs_read("provision-fake-native.json")))
    flags.anchor=disk.anchor
    local animal,data=S.animal();data[config.namespace]=disk.marker;flags.animals={animal}
    local runtime=assert(Runtime.install({namespace=config.namespace,allowedTypes={[config.nativeType]={[config.breed]=true}}},api))
    fire("OnInitGlobalModData");fire("OnServerStarted")
    assert(runtime.observe(animal).status=="MATCHED")
    local store=assert(Store.open(assert(Cache.new(config.namespace,disk.anchor.worldId,api)),
        {kind="NativeLoaded",worldId=disk.anchor.worldId,checkpoint=disk.anchor.checkpoint,saveLocator=flags.locator}))
    local record=store.read().payload.records[disk.marker.dogId]
    assert(record.ownership.name=="Persistence test carrier" and record.privateHistory.origin=="EXPLICIT_RACCOON_TEST")
    assert(not Provision.new(config,api).available());assert(calls.spawns==0 and calls.writes==0)
end
return {passed=1,failed=0,failures={}}
