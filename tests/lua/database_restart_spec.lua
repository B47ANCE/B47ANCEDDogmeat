-- Separate Lua VMs and disposable files; NOT PZ/native restart evidence.
local F=require 'database_store_fixture'
local Codec=require 'B47Dog/Codec'
local io={read=function(s) return testfs_read('database-restart/'..s) end,
    write=function(s,b) testfs_write('database-restart/'..s,b);return true end}
if RESTART_PHASE=='prepare' then
    local raw=assert(F.seal(F.initial()));io.write('a',raw);io.write('b',raw)
    local q={receipt='restart-bond',dogId=F.DOG,principal='Alice',amount=10,
        expectedAggregate=1,expectedDog=1,expectedRelationship=1}
    local s=assert(F.open(io,F.WORLD,'fixture-root'))
    assert(s.prepare(q,{synthetic=true,principal='Alice'},'restart-next'))
    testfs_write('database-restart/request',assert(Codec.encode(q)))
else
    local s=assert(F.open(io,F.WORLD,'restart-next'));local a=s.read()
    assert(a.primaryOwners[F.DOG]=='Alice' and a.relationships[F.DOG].Alice.bond==100)
    assert(a.receipts['restart-bond'] and a.dogs[F.DOG].history=='SYNTHETIC_ONLY')
    assert(a.activeLeases==nil) -- No durable lease authority in this fixture schema.
    local r=assert(s.prepare(Codec.decode(testfs_read('database-restart/request')),
        {synthetic=true,principal='Alice'},'unused'))
    assert(r.status=='REPLAY' and s.read().revision==2)
end
return {passed=1,failed=0,failures={}}
