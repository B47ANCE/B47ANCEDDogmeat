-- Server completion guards for the restricted live-world carrier. These guards
-- close known Lua representation transitions, not all native admission paths.
-- In particular, this module never certifies a native ID or grants ownership.
local Guard=require "B47Dog/Guard"
local Codec=require "B47Dog/Codec"
local Identity=require "B47Dog/Identity"
local Authority=require "B47Dog/NativeAuthority"
local Policy=require "B47Dog/AdmissionPolicy"
local Admission={}
local installed=setmetatable({},{__mode="k"})
local owners=setmetatable({},{__mode="k"})
-- API adapters may be recreated around the same native server function. Key the
-- one-shot reservation there too, so a new table cannot erase a failed attempt.
local processes=setmetatable({},{__mode="k"})
local contract="LUA_WORLD_CARRIER_GUARD_1"
local hooks={
    {name="ISPickupAnimal",source="animal"},
    {name="ISAddAnimalInTrailer",source="animal",corpse=true},
    {name="ISRemoveAnimalFromTrailer",source="animal",corpse=true},
    {name="ISAttachAnimalToPlayer",source="animal"},
    {name="ISAttachAnimalToTree",source="animal"},
    {name="ISPutAnimalInHutch",source="hand"},
    {name="ISHutchGrabAnimal",source="hutch"},
    {name="ISDropWorldItemAction",source="item"},
    {name="ISDropVehicleItemAction",source="item"}
}

function Admission.current(config,api)
    local item=installed[api]
    local signature=Codec.encode(config)
    if item and signature and item.signature==signature then return item.controller end
end

function Admission.active(namespace,nativeType,api)
    local item=installed[api]
    if not item or item.namespace~=namespace or not item.types[nativeType] then return false end
    return item.controller.check()==true
end

