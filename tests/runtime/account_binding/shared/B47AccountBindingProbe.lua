-- Disposable diagnostic only. No principal provider, persistence or authority.
local Probe = {}

local function method(object, name)
    if object == nil then return nil end
    local ok, value = pcall(function() return object[name] end)
    if ok and type(value) == 'function' then return value end
    return nil
end

local function invoke(object, name, ...)
    local fn = method(object, name)
    if not fn then return false, nil, 'API_ABSENT' end
    local ok, value = pcall(fn, object, ...)
    if not ok then return false, nil, 'CALL_ERROR' end
    return true, value
end

local function association(connection, actor, slot)
    if connection == nil then return {status='NO_CONNECTION'} end
    local ok, current, why = invoke(connection, 'getPlayerAt', slot)
    if not ok then return {status='MEMBERSHIP_'..why} end
    if current ~= actor then return {status='SLOT_MISMATCH'} end
    local rootOK, root, rootWhy = invoke(connection, 'getUserName')
    if not rootOK then return {status='ROOT_'..rootWhy} end
    if type(root) ~= 'string' or root == '' then return {status='INVALID_ROOT'} end
    local nameOK, name = invoke(actor, 'getUsername')
    -- Return comparisons only; never retain names, account IDs or the connection.
    local result={status='OBSERVED_UNPROVEN'}
    if nameOK and type(name) == 'string' and name ~= '' then result.rootMatchesActor=root == name end
    return result
end

local function staticRoute(receiver, name, argument, actor, slot)
    local fn = method(receiver, name)
    if not fn then return {status='API_ABSENT'} end
    local ok, connection = pcall(fn, argument)
    if not ok then return {status='LOOKUP_ERROR'} end
    return association(connection, actor, slot)
end

function Probe.sample(env, actor)
    local result = {authority='UNPROVEN', ownership=false, liveTaskControl=false,
        actorCurrent=false, gameServer={status='NOT_CHECKED'},
        chatUtility={status='NOT_CHECKED'}, playerOwner={status='NOT_CHECKED'}}
    if type(env.isServer) ~= 'function' or not env.isServer() then
        result.status='SERVER_REQUIRED'; return result
    end
    local slotOK, slot = invoke(actor, 'getPlayerNum')
    local idOK, id = invoke(actor, 'getOnlineID')
    if not slotOK or type(slot) ~= 'number' or slot ~= math.floor(slot) or slot < 0 or slot > 3
        or not idOK or type(id) ~= 'number' or id ~= math.floor(id) or id < 0 or id > 32767 then
        result.status='INVALID_ACTOR'; return result
    end
    if type(env.getPlayerByOnlineID) ~= 'function' then
        result.status='ACTOR_LOOKUP_ABSENT'; return result
    end
    local ok, current = pcall(env.getPlayerByOnlineID, id)
    if not ok then result.status='ACTOR_LOOKUP_ERROR'; return result end
    if current ~= actor then result.status='STALE_ACTOR'; return result end
    result.actorCurrent=true
    result.status='DIAGNOSTIC_ONLY'
    result.gameServer=staticRoute(env.GameServer, 'getConnectionFromPlayer', actor, actor, slot)
    result.chatUtility=staticRoute(env.ChatUtility, 'findConnection', id, actor, slot)
    local ownerOK, owner, ownerWhy = invoke(actor, 'getOwner')
    result.playerOwner=ownerOK and association(owner, actor, slot) or {status='OWNER_'..ownerWhy}
    return result
end

local function caseLabel(value)
    return type(value) == 'string' and value:match('^AC0[1-9]$')
        or type(value) == 'string' and value:match('^AC1[0-2]$')
end

function Probe.install(env)
    if type(env.isServer) ~= 'function' or not env.isServer() then return nil, 'SERVER_REQUIRED' end
    if env.B47AccountBindingProbeInstalled then return nil, 'ALREADY_INSTALLED' end
    local event = env.Events and env.Events.OnClientCommand
    if not event or type(event.Add) ~= 'function' or type(env.print) ~= 'function' then
        return nil, 'EVENT_OR_LOG_ABSENT'
    end
    local count = 0 -- Technical log cap for a disposable experiment, not a gameplay setting.
    local function onCommand(module, command, actor, args)
        if module ~= 'B47AccountBindingProbe' or command ~= 'sample' then return end
        if count >= 64 or type(args) ~= 'table' or not caseLabel(args.case) then return end
        count=count+1
        local r=Probe.sample(env, actor) -- All supplied identity/role/connection fields are ignored.
        local function route(name)
            local v=r[name]
            local comparison=v.rootMatchesActor == nil and 'UNAVAILABLE' or tostring(v.rootMatchesActor)
            return name..'='..v.status..':rootMatchesActor='..comparison
        end
        env.print('[B47AccountBindingProbe] case='..args.case..' sample='..count..' status='..r.status
            ..' actorCurrent='..tostring(r.actorCurrent)..' '..route('gameServer')..' '
            ..route('chatUtility')..' '..route('playerOwner')..' authority=UNPROVEN ownership=false tasks=false')
    end
    event.Add(onCommand)
    env.B47AccountBindingProbeInstalled=true
    env.print('[B47AccountBindingProbe] installed; disposable diagnostic; no persisted identity; 64 samples maximum')
    return onCommand
end

return Probe
