-- Pure Lua 5.1. No engine calls, persistence, event registration or client globals.
local Guard = {}
Guard.MAX_COUNTER = 2147483647 -- Exact bounded protocol counter; refuse rollover.
Guard.MAX_HANDLERS = 64 -- Defensive record/packet limit, not a progression setting.

function Guard.plain(value)
    return type(value) == "table" and getmetatable(value) == nil
end

function Guard.integer(value, minimum)
    return type(value) == "number" and value == value and value >= minimum
        and value <= Guard.MAX_COUNTER and value == math.floor(value)
end

function Guard.id(value)
    return type(value) == "string" and #value > 0 and #value <= 128
        and not value:find("[%z\1-\31\127]") and value:find("%S") ~= nil
end

-- Validate UTF-8 explicitly: Kahlua/Lua 5.1 has no standard utf8 library.
-- Names are literal text. A future UI must use a plain-text widget, not markup.
function Guard.name(value)
    if type(value) ~= "string" or #value == 0 or #value > 192 then return nil end
    local name = value:match("^ *(.-) *$")
    if name == "" or name:find("[<>]") then return nil end
    local index, count = 1, 0
    while index <= #name do
        local first = name:byte(index)
        local length, point, minimum
        if first < 128 then length, point, minimum = 1, first, 0
        elseif first >= 194 and first <= 223 then length, point, minimum = 2, first - 192, 128
        elseif first >= 224 and first <= 239 then length, point, minimum = 3, first - 224, 2048
        elseif first >= 240 and first <= 244 then length, point, minimum = 4, first - 240, 65536
        else return nil end
        for offset = 1, length - 1 do
            local byte = name:byte(index + offset)
            if not byte or byte < 128 or byte > 191 then return nil end
            point = point * 64 + byte - 128
        end
        if point < minimum or point > 1114111 or (point >= 55296 and point <= 57343)
            or point < 32 or (point >= 127 and point <= 159)
            or point == 1564 or point == 8206 or point == 8207
            or (point >= 8232 and point <= 8238) or (point >= 8294 and point <= 8297)
            or point == 8203 or point == 65279 then return nil end
        count, index = count + 1, index + length
        if count > 48 then return nil end
    end
    return name
end

local phases = { LIVE=true, RESERVED=true, STORED_ITEM=true, STORED_VEHICLE=true,
    DETACHED_PENDING=true, TERMINAL=true, UNBOUND=true, RECOVERING=true, QUARANTINED=true }
local stateFields = {schema=true, worldId=true, dogId=true, generation=true, revision=true,
    aclRevision=true, phase=true, name=true, ownerAccount=true, ownerEpisode=true, handlers=true}

function Guard.state(state)
    if not Guard.plain(state) or state.schema ~= 1 or not Guard.id(state.worldId)
        or not Guard.id(state.dogId) or not Guard.integer(state.generation, 1)
        or not Guard.integer(state.revision, 0) or not Guard.integer(state.aclRevision, 0)
        or state.aclRevision > state.revision or not phases[state.phase]
        or not Guard.plain(state.handlers) then return false end
    for key in pairs(state) do if not stateFields[key] then return false end end
    if state.name ~= nil and Guard.name(state.name) ~= state.name then return false end
    if state.ownerAccount == nil then
        if state.ownerEpisode ~= nil or next(state.handlers) ~= nil then return false end
    elseif not Guard.id(state.ownerAccount) or not Guard.id(state.ownerEpisode) then return false end
    local count = 0
    for account, grant in pairs(state.handlers) do
        count = count + 1
        if count > Guard.MAX_HANDLERS or not Guard.id(account) or grant ~= true
            or account == state.ownerAccount then return false end
    end
    return true
end

function Guard.context(context)
    if not Guard.plain(context) or not Guard.id(context.worldId) or not Guard.id(context.sessionId)
        or not Guard.plain(context.actor) or not Guard.id(context.actor.accountId)
        or not Guard.id(context.actor.episodeId) or context.actor.connected ~= true
        or context.actor.alive ~= true or not Guard.plain(context.config)
        or not Guard.integer(context.config.revision, 0) then return false end
    local config = context.config
    return (config.HandlerPermissionMode == "OwnerOnly" or config.HandlerPermissionMode == "OwnerAndGranted")
        and (config.OwnerAfterCharacterDeath == "RetainAccountAccess"
            or config.OwnerAfterCharacterDeath == "RequireNewClaim")
end

function Guard.ready(state, context)
    if not Guard.state(state) then return "Recovery" end
    if not Guard.context(context) then return "Unavailable" end
    if context.worldId ~= state.worldId then return "Unavailable" end
    if state.phase ~= "LIVE" or context.bindingVerified ~= true or context.storeRecovered ~= true then
        return "Recovery"
    end
    if context.visible ~= true then return "Unavailable" end
    return nil
end

function Guard.copyState(state)
    -- This is the OWNERSHIP subrecord only. The adapter must preserve other domains.
    local result = { schema=state.schema, worldId=state.worldId, dogId=state.dogId,
        generation=state.generation, revision=state.revision, aclRevision=state.aclRevision,
        phase=state.phase, name=state.name, ownerAccount=state.ownerAccount,
        ownerEpisode=state.ownerEpisode, handlers={} }
    for account in pairs(state.handlers) do result.handlers[account] = true end
    return result
end

return Guard