function Admission.install(config,api)
    if not Identity.keys(config,{namespace=true,allowedTypes=true}) or type(api)~="table"
        or type(config.namespace)~="string" or #config.namespace>64
        or not config.namespace:match("^[A-Za-z][A-Za-z0-9_]*$")
        or not Guard.plain(config.allowedTypes) or not Authority.allowed(api)
        or type(api.instanceof)~="function" then return nil,"Unavailable" end
    local signature=Codec.encode(config)
    if not signature then return nil,"Invalid" end
    local frozen=Codec.decode(signature)
    local types,count={},0
    for kind,breeds in pairs(frozen.allowedTypes) do
        if not Guard.id(kind) or not Guard.plain(breeds) or next(breeds)==nil then return nil,"Invalid" end
        for breed,value in pairs(breeds) do
            if not Guard.id(breed) or value~=true then return nil,"Invalid" end
        end
        count=count+1;types[kind]=true
    end
    if count==0 or count>16 then return nil,"Invalid" end
    if installed[api] then return nil,"AlreadyInstalled" end
    if processes[api.isServer] then return nil,"GuardProcessReserved" end
    local serverFunction,clientFunction,instanceFunction=api.isServer,api.isClient,api.instanceof
    local phase,reason="INSTALLING",nil
    local captured={}
    local controller={}
    local function close(why)
        if phase~="RECOVERY" then phase="RECOVERY";reason=why end
        return nil,reason
    end
    -- Reserve before checking/installing hooks. Partial installs cannot be retried
    -- or silently repaired in a live process, even if another mod restores a table.
    installed[api]={signature=signature,namespace=config.namespace,types=types,controller=controller}
    processes[serverFunction]=controller
    function controller.check()
        if phase=="RECOVERY" then return nil,reason end
        local authorityOK,authoritative=pcall(function()
            return Authority.allowed(api) and api.isServer==serverFunction and api.isClient==clientFunction
                and api.instanceof==instanceFunction
        end)
        if not authorityOK or not authoritative then return close("GuardAuthorityLost") end
        local ok,intact=pcall(function()
            for _,item in ipairs(captured) do
                if api[item.name]~=item.class or rawget(item.class,"new")~=item.new
                    or rawget(item.class,"complete")~=item.wrapper
                    or rawget(item.class,"__index")~=item.class
                    or getmetatable(item.class)~=item.metatable then return false end
            end
            return true
        end)
        if not ok then return close("GuardInspectionFailed") end
        if not intact then return close("GuardDisplaced") end
        if phase~="GUARDED" or #captured~=#hooks then return close("GuardIncomplete") end
        return true
    end
    function controller.status()
        controller.check()
        return {phase=phase,reason=reason,contract=contract,guardedActions=#captured,
            coverage="LUA_ACTIONS_ONLY",ownershipReady=false}
    end
    -- Native parser ghosts may be detached/dead/markerless. Do not require world
    -- presence, a public marker or a private match before refusing their transport.
    local function allowedAnimal(animal,corpse)
        if corpse and api.instanceof(animal,"IsoDeadBody")==true then return true end
        if api.instanceof(animal,"IsoAnimal")~=true then return false end
        local kind=animal:getAnimalType()
        local decision=Policy.transition(frozen.allowedTypes,kind)
        return decision.decision=="DEFER" and decision.reason=="Unmanaged" and decision.managed==false
    end
    local function allowedItem(item)
        if api.instanceof(item,"InventoryItem")~=true then return false end
        if api.instanceof(item,"AnimalInventoryItem")~=true then return true end
        return allowedAnimal(item:getAnimal(),false)
    end
    local function allowedAction(spec,action)
        if type(action)~="table" then return false end
        if spec.source=="animal" then return allowedAnimal(action.animal,spec.corpse) end
        if spec.source=="item" then return allowedItem(action.item) end
        if spec.source=="hand" then
            if api.instanceof(action.character,"IsoPlayer")~=true then return false end
            local item=action.character:getPrimaryHandItem()
            return api.instanceof(item,"AnimalInventoryItem")==true and allowedItem(item)
        end
        if spec.source=="hutch" then
            -- The native hutch lookup is an integer-keyed map, not a list index.
            if api.instanceof(action.hutch,"IsoHutch")~=true or not Guard.integer(action.index,0) then return false end
            return allowedAnimal(action.hutch:getAnimal(action.index),false)
        end
        return false
    end
    -- Inspect the entire set first. Constructors keep their original identity and
    -- parameter metadata: NetTimedAction serializes from their Lua prototypes.
    local seenClasses={}
    for _,spec in ipairs(hooks) do
        local class=api[spec.name]
        if type(class)~="table" or type(rawget(class,"new"))~="function"
            or type(rawget(class,"complete"))~="function" then
            close("GuardMissingHook");return nil,"GuardMissingHook"
        end
        if owners[class] then close("GuardHookOwned");return nil,"GuardHookOwned" end
        if seenClasses[class] then close("GuardAliasedHook");return nil,"GuardAliasedHook" end
        if rawget(class,"__index")~=nil and rawget(class,"__index")~=class then
            close("GuardClassShape");return nil,"GuardClassShape"
        end
        seenClasses[class]=true
        captured[#captured+1]={name=spec.name,class=class,new=rawget(class,"new"),
            original=rawget(class,"complete"),metatable=getmetatable(class),spec=spec}
    end
    for _,item in ipairs(captured) do
        item.wrapper=function(action,...)
            if controller.check()~=true then return false end
            local ok,allow=pcall(allowedAction,item.spec,action)
            -- Invalid requests never reach vanilla. Refusal itself does not poison
            -- the session: a remote malformed intent must not disable all dogs.
            if not ok or allow~=true then return false end
            if controller.check()~=true then return false end
            local completed,result=pcall(item.original,action,...)
            if not completed then
                close("GuardMutationFailed")
                error(result,0) -- retain the actual native/Lua error for diagnostics
            end
            -- An uncertain delegated mutation is never retried or reported true.
            if controller.check()~=true then return false end
            return result
        end
    end
    local ok=pcall(function()
        for _,item in ipairs(captured) do
            owners[item.class]=controller
            -- Same index assignment as vanilla ISBaseTimedAction.new, done once
            -- before clients can construct actions; subsequent changes are drift.
            rawset(item.class,"__index",item.class)
            rawset(item.class,"complete",item.wrapper)
        end
    end)
    if not ok then close("GuardInstallationFailed");return nil,"GuardInstallationFailed" end
    phase="GUARDED"
    local ready,why=controller.check()
    if not ready then return nil,why end
    return controller
end

return Admission
