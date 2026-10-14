local Guard = require "B47Dog/Guard"
local Access = require "B47Dog/Access"
local Ownership = {}

local common = { protocol=true, worldId=true, sessionId=true, dogId=true,
    generation=true, revision=true, configRevision=true, action=true }
local actionFields = { ClaimDog={}, RenameDog={name=true}, GrantHandler={targetRef=true},
    RevokeHandler={targetRef=true}, TransferDog={targetRef=true} }

local function refuse(reason) return { ok=false, reason=reason } end

local function validateRequest(state, context, request)
    if not Guard.plain(request) or type(request.action) ~= "string" then return "Invalid" end
    local extra = actionFields[request.action]
    if not extra then return "Invalid" end
    local count = 0
    for key in pairs(request) do
        count = count + 1
        if count > 10 or not common[key] and not extra[key] then return "Invalid" end
    end
    if request.protocol ~= 1 then return "Protocol" end
    for _, key in ipairs({ "worldId", "sessionId", "dogId" }) do
        if not Guard.id(request[key]) then return "Invalid" end
    end
    for _, key in ipairs({ "generation", "revision", "configRevision" }) do
        if not Guard.integer(request[key], key == "generation" and 1 or 0) then return "Invalid" end
    end
    if request.worldId ~= state.worldId or request.sessionId ~= context.sessionId
        or request.dogId ~= state.dogId or request.generation ~= state.generation
        or request.revision ~= state.revision or request.configRevision ~= context.config.revision then
        return "Stale"
    end
    if extra.targetRef and not Guard.id(request.targetRef) then return "Invalid" end
    if extra.name and not Guard.name(request.name) then return "Invalid" end
    return nil
end

local function targetFor(context, request)
    -- The adapter resolves this opaque reference again; never copy identity from args.
    local target = context.target
    if not Guard.plain(target) or target.reference ~= request.targetRef or not Guard.id(target.accountId)
        or target.verified ~= true then return nil end
    return target
end

function Ownership.propose(state, context, request)
    local reason = Guard.ready(state, context)
    if reason then return refuse(reason) end
    reason = validateRequest(state, context, request)
    if reason then return refuse(reason) end
    if context.ownershipEnabled ~= true then return refuse("Capability") end
    if context.reachable ~= true then return refuse("Unavailable") end
    local action = request.action
    if action == "ClaimDog" then
        if not Access.canClaim(state, context) then return refuse("Unauthorized") end
    elseif Access.role(state, context) ~= "owner" then return refuse("Unauthorized") end

    local result = Guard.copyState(state)
    local target
    if actionFields[action].targetRef then
        target = targetFor(context, request)
        if not target then return refuse("Unavailable") end
        if target.accountId == state.ownerAccount then return refuse("Invalid") end
    end
    if action == "ClaimDog" then
        result.ownerAccount, result.ownerEpisode = context.actor.accountId, context.actor.episodeId
        -- Reclaim after character death invalidates old grants; histories live separately.
        result.handlers = {}
    elseif action == "RenameDog" then result.name = Guard.name(request.name)
    elseif action == "GrantHandler" then
        if not result.handlers[target.accountId] then
            local count = 0
            for _ in pairs(result.handlers) do count = count + 1 end
            if count >= Guard.MAX_HANDLERS then return refuse("Unavailable") end
        end
        result.handlers[target.accountId] = true
    elseif action == "RevokeHandler" then result.handlers[target.accountId] = nil
    elseif action == "TransferDog" then
        if target.connected ~= true or target.alive ~= true or target.reachable ~= true
            or target.consentsToTransfer ~= true or not Guard.id(target.episodeId) then
            return refuse("Unavailable")
        end
        result.ownerAccount, result.ownerEpisode = target.accountId, target.episodeId
        result.handlers = {}
    end
    local changed = action == "ClaimDog" or action == "TransferDog"
        or action == "RenameDog" and result.name ~= state.name
        or action == "GrantHandler" and not state.handlers[target.accountId]
        or action == "RevokeHandler" and state.handlers[target.accountId] == true
    if changed then
        if state.revision == Guard.MAX_COUNTER or action ~= "RenameDog" and state.aclRevision == Guard.MAX_COUNTER then
            return refuse("Recovery")
        end
        result.revision = state.revision + 1
        if action ~= "RenameDog" then result.aclRevision = state.aclRevision + 1 end
    end
    -- SERVER-ONLY proposal, never a packet or a durable receipt. No input is mutated.
    -- Before durable commit the adapter must re-resolve facts and run propose again
    -- inside one serialized/CAS boundary; persistence + native pairing are still blocked.
    return { ok=true, changed=not not changed, state=result,
        expected={revision=state.revision, generation=state.generation, configRevision=context.config.revision,
            sessionId=context.sessionId, actorAccount=context.actor.accountId, actorEpisode=context.actor.episodeId},
        event=changed and {action=action, actorAccount=context.actor.accountId, actorEpisode=context.actor.episodeId,
            targetAccount=target and target.accountId or nil, revision=result.revision} or nil }
end

return Ownership
