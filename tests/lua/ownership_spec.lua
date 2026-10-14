local Ownership = require "B47Dog/Ownership"
local Projection = require "B47Dog/Projection"
local Guard = require "B47Dog/Guard"
local Access = require "B47Dog/Access"
local passed, failed, failures = 0, 0, {}

local function test(name, fn)
    local ok, message = pcall(fn)
    if ok then passed = passed + 1
    else failed = failed + 1; failures[#failures + 1] = name .. ": " .. tostring(message) end
end

local function equal(actual, expected)
    assert(actual == expected, "expected " .. tostring(expected) .. ", got " .. tostring(actual))
end

local function clone(value)
    if type(value) ~= "table" then return value end
    local result = {}
    for key, item in pairs(value) do result[key] = clone(item) end
    return result
end

local function same(a, b)
    if type(a) ~= type(b) then return false end
    if type(a) ~= "table" then return a == b end
    for key, value in pairs(a) do if not same(value, b[key]) then return false end end
    for key in pairs(b) do if a[key] == nil then return false end end
    return true
end

local function fixture()
    local state = {schema=1, worldId="world-a", dogId="dog-a", generation=1, revision=3,
        aclRevision=2, phase="LIVE", name="Koda", ownerAccount="Alice", ownerEpisode="alice-1",
        handlers={Bob=true}}
    local context = {worldId="world-a", sessionId="session-a", visible=true, reachable=true,
        bindingVerified=true, storeRecovered=true, ownershipEnabled=true,
        actor={accountId="Alice", episodeId="alice-1", connected=true, alive=true},
        config={revision=1, HandlerPermissionMode="OwnerAndGranted", OwnerAfterCharacterDeath="RetainAccountAccess"},
        target={reference="target-b", accountId="Bob", episodeId="bob-1", verified=true,
            connected=true, alive=true, reachable=true, consentsToTransfer=true},
        observed={posture="Standing", activity="Idle", hiddenStress=987654}}
    return state, context
end

local function request(state, context, action)
    local result = {protocol=1, worldId=state.worldId, sessionId=context.sessionId, dogId=state.dogId,
        generation=state.generation, revision=state.revision, configRevision=context.config.revision, action=action}
    if action == "RenameDog" then result.name = "Rex" end
    if action == "GrantHandler" or action == "RevokeHandler" or action == "TransferDog" then result.targetRef="target-b" end
    return result
end

local function rejected(result, reason)
    equal(result.ok, false); equal(result.reason, reason); equal(result.state, nil); equal(result.view, nil)
    local count=0; for _ in pairs(result) do count=count+1 end; equal(count, 2)
end

test("claim binds authenticated account and episode, no input mutation", function()
    local state, context = fixture(); state.ownerAccount=nil; state.ownerEpisode=nil; state.handlers={}
    local before = clone(state)
    local result = Ownership.propose(state, context, request(state, context, "ClaimDog"))
    equal(result.ok, true); equal(result.state.ownerAccount, "Alice"); equal(result.state.ownerEpisode, "alice-1")
    equal(result.state.revision, 4); equal(result.state.aclRevision, 3); assert(same(state, before))
end)

test("rename changes display data, preserves dog identity and ACL", function()
    local state, context = fixture(); local req=request(state, context, "RenameDog"); req.name="  Éclair 🐕  "
    local result=Ownership.propose(state, context, req)
    equal(result.ok,true); equal(result.state.name,"Éclair 🐕"); equal(result.state.dogId,state.dogId)
    equal(result.state.generation,1); equal(result.state.aclRevision,2); equal(result.state.revision,4)
    equal(state.name,"Koda"); result.state.handlers.Bob=nil; equal(state.handlers.Bob,true)
end)

test("grant and revoke update eligibility only, retain external history", function()
    local state, context=fixture(); state.handlers={}
    local discoveries={worldId=state.worldId,dogId=state.dogId,byAccount={Bob={["bob-1"]={relationship="Trusted"}}}}; local before=clone(discoveries)
    local granted=Ownership.propose(state,context,request(state,context,"GrantHandler"))
    context.actor={accountId="Bob",episodeId="bob-1",connected=true,alive=true}
    equal(Projection.build(granted.state,context,discoveries).view.role,"handler")
    context.actor={accountId="Alice",episodeId="alice-1",connected=true,alive=true}
    local revoked=Ownership.propose(granted.state,context,request(granted.state,context,"RevokeHandler"))
    context.actor={accountId="Bob",episodeId="bob-1",connected=true,alive=true}
    local view=Projection.build(revoked.state,context,discoveries).view
    equal(view.role,"observer"); equal(view.discovered,nil); assert(same(discoveries,before))
end)

test("transfer clears previous owner and all grants without replacing dog", function()
    local state,context=fixture(); state.handlers.Carol=true
    local oldRequest=request(state,context,"RenameDog")
    local result=Ownership.propose(state,context,request(state,context,"TransferDog"))
    equal(result.state.ownerAccount,"Bob"); equal(result.state.ownerEpisode,"bob-1")
    equal(next(result.state.handlers),nil); equal(result.state.dogId,"dog-a"); equal(result.state.generation,1)
    rejected(Ownership.propose(result.state,context,oldRequest),"Stale")
    rejected(Ownership.propose(result.state,context,request(result.state,context,"RenameDog")),"Unauthorized")
end)

test("replaying a committed mutation with old revision cannot repeat it", function()
    local state,context=fixture(); local req=request(state,context,"RenameDog")
    local proposal=Ownership.propose(state,context,req)
    rejected(Ownership.propose(proposal.state,context,req),"Stale")
    local repeated=Ownership.propose(proposal.state,context,request(proposal.state,context,"RenameDog"))
    equal(repeated.changed,false); equal(repeated.event,nil); equal(repeated.state.revision,4)
end)

test("two concurrent proposals require compare-and-swap at commit", function()
    local state,context=fixture()
    local rename=Ownership.propose(state,context,request(state,context,"RenameDog"))
    local transferRequest=request(state,context,"TransferDog")
    local transfer=Ownership.propose(state,context,transferRequest)
    equal(rename.expected.revision,transfer.expected.revision)
    rejected(Ownership.propose(rename.state,context,transferRequest),"Stale")
end)

for _, action in ipairs({"RenameDog","GrantHandler","RevokeHandler","TransferDog","ClaimDog"}) do
    test("handler cannot take owner action "..action,function()
        local state,context=fixture(); context.actor.accountId="Bob"; context.actor.episodeId="bob-1"
        rejected(Ownership.propose(state,context,request(state,context,action)),"Unauthorized")
    end)
end

for _, field in ipairs({"accountId","ownerAccount","role","reachable","storeRecovered","targetAccount","isAdmin"}) do
    test("payload cannot supply authority "..field,function()
        local state,context=fixture(); local req=request(state,context,"RenameDog"); req[field]="Alice"
        rejected(Ownership.propose(state,context,req),"Invalid")
    end)
end

for field, value in pairs({protocol=2,worldId="world-b",sessionId="old-session",dogId="dog-b",generation=2,revision=2,configRevision=2}) do
    test("stale envelope "..field,function()
        local state,context=fixture(); local req=request(state,context,"RenameDog"); req[field]=value
        rejected(Ownership.propose(state,context,req),field=="protocol" and "Protocol" or "Stale")
    end)
end

for _, value in ipairs({-1,0.5,math.huge,-math.huge,0/0,2147483648,"3",false,{}}) do
    test("invalid revision type/value "..tostring(value),function()
        local state,context=fixture(); local req=request(state,context,"RenameDog"); req.revision=value
        rejected(Ownership.propose(state,context,req),"Invalid")
    end)
end

for _, field in ipairs({"protocol","worldId","sessionId","dogId","generation","revision","configRevision","action","name"}) do
    test("missing request field "..field,function()
        local state,context=fixture(); local req=request(state,context,"RenameDog"); req[field]=nil
        rejected(Ownership.propose(state,context,req),field=="protocol" and "Protocol" or "Invalid")
    end)
end

for _, name in ipairs({"", "   ", "a\nname", "a\0b", "<RGB:1,0,0>", string.rep("x",49),
    string.char(192,175),string.char(237,160,128),string.char(244,144,128,128),string.char(226,128),
    "a"..string.char(226,128,174).."b", "a"..string.char(194,128),
    "a"..string.char(216,156), "a"..string.char(226,128,142), "a"..string.char(226,128,143)}) do
    test("invalid literal name "..#name,function()
        local state,context=fixture(); local req=request(state,context,"RenameDog"); req.name=name
        rejected(Ownership.propose(state,context,req),"Invalid")
    end)
end

test("valid Unicode and literal percent names",function()
    for _, name in ipairs({"Rex", "O'Neil", "100% Dog", "狼", string.rep("🐕",48)}) do equal(Guard.name(name),name) end
end)

test("same account new character retains access, never prior discoveries",function()
    local state,context=fixture(); context.actor.episodeId="alice-2"
    local discoveries={worldId=state.worldId,dogId=state.dogId,byAccount={Alice={["alice-1"]={relationship="Trusted",knownCues={Sit="Reliable"}}}}}
    local result=Projection.build(state,context,discoveries)
    equal(result.view.role,"owner"); equal(result.view.discovered,nil)
end)

test("RequireNewClaim blocks new episode and prevents foreign takeover",function()
    local state,context=fixture(); context.config.OwnerAfterCharacterDeath="RequireNewClaim"
    context.actor.episodeId="alice-2"
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Unauthorized")
    local reclaimed=Ownership.propose(state,context,request(state,context,"ClaimDog"))
    equal(reclaimed.ok,true); equal(reclaimed.state.ownerEpisode,"alice-2"); equal(next(reclaimed.state.handlers),nil)
    context.actor.accountId="Carol"; context.actor.episodeId="carol-1"
    rejected(Ownership.propose(state,context,request(state,context,"ClaimDog")),"Unauthorized")
end)

test("OwnerOnly suspends existing grants without destroying them",function()
    local state,context=fixture(); context.actor.accountId="Bob"; context.actor.episodeId="bob-1"
    equal(Projection.build(state,context,nil).view.role,"handler")
    context.config.HandlerPermissionMode="OwnerOnly"; context.config.revision=2
    equal(Projection.build(state,context,nil).view.role,"observer"); equal(state.handlers.Bob,true)
    context.config.HandlerPermissionMode="OwnerAndGranted"; context.config.revision=3
    equal(Projection.build(state,context,nil).view.role,"handler")
end)

test("account case changes do not acquire another account",function()
    local state,context=fixture(); context.actor.accountId="alice"
    equal(Projection.build(state,context,nil).view.role,"observer")
end)

test("projection copies only visible and current episode allowlists",function()
    local state,context=fixture()
    local discoveries={worldId=state.worldId,dogId=state.dogId,byAccount={Alice={["alice-1"]={relationship="Trusted",privateHistory="PRIVATE",
        knownCues={Sit="Reliable",Recall="Learning",Attack="PRIVATE"},exactHealth=17}}}}
    local before=clone(discoveries)
    local view=Projection.build(state,context,discoveries).view
    equal(view.ownerAccount,nil); equal(view.handlers,nil); equal(view.hiddenTraits,nil)
    equal(view.visible.hiddenStress,nil); equal(view.discovered.privateHistory,nil); equal(view.discovered.exactHealth,nil)
    equal(view.discovered.knownCues.Attack,nil); equal(view.discovered.knownCues.Sit,"Reliable")
    view.discovered.knownCues.Sit="CHANGED"; view.actions[1]="CHANGED"
    assert(same(discoveries,before)); equal(Projection.build(state,context,discoveries).view.actions[1],"InspectDog")
end)

test("observer receives no discovery even with an existing discovery record",function()
    local state,context=fixture(); context.actor.accountId="Carol"; context.actor.episodeId="carol-1"
    local discoveries={worldId=state.worldId,dogId=state.dogId,byAccount={Carol={["carol-1"]={relationship="Trusted"}}}}
    local view=Projection.build(state,context,discoveries).view
    equal(view.role,"observer"); equal(view.discovered,nil); equal(#view.actions,1)
end)

for _, field in ipairs({"bindingVerified","storeRecovered","visible","reachable","ownershipEnabled"}) do
    test("missing current observation fails closed "..field,function()
        local state,context=fixture(); context[field]=nil
        local expected=({bindingVerified="Recovery",storeRecovered="Recovery",visible="Unavailable",
            reachable="Unavailable",ownershipEnabled="Capability"})[field]
        rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),expected)
        if field=="reachable" or field=="ownershipEnabled" then
            equal(#Projection.build(state,context,nil).view.actions,1)
        else rejected(Projection.build(state,context,nil),expected) end
    end)
end

for _, phase in ipairs({"RESERVED","STORED_ITEM","STORED_VEHICLE","DETACHED_PENDING","TERMINAL","UNBOUND","RECOVERING","QUARANTINED"}) do
    test("inactive lifecycle refuses actions "..phase,function()
        local state,context=fixture(); state.phase=phase
        rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Recovery")
    end)
end

for _, field in ipairs({"connected","alive","reachable","consentsToTransfer","verified","episodeId"}) do
    test("transfer target requires current server facts "..field,function()
        local state,context=fixture(); context.target[field]=nil
        rejected(Ownership.propose(state,context,request(state,context,"TransferDog")),"Unavailable")
    end)
end

test("unknown schema is preserved and refused",function()
    local state,context=fixture(); state.schema=2; local before=clone(state)
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Recovery"); assert(same(state,before))
end)

test("counter exhaustion fails instead of rounding or wrapping",function()
    local state,context=fixture(); state.revision=Guard.MAX_COUNTER
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Recovery")
end)

test("malformed ACL is not reset to an empty record",function()
    local state,context=fixture(); state.handlers.Bob="true"
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Recovery")
    equal(state.handlers.Bob,"true")
end)

test("technical grant limit refuses overflow and permits revocation",function()
    local state,context=fixture(); state.handlers={}
    for n=1,Guard.MAX_HANDLERS do state.handlers["handler-"..n]=true end
    rejected(Ownership.propose(state,context,request(state,context,"GrantHandler")),"Unavailable")
    context.target.accountId="handler-1"
    equal(Ownership.propose(state,context,request(state,context,"RevokeHandler")).ok,true)
end)

test("invalid configuration never defaults to expanded access",function()
    local state,context=fixture(); context.config.HandlerPermissionMode="Everyone"
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Unavailable")
    rejected(Projection.build(state,context,nil),"Unavailable")
end)

test("disconnect and world mismatch refuse pending work",function()
    local state,context=fixture(); local req=request(state,context,"RenameDog")
    context.actor.connected=false; rejected(Ownership.propose(state,context,req),"Unavailable")
    context.actor.connected=true; context.worldId="other-world"; rejected(Ownership.propose(state,context,req),"Unavailable")
end)

test("malformed inputs and metatables never execute callbacks",function()
    local state,context=fixture()
    for _, value in ipairs({true,7,"text",{}}) do
        equal(Ownership.propose(value,context,{}).ok,false)
        equal(Ownership.propose(state,value,{}).ok,false)
        equal(Ownership.propose(state,context,value).ok,false)
    end
    local hostile=setmetatable({}, {__index=function() error("metatable executed") end})
    equal(Ownership.propose(hostile,context,{}).ok,false)
    equal(Ownership.propose(state,context,hostile).ok,false)
    rejected(Projection.build(state,context,hostile),"Recovery")
end)

test("unexpected ownership fields are preserved and refused",function()
    local state,context=fixture(); state.futureField={value="preserve"}
    rejected(Ownership.propose(state,context,request(state,context,"RenameDog")),"Recovery")
    equal(state.futureField.value,"preserve")
end)

for _, field in ipairs({"worldId","dogId"}) do
    test("discoveries cannot cross "..field,function()
        local state,context=fixture()
        local data={worldId=state.worldId,dogId=state.dogId,byAccount={Alice={["alice-1"]={relationship="Trusted"}}}}
        data[field]="foreign"
        rejected(Projection.build(state,context,data),"Recovery")
    end)
end

return {passed=passed, failed=failed, failures=failures}
