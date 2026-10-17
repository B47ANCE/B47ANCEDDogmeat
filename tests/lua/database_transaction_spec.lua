local F=require 'database_store_fixture'
local Codec=require 'B47Dog/Codec'
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,err=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..': '..tostring(err) end
end
local function eq(a,b) assert(a==b,'expected '..tostring(b)..', got '..tostring(a)) end
local function request(principal,revision)
    return {receipt='receipt-'..principal,dogId=F.DOG,principal=principal,amount=10,
        expectedAggregate=revision or 1,expectedDog=revision or 1,expectedRelationship=1}
end
local function actor(p) return {synthetic=true,principal=p or 'Alice'} end
local function memory()
    local bytes=assert(F.seal(F.initial())); local files={a=bytes,b=bytes};local writes=0
    local io={read=function(s) return files[s] end,
        write=function(s,b) writes=writes+1;files[s]=b;return true end}
    return io,files,function() return writes end
end
local function open(io,checkpoint) return assert(F.open(io,F.WORLD,checkpoint or 'fixture-root')) end

test('bond, primary index and event form one sealed candidate',function()
    local io,files=memory();local s=open(io);local old=files.a
    local r=assert(s.prepare(request('Alice'),actor(),'next'))
    eq(r.status,'PREPARED_READBACK_ONLY');eq(s.read().dogs[F.DOG].owner,false)
    eq(files.b,old) -- equal slots select b; write only inactive a
    local a=open(io,'next').read()
    eq(a.dogs[F.DOG].owner,'Alice');eq(a.primaryOwners[F.DOG],'Alice')
    eq(a.relationships[F.DOG].Alice.bond,100);eq(a.receipts['receipt-Alice'].owner,'Alice')
    eq(a.dogs[F.DOG].revision,2);eq(a.relationships[F.DOG].Alice.revision,2)
end)

test('serialized competing coordinators cannot both claim old aggregate',function()
    local io,files,writes=memory();local a,b=open(io),open(io)
    assert(a.prepare(request('Alice'),actor(),'next'))
    local r,why=b.prepare(request('Bob'),actor('Bob'),'loser');eq(r,nil);eq(why,'ChangedOnDisk');eq(writes(),1)
    eq(open(io,'next').read().primaryOwners[F.DOG],'Alice')
end)

test('secondary 100 never transfers primary ownership',function()
    local io=memory();assert(open(io).prepare(request('Alice'),actor(),'next'))
    assert(open(io,'next').prepare(request('Bob',2),actor('Bob'),'later'))
    local a=open(io,'later').read();eq(a.relationships[F.DOG].Bob.bond,100)
    eq(a.primaryOwners[F.DOG],'Alice');eq(a.receipts['receipt-Bob'].owner,'Alice')
end)

test('receipt replay after reopen does not write or increment',function()
    local io,files,writes=memory();local q=request('Alice')
    assert(open(io).prepare(q,actor(),'next'))
    local saved=files.a;local s=open(io,'next');local r=assert(s.prepare(q,actor(),'ignored'))
    eq(r.status,'REPLAY');eq(r.revision,2);eq(writes(),1);eq(files.a,saved)
    q.amount=9;local v,why=s.prepare(q,actor(),'ignored');eq(v,nil);eq(why,'ReceiptConflict')
end)

for _,field in ipairs({'expectedAggregate','expectedDog','expectedRelationship'}) do
    test('stale revision refuses before I/O '..field,function()
        local io,files,writes=memory();local q=request('Alice');q[field]=2
        local r,why=open(io).prepare(q,actor(),'next');eq(r,nil);eq(why,'Stale');eq(writes(),0);eq(files.a,files.b)
    end)
end

for _,context in ipairs({{synthetic=true,principal='Bob'},{principal='Alice'},{synthetic=false,principal='Alice'}}) do
    test('no synthetic actor substitution '..tostring(context.synthetic)..tostring(context.principal),function()
        local io,_,writes=memory();eq(open(io).prepare(request('Alice'),context,'next'),nil);eq(writes(),0)
    end)
end

for _,change in ipairs({'partialOwner','partialIndex','partialBond','activeLease','futureSchema','foreignWorld','malformedReceipt','over100'}) do
    test('invalid aggregate cannot be admitted '..change,function()
        local a=F.initial()
        if change=='partialOwner' then a.dogs[F.DOG].owner='Alice'
        elseif change=='partialIndex' then a.primaryOwners[F.DOG]='Alice'
        elseif change=='partialBond' then a.dogs[F.DOG].owner='Alice';a.primaryOwners[F.DOG]='Alice'
        elseif change=='activeLease' then a.activeLeases={Alice=true}
        elseif change=='futureSchema' then a.fixtureSchema=2
        elseif change=='foreignWorld' then a.worldId='client-world'
        elseif change=='over100' then a.relationships[F.DOG].Alice.bond=101
        else a.receipts.bad={request='{}',revision=2,owner=false};a.revision=2;a.previous='old' end
        eq(F.seal(a),nil)
    end)
