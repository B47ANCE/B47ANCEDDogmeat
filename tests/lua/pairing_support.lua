local S=require "storage_support"
local P={}
function P.fixture()
    local api,flags,calls=S.api()
    flags.anchor={schema=1,worldId=S.WORLD,checkpoint=S.FIRST}
    flags.animals={(S.animal())}
    calls.modReads=0;calls.census=0;calls.censusReads=0
    api.ModData={get=function(namespace)
        assert(namespace=="FixtureDogs");calls.modReads=calls.modReads+1
        return flags.anchor
    end}
    api.getCell=function()
        if flags.missingCell then return nil end
        return {getAnimals=function()
            calls.census=calls.census+1
            return {size=function() return flags.animalCount or #flags.animals end,
                get=function(_,index) calls.censusReads=calls.censusReads+1;return flags.animals[index+1] end}
        end}
    end
    local callbacks={}
    api.Events={}
    for _,name in ipairs({"OnInitGlobalModData","OnServerStarted","OnGameStart","OnCharacterDeath",
        "OnSave","OnPostSave","OnReceiveGlobalModData"}) do
        callbacks[name]={}
        api.Events[name]={Add=function(callback)
            if flags.registrationFailure==name then error("fixture registration failure") end
            callbacks[name][#callbacks[name]+1]=callback
        end}
    end
    local function fire(name,...)
        for _,callback in ipairs(callbacks[name]) do callback(...) end
    end
    return api,flags,calls,fire,callbacks
end
function P.config() return {namespace="FixtureDogs",allowedTypes={FixtureCanine={FixtureShepherd=true}}} end
function P.request()
    return {worldId=S.WORLD,sessionId="fixture-session",visible=true,reachable=true,ownershipEnabled=true,
        actor={accountId="Alice",episodeId="alice-1",connected=true,alive=true},
        config={revision=1,HandlerPermissionMode="OwnerAndGranted",OwnerAfterCharacterDeath="RetainAccountAccess"}},
        {protocol=1,worldId=S.WORLD,sessionId="fixture-session",dogId=S.DOG,generation=1,
            revision=3,configRevision=1,action="RenameDog",name="Native paired name"}
end
return P
