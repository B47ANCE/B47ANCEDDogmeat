local F=require "provision_support"
local A=require "admission_support"
local passed,failed,failures=0,0,{}
local function test(name,fn)
    local ok,err=pcall(fn);if ok then passed=passed+1 else failed=failed+1;failures[#failures+1]=name..": "..tostring(err) end
end
local function fixture(single)
    local api,flags,calls,fire,config,player=F.fixture("BootstrapFixture"..(F.counter+1),true)
    flags.server=not single
    function player:getOnlineID() return 7 end
    function player:getPlayerNum() return 0 end
    function player:getJoypadBind() return -1 end
    api.Events.OnClientCommand={Add=function(fn) flags.command=fn end}
    api.Events.OnServerCommand={Add=function(fn) flags.reply=fn end}
    api.Events.OnFillWorldObjectContextMenu={Add=function(fn) flags.menu=fn end}
    for key,value in pairs(api) do _G[key]=value end
    B47DogLocalTest=nil
    package.loaded.B47DogRegistration=config
    getSpecificPlayer=function(index) if index==0 then return player end end
    getText=function(key) return key end
    sendServerCommand=function(target,module,command,args)
        assert(target==player and module=="B47ANCEDDogmeat" and command=="Result")
        flags.lastReply=args;if flags.reply then flags.reply(module,command,args) end
    end
    sendClientCommand=function(target,module,command,args)
        -- Simulate crossing into the separate dedicated authority process.
        local client,server=flags.client,flags.server
        flags.client=false;flags.server=true
        flags.command(module,command,target,args)
        flags.client=client;flags.server=server
    end
    package.preload["ISUI/ISModalDialog"]=function() return true end
    for _,name in ipairs(A.names) do
        local path="TimedActions/"..((name=="ISDropWorldItemAction" or name=="ISDropVehicleItemAction") and "" or "Animals/")..name
        package.preload[path]=function() return true end
    end
    ISModalDialog={new=function(_,x,y,w,h,text,yesno,target,onclick,index)
        assert(index==0)
        local modal={text=text,yesno=yesno,callback=onclick,target=target,
            initialise=function() end,addToUIManager=function() end}
        flags.modal=modal;return modal
    end}
    return api,flags,calls,fire,config,player
end
for _,single in ipairs({false,true}) do
    test("bootstrap menu challenge and immediate confirmation "..tostring(single),function()
        local api,flags,calls,fire,config,player=fixture(single)
        assert(loadstring(test_bootstrap_server))()
        assert(loadstring(test_bootstrap_client))()
        fire("OnInitGlobalModData",true);fire(single and "OnGameStart" or "OnServerStarted")
        if not single then flags.client=true;flags.server=false end
        local action
        local context={addOption=function(_,label,target,callback) action=function() callback(target) end end}
        flags.menu(0,context,{},false);assert(action);action()
        assert(flags.modal.yesno and flags.modal.text=="UI_B47ANCEDDogmeat_TestConfirm")
        flags.modal.callback(nil,{internal="YES"})
        assert(calls.spawns==1 and flags.anchor and flags.modal.text=="UI_B47ANCEDDogmeat_Test_WAITING_INITIAL_NATIVE_RELOAD")
        if single then assert(B47DogLocalTest) else assert(B47DogLocalTest==nil) end
    end)
end
test("declining confirmation does not provision",function()
    local api,flags,calls,fire=fixture(true)
    assert(loadstring(test_bootstrap_server))();assert(loadstring(test_bootstrap_client))()
    fire("OnInitGlobalModData");fire("OnGameStart")
    local action
    flags.menu(0,{addOption=function(_,_,target,callback) action=function() callback(target) end end},{},false)
    action();flags.modal.callback(nil,{internal="NO"})
    assert(calls.writes==0 and calls.spawns==0)
end)
test("remote-client server bootstrap installs no authority",function()
    local api,flags,calls=fixture(false);flags.client=true
    assert(loadstring(test_bootstrap_server))()
    assert(flags.command==nil and B47DogLocalTest==nil and calls.writes==0)
end)
return {passed=passed,failed=failed,failures=failures}
