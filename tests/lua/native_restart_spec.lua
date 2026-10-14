-- Two fresh Lua VMs and a simulated native disk anchor. This never invokes PZ.
local S=require "storage_support"
local P=require "pairing_support"
local Codec=require "B47Dog/Codec"
local Runtime=require "B47Dog/NativeRuntime"
local Store=require "B47Dog/PrivateStore"
local Cache=require "B47Dog/PZCache"
local api,flags,calls,fire=P.fixture()
if RESTART_PHASE=="prepare" then
    S.seed()
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData",false);fire("OnServerStarted")
    local ctx,intent=P.request()
    assert(runtime.prepareOwnership(flags.animals[1],ctx,intent).status=="WAITING_NATIVE_RELOAD")
    -- Explicit fake native persistence. No completion claim about the real engine.
    testfs_write("simulated-native-anchor.json",assert(Codec.encode(flags.anchor)))
else
    flags.anchor=assert(Codec.decode(testfs_read("simulated-native-anchor.json")))
    local runtime=assert(Runtime.install(P.config(),api))
    fire("OnInitGlobalModData",false);fire("OnServerStarted")
    assert(runtime.status().phase=="RECOVERED")
    assert(runtime.observe(flags.animals[1]).status=="MATCHED")
    local store=assert(Store.open(assert(Cache.new("FixtureDogs",S.WORLD,api)),
        {kind="NativeLoaded",worldId=S.WORLD,saveLocator="fixture-save",checkpoint=flags.anchor.checkpoint}))
    assert(store.read().payload.records[S.DOG].ownership.name=="Native paired name")
    assert(store.read().payload.records[S.DOG].privateHistory.retained=="HIDDEN_FIXTURE")
    assert(calls.writes==0)
end
return {passed=1,failed=0,failures={}}
