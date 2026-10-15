-- TEST-ONLY logical aggregate experiment. Not a production schema, principal
-- adapter, gameplay permission API, bond-rate policy or native commit protocol.
local Codec=require 'B47Dog/Codec'
local Guard=require 'B47Dog/Guard'
local Identity=require 'B47Dog/Identity'
local F={WORLD='11111111-1111-4111-8111-111111111111',DOG='22222222-2222-4222-8222-222222222222'}
local function copy(v) return Codec.decode(assert(Codec.encode(v))) end
local function exact(v,keys) return Guard.plain(v) and Identity.keys(v,keys) end
local function id(v) return Guard.id(v) end
local function request(q)
    return exact(q,{receipt=true,dogId=true,principal=true,amount=true,expectedAggregate=true,
        expectedDog=true,expectedRelationship=true}) and id(q.receipt) and Identity.uuid(q.dogId)
        and id(q.principal) and Guard.integer(q.amount,1) and q.amount<=100
        and Guard.integer(q.expectedAggregate,1) and Guard.integer(q.expectedDog,1)
        and Guard.integer(q.expectedRelationship,1)
end
F.copy=copy

function F.initial()
    return {fixtureSchema=1,worldId=F.WORLD,revision=1,checkpoint='fixture-root',previous='ROOT',
        dogs={[F.DOG]={revision=1,owner=false,alive=true,history='SYNTHETIC_ONLY'}},
        relationships={[F.DOG]={Alice={revision=1,bond=90},Bob={revision=1,bond=90}}},
        primaryOwners={},receipts={}}
end

function F.valid(a)
    if not exact(a,{fixtureSchema=true,worldId=true,revision=true,checkpoint=true,previous=true,
        dogs=true,relationships=true,primaryOwners=true,receipts=true}) or a.fixtureSchema~=1
        or not Identity.uuid(a.worldId) or not Guard.integer(a.revision,1) or not id(a.checkpoint)
        or not id(a.previous) or a.checkpoint==a.previous or not Guard.plain(a.dogs)
        or not Guard.plain(a.relationships) or not Guard.plain(a.primaryOwners) or not Guard.plain(a.receipts)
        or (a.revision==1)~=(a.previous=='ROOT') then return false end
    local count=0
    for dog,row in pairs(a.dogs) do
        count=count+1
        if count>8 or not Identity.uuid(dog) or not exact(row,{revision=true,owner=true,alive=true,history=true})
            or not Guard.integer(row.revision,1) or type(row.alive)~='boolean' or row.history~='SYNTHETIC_ONLY'
            or (row.owner~=false and not id(row.owner)) or not Guard.plain(a.relationships[dog]) then return false end
        local n=0
        for principal,rel in pairs(a.relationships[dog]) do
            n=n+1
            if n>8 or not id(principal) or not exact(rel,{revision=true,bond=true})
                or not Guard.integer(rel.revision,1) or not Guard.integer(rel.bond,0) or rel.bond>100 then return false end
        end
        if row.owner==false then
            if a.primaryOwners[dog]~=nil then return false end
        elseif a.primaryOwners[dog]~=row.owner or not a.relationships[dog][row.owner]
            or a.relationships[dog][row.owner].bond~=100 then return false end
    end
    if count==0 then return false end
    for dog in pairs(a.relationships) do if not a.dogs[dog] then return false end end
    for dog in pairs(a.primaryOwners) do if not a.dogs[dog] then return false end end
    local n=0
    for receipt,r in pairs(a.receipts) do
        n=n+1
        if n>32 or not id(receipt) or not exact(r,{request=true,revision=true,owner=true})
            or type(r.request)~='string' or not Guard.integer(r.revision,2) or r.revision>a.revision
            or (r.owner~=false and not id(r.owner)) then return false end
        local q=Codec.decode(r.request)
        if not request(q) or q.receipt~=receipt or not a.dogs[q.dogId] or not a.relationships[q.dogId][q.principal] then return false end
    end
    return Codec.encode(a)~=nil
end

function F.seal(a)
    if not F.valid(a) then return nil,'Schema' end
    local body=Codec.encode(a)
    return Codec.encode({fixtureEnvelope=1,body=a,checksum=Codec.checksum(body)})
end

