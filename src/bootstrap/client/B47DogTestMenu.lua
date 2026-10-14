require "ISUI/ISModalDialog"
local pending
local request
local keys={Disabled=true,Unavailable=true,Invalid=true,Busy=true,Recovery=true,
    WAITING_INITIAL_NATIVE_RELOAD=true,WAITING_NATIVE_RELOAD=true,Loaded=true}
local function show(player,text,yesno,callback)
    local modal=ISModalDialog:new(0,0,420,190,text,yesno,nil,callback,player:getPlayerNum())
    modal:initialise();modal:addToUIManager()
    if player:getJoypadBind()~=-1 then setJoypadFocus(player:getPlayerNum(),modal) end
end
local function receive(result)
    local player=pending
    if not player or type(result)~="table" or result.playerId~=player:getOnlineID() then return end
    pending=nil
    if result.status=="NeedsInitialization" and type(result.challenge)=="string" and #result.challenge==36 then
        show(player,getText("UI_B47ANCEDDogmeat_TestConfirm"),true,function(_,button)
            if button.internal=="YES" then
                request(player,"Provision",{protocol=1,challenge=result.challenge,ack="NEW_DISPOSABLE_WORLD"})
            end
        end)
    elseif keys[result.status] then
        local text=getText("UI_B47ANCEDDogmeat_Test_"..result.status)
        if result.status=="Loaded" then
            text=getText("UI_B47ANCEDDogmeat_Test_Loaded",tonumber(result.matched) or 0,tonumber(result.other) or 0,
                type(result.dogId)=="string" and result.dogId or "-")
        end
        show(player,text,false,nil)
    end
end
request=function(player,command,args)
    pending=player
    if isClient() then sendClientCommand(player,"B47ANCEDDogmeat",command,args)
    elseif B47DogLocalTest then receive(B47DogLocalTest(player,command,args)) end
end
Events.OnServerCommand.Add(function(module,command,args)
    if module=="B47ANCEDDogmeat" and command=="Result" then receive(args) end
end)
Events.OnFillWorldObjectContextMenu.Add(function(playerIndex,context,worldobjects,test)
    if test then return end
    local player=getSpecificPlayer(playerIndex)
    local settings=SandboxVars.B47ANCEDDogmeat
    if not player or player:isDead() or not settings or settings.PersistenceTestMode~=true then return end
    local ok,allowed=pcall(function()
        return not isClient() or player:getRole():hasCapability(Capability.AnimalCheats)==true
    end)
    if not ok or not allowed then return end
    context:addOption(getText("UI_B47ANCEDDogmeat_TestMenu"),player,function(actor)
        request(actor,"Inspect",{protocol=1})
    end)
end)
