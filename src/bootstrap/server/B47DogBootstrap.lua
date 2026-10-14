if isClient() then return end
local config=require "B47DogRegistration"
local Runtime=require "B47Dog/NativeRuntime"
local Service=require "B47Dog/NativeTestService"
-- Explicit SP adapter, preserving the real native isServer/isClient functions.
local api=setmetatable({B47DogSinglePlayer=isServer()==false},{__index=_G})
local runtime,reason=Runtime.install({namespace=config.namespace,
    allowedTypes={[config.nativeType]={[config.breed]=true}}},api)
if not runtime then error("B47ANCEDDogmeat: bootstrap refused "..tostring(reason)) end
local service=Service.new(config,runtime,api)
local function handle(player,command,args)
    local ok,result=pcall(service.handle,player,command,args)
    if not ok then result={status="Recovery"} end
    if result then result.playerId=player:getOnlineID() end
    if result and isServer() then sendServerCommand(player,"B47ANCEDDogmeat","Result",result) end
    return result
end
Events.OnClientCommand.Add(function(module,command,player,args)
    if module=="B47ANCEDDogmeat" and isServer() then handle(player,command,args) end
end)
-- Only the local SP client uses this; remote clients have no authority bootstrap.
if api.B47DogSinglePlayer then B47DogLocalTest=handle end