function F.decode(bytes,world)
    local e=Codec.decode(bytes)
    if not exact(e,{fixtureEnvelope=true,body=true,checksum=true}) or e.fixtureEnvelope~=1
        or not F.valid(e.body) or e.checksum~=Codec.checksum(Codec.encode(e.body)) then return nil,'Corrupt' end
    if e.body.worldId~=world then return nil,'ForeignWorld' end
    return e.body
end

-- Synthetic prior fixture only. NO converter for deployed ownership schema 1.
function F.migrate(a)
    if F.valid(a) then return copy(a) end
    if not exact(a,{fixtureSchema=true,aggregate=true}) or a.fixtureSchema~=0
        or not F.valid(a.aggregate) then return nil,'UnsupportedMigration' end
    return copy(a.aggregate)
end

function F.open(io,world,checkpoint)
    if not Identity.uuid(world) or not id(checkpoint) then return nil,'Pairing' end
    local raw,slots={},{}
    for _,s in ipairs({'a','b'}) do
        local ok,bytes=pcall(io.read,s)
        if not ok or type(bytes)~='string' then return nil,'Missing' end
        raw[s]=bytes
        local a,why=F.decode(bytes,world)
        if not a then return nil,why end
        slots[s]=a
    end
    local selected
    for _,s in ipairs({'a','b'}) do
        if slots[s].checkpoint==checkpoint then
            if selected and raw[s]~=raw[selected] then return nil,'Ambiguous' end
            selected=s
        end
    end
    if not selected then return nil,'Unpaired' end
    local inactive=selected=='a' and 'b' or 'a'
    local current,other=slots[selected],slots[inactive]
    if other.checkpoint~=checkpoint and
        (current.revision~=other.revision+1 or current.previous~=other.checkpoint) then return nil,'PendingOrAmbiguous' end
    local locked=false
    local session={}
    function session.read() return copy(current) end
    function session.prepare(q,actor,nextCheckpoint)
        if locked then return nil,'Locked' end
        if not request(q) or not exact(actor,{synthetic=true,principal=true}) or actor.synthetic~=true
            or actor.principal~=q.principal then return nil,'SyntheticContextRequired' end
        local encoded=Codec.encode(q)
        local old=current.receipts[q.receipt]
        if old then
            if old.request~=encoded then return nil,'ReceiptConflict' end
            return {status='REPLAY',revision=old.revision,owner=old.owner}
        end
        local dog=current.dogs[q.dogId]
        local rel=dog and current.relationships[q.dogId][q.principal]
        if not dog or not rel or not dog.alive then return nil,'Unavailable' end
        if current.revision~=q.expectedAggregate or dog.revision~=q.expectedDog
            or rel.revision~=q.expectedRelationship then return nil,'Stale' end
        if not id(nextCheckpoint) or nextCheckpoint=='ROOT' or nextCheckpoint==current.checkpoint
            or nextCheckpoint==other.checkpoint or rel.bond+q.amount>100 then return nil,'Invalid' end
        local after=copy(current)
        local d,r=after.dogs[q.dogId],after.relationships[q.dogId][q.principal]
        after.revision=after.revision+1; d.revision=d.revision+1; r.revision=r.revision+1
        r.bond=r.bond+q.amount
        if r.bond==100 and d.owner==false then d.owner=q.principal;after.primaryOwners[q.dogId]=q.principal end
        after.receipts[q.receipt]={request=encoded,revision=after.revision,owner=d.owner}
        after.previous=current.checkpoint;after.checkpoint=nextCheckpoint
        local bytes,why=F.seal(after)
        if not bytes then return nil,why end
        for _,s in ipairs({'a','b'}) do
            local ok,value=pcall(io.read,s)
            if not ok or value~=raw[s] then locked=true;return nil,'ChangedOnDisk' end
        end
        locked=true -- Any I/O uncertainty requires explicit reopen/reconciliation.
        local ok,written=pcall(io.write,inactive,bytes)
        if not ok or written~=true then return nil,'WriteUncertain' end
        local readOK,readback=pcall(io.read,inactive)
        if not readOK or readback~=bytes then return nil,'ReadbackUncertain' end
        return {status='PREPARED_READBACK_ONLY',checkpoint=nextCheckpoint,revision=after.revision,owner=d.owner}
    end
    return session
end

return F
