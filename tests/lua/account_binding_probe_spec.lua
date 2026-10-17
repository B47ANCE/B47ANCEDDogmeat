local Probe=require 'B47AccountBindingProbe'
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,err=pcall(fn)
    if ok then passed=passed+1 else failed=failed+1; failures[#failures+1]=name..': '..tostring(err) end
end
local function eq(a,b) assert(a==b,'expected '..tostring(b)..', got '..tostring(a)) end
local function fixture()
    local actor={getPlayerNum=function() return 0 end, getOnlineID=function() return 12 end,
        getUsername=function() return 'PRIVATE_SLOT' end, getOwner=function() return nil end}
    local connection={getPlayerAt=function(_,slot) if slot==0 then return actor end end,
        getUserName=function() return 'PRIVATE_ROOT' end}
    local logs,handlers={},{}
    local env={isServer=function() return true end,getPlayerByOnlineID=function(id) if id==12 then return actor end end,
        Events={OnClientCommand={Add=function(fn) handlers[#handlers+1]=fn end}},
        print=function(s) logs[#logs+1]=s end}
    return env,actor,connection,logs,handlers
end

test('vanilla-shaped absent globals and nil owner refuse association',function()
    local e,a=fixture();local r=Probe.sample(e,a)
    eq(r.gameServer.status,'API_ABSENT');eq(r.chatUtility.status,'API_ABSENT');eq(r.playerOwner.status,'NO_CONNECTION')
    eq(r.authority,'UNPROVEN');eq(r.ownership,false);eq(r.liveTaskControl,false)
end)
test('matching slot observes different root without treating alias as identity',function()
    local e,a,c=fixture();e.GameServer={getConnectionFromPlayer=function(actor) eq(actor,a);return c end}
    local r=Probe.sample(e,a);eq(r.gameServer.status,'OBSERVED_UNPROVEN');eq(r.gameServer.rootMatchesActor,false)
    eq(r.authority,'UNPROVEN')
    a.getUsername=function() error('PRIVATE_EXCEPTION') end
    eq(Probe.sample(e,a).gameServer.rootMatchesActor,nil)
end)
test('equal root and alias still never authenticate or persist',function()
    local e,a,c=fixture();a.getUsername=function() return 'PRIVATE_ROOT' end
    e.ChatUtility={findConnection=function(id) eq(id,12);return c end}
    local r=Probe.sample(e,a);eq(r.chatUtility.rootMatchesActor,true);eq(r.authority,'UNPROVEN')
end)
test('reused online ID cannot substitute an old actor',function()
    local e,a=fixture();e.getPlayerByOnlineID=function() return {} end
    eq(Probe.sample(e,a).status,'STALE_ACTOR')
end)
test('wrong connection member refuses even with identical account text',function()
    local e,a,c=fixture();c.getPlayerAt=function() return {getUsername=a.getUsername} end
    a.getOwner=function() return c end;eq(Probe.sample(e,a).playerOwner.status,'SLOT_MISMATCH')
end)
test('co-op slot uses exact slot membership',function()
    local e,a,c=fixture();a.getPlayerNum=function() return 2 end
    c.getPlayerAt=function(_,slot) if slot==2 then return a end end
    e.GameServer={getConnectionFromPlayer=function() return c end}
    eq(Probe.sample(e,a).gameServer.status,'OBSERVED_UNPROVEN')
end)
for _,bad in ipairs({-1,4,0.5,math.huge,'0'}) do
    test('invalid slot rejects '..tostring(bad),function()
        local e,a=fixture();a.getPlayerNum=function() return bad end;eq(Probe.sample(e,a).status,'INVALID_ACTOR')
    end)
end
test('nil actor refuses',function() local e=fixture();eq(Probe.sample(e,nil).status,'INVALID_ACTOR') end)
test('client context cannot install or sample',function()
    local e,a=fixture();e.isServer=function() return false end
    eq(Probe.sample(e,a).status,'SERVER_REQUIRED');local fn,why=Probe.install(e);eq(fn,nil);eq(why,'SERVER_REQUIRED')
end)
test('unexposed userdata-style indexing is reported without reflection',function()
    local e,a=fixture();e.GameServer=setmetatable({}, {__index=function() error('PRIVATE_EXCEPTION') end})
    eq(Probe.sample(e,a).gameServer.status,'API_ABSENT')
end)
test('native lookup errors have a fixed redacted diagnostic',function()
    local e,a=fixture();e.GameServer={getConnectionFromPlayer=function() error('PRIVATE_EXCEPTION') end}
    eq(Probe.sample(e,a).gameServer.status,'LOOKUP_ERROR')
end)
test('opaque connection without readable membership refuses',function()
    local e,a=fixture();a.getOwner=function() return {} end
    eq(Probe.sample(e,a).playerOwner.status,'MEMBERSHIP_API_ABSENT')
end)
test('missing root method refuses',function()
    local e,a,c=fixture();c.getUserName=nil;a.getOwner=function() return c end
    eq(Probe.sample(e,a).playerOwner.status,'ROOT_API_ABSENT')
end)
test('empty root refuses',function()
    local e,a,c=fixture();c.getUserName=function() return '' end;a.getOwner=function() return c end
    eq(Probe.sample(e,a).playerOwner.status,'INVALID_ROOT')
end)
test('installation is idempotent',function()
    local e,a,c,logs,handlers=fixture();assert(Probe.install(e));local fn,why=Probe.install(e)
    eq(fn,nil);eq(why,'ALREADY_INSTALLED');eq(#handlers,1);eq(#logs,1)
end)
test('forged identity fields never affect route or enter logs',function()
    local e,a,c,logs=fixture();local fn=assert(Probe.install(e))
    fn('B47AccountBindingProbe','sample',a,{case='AC02',username='SECRET_FORGED',root='SECRET_FORGED',
        principalId='SECRET_FORGED',connection=c,role='admin'})
    eq(#logs,2);assert(logs[2]:find('gameServer=API_ABSENT',1,true))
    assert(not logs[2]:find('PRIVATE',1,true));assert(not logs[2]:find('SECRET',1,true))
end)
test('malformed requests cannot inject log text',function()
    local e,a,c,logs=fixture();local fn=assert(Probe.install(e))
    for _,v in ipairs({'AC13','AC01\nSECRET','ac01','AC1',''}) do fn('B47AccountBindingProbe','sample',a,{case=v}) end
    fn('B47AccountBindingProbe','sample',a,nil);fn('other','sample',a,{case='AC01'})
    fn('B47AccountBindingProbe','other',a,{case='AC01'});eq(#logs,1)
end)
test('fixed experiment budget bounds log and lookup work',function()
    local e,a,c,logs=fixture();local fn=assert(Probe.install(e));local calls=0
    e.getPlayerByOnlineID=function() calls=calls+1;return a end
    for i=1,100 do fn('B47AccountBindingProbe','sample',a,{case='AC01'}) end
    eq(calls,64);eq(#logs,65)
end)
test('fresh probe installation retains no prior session actor association',function()
    local e,a=fixture();assert(Probe.install(e));local nextEnv,nextActor=fixture();assert(Probe.install(nextEnv))
    eq(Probe.sample(nextEnv,a).status,'STALE_ACTOR');eq(Probe.sample(nextEnv,nextActor).authority,'UNPROVEN')
end)
test('actual server bootstrap installs once without sampling a player',function()
    local e,a,c,logs,handlers=fixture();e._G=e;setmetatable(e,{__index=_G})
    local boot=assert(loadstring(test_account_probe_bootstrap));setfenv(boot,e);boot();boot()
    eq(#handlers,1);eq(#logs,1)
end)
test('actual client helper sends only explicit case and selected current player',function()
    local e,a=fixture();local sent={}
    e.getSpecificPlayer=function(slot) eq(slot,2);return a end
    e.sendClientCommand=function(player,module,command,args)
        eq(player,a);eq(module,'B47AccountBindingProbe');eq(command,'sample')
        eq(args.case,'AC05');for key in pairs(args) do eq(key,'case') end;sent[#sent+1]=true
    end
    setmetatable(e,{__index=_G});local client=assert(loadstring(test_account_probe_client));setfenv(client,e);client()
    eq(#sent,0);e.B47AccountBindingSample('AC05',2);eq(#sent,1)
    eq(pcall(e.B47AccountBindingSample,'AC13',2),false);eq(pcall(e.B47AccountBindingSample,'AC05',4),false)
    eq(#sent,1)
end)

return {passed=passed,failed=failed,failures=failures}