end

test('detached reads preserve private baseline',function()
    local io=memory();local s=open(io);local a=s.read();a.dogs[F.DOG].history='changed'
    eq(s.read().dogs[F.DOG].history,'SYNTHETIC_ONLY')
end)

for _,failure in ipairs({'beforeWrite','partialWrite','afterWrite','readback'}) do
    test('uncertain write preserves selected data and locks session '..failure,function()
        local io,files=memory();local old=files.b;local original=io.write
        io.write=function(slot,bytes)
            if failure=='beforeWrite' then error('injected') end
            if failure=='partialWrite' then files[slot]=bytes:sub(1,30);error('injected') end
            original(slot,bytes)
            if failure=='afterWrite' then error('injected') end
            if failure=='readback' then files[slot]=bytes..'trailing' end
            return true
        end
        local s=open(io);eq(s.prepare(request('Alice'),actor(),'next'),nil)
        eq(files.b,old);local r,why=s.prepare(request('Alice'),actor(),'retry');eq(r,nil);eq(why,'Locked')
        if failure=='beforeWrite' then assert(open(io))
        else eq(F.open(io,F.WORLD,'fixture-root'),nil) end
        if failure=='afterWrite' then
            -- A complete candidate can exist despite caller failure. Never retry effects.
            eq(open(io,'next').read().primaryOwners[F.DOG],'Alice')
        end
    end)
end

test('neither missing nor corrupt stores initialize themselves',function()
    local io,files,writes=memory();files.a=nil;eq(F.open(io,F.WORLD,'fixture-root'),nil);eq(writes(),0)
    files.a='{';eq(F.open(io,F.WORLD,'fixture-root'),nil);eq(writes(),0)
end)

test('foreign world and divergent same-checkpoint slots refused',function()
    local io,files=memory();eq(F.open(io,F.DOG,'fixture-root'),nil)
    local a=F.initial();a.relationships[F.DOG].Alice.bond=89;files.a=assert(F.seal(a))
    local r,why=F.open(io,F.WORLD,'fixture-root');eq(r,nil);eq(why,'Ambiguous')
end)

test('old pair cannot authorize pending candidate or private-only rollback',function()
    local io,files=memory();local backup=files.a
    assert(open(io).prepare(request('Alice'),actor(),'next'))
    local r,why=F.open(io,F.WORLD,'fixture-root');eq(r,nil);eq(why,'PendingOrAmbiguous')
    files.a=backup;files.b=backup
    r,why=F.open(io,F.WORLD,'next');eq(r,nil);eq(why,'Unpaired')
    -- A coordinated rollback of slots AND external pairing is indistinguishable.
    eq(open(io).read().primaryOwners[F.DOG],nil)
end)

test('synthetic forward migration is detached and idempotent; legacy is refused',function()
    local old={fixtureSchema=0,aggregate=F.initial()};local before=Codec.encode(old)
    local a=assert(F.migrate(old));eq(Codec.encode(F.migrate(a)),Codec.encode(a));eq(Codec.encode(old),before)
    eq(a.relationships[F.DOG].Alice.bond,90);eq(a.dogs[F.DOG].owner,false)
    eq(F.migrate({schema=1,records={}}),nil);old.aggregate.dogs[F.DOG].history='corrupt';eq(F.migrate(old),nil)
end)

test('real files survive repeated fresh store reopen',function()
    local io={read=function(s) return testfs_read('database-repeat/'..s) end,
        write=function(s,b) testfs_write('database-repeat/'..s,b);return true end}
    local raw=assert(F.seal(F.initial()));io.write('a',raw);io.write('b',raw)
    assert(open(io).prepare(request('Alice'),actor(),'next'))
    for _=1,3 do eq(open(io,'next').read().primaryOwners[F.DOG],'Alice') end
end)

test('adjacent synthetic SteamID64 strings collide as doubles',function()
    local a,b='76561198000000000','76561198000000001'
    assert(a~=b and tonumber(a)==tonumber(b))
    -- Mathematical witness only; installed Kahlua conversion is source evidence.
end)

return {passed=passed,failed=failed,failures=failures}
