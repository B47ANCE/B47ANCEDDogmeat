local Guard = require "B47Dog/Guard"
local Access = {}

-- Call only after Guard.ready. Account keys are exact and world-scoped; no folding.
function Access.role(state, context)
    local actor, config = context.actor, context.config
    if state.ownerAccount == actor.accountId then
        if config.OwnerAfterCharacterDeath == "RetainAccountAccess" or state.ownerEpisode == actor.episodeId then
            return "owner"
        end
        return "observer"
    end
    if config.HandlerPermissionMode == "OwnerAndGranted" and state.handlers[actor.accountId] == true then
        return "handler"
    end
    return "observer"
end

function Access.canClaim(state, context)
    return state.ownerAccount == nil or (state.ownerAccount == context.actor.accountId
        and state.ownerEpisode ~= context.actor.episodeId
        and context.config.OwnerAfterCharacterDeath == "RequireNewClaim")
end

function Access.actions(state, context)
    local actions = { "InspectDog" }
    if context.reachable ~= true or context.ownershipEnabled ~= true then return actions end
    if Access.canClaim(state, context) then actions[#actions + 1] = "ClaimDog" end
    if Access.role(state, context) == "owner" then
        for _, action in ipairs({ "RenameDog", "GrantHandler", "RevokeHandler", "TransferDog" }) do
            actions[#actions + 1] = action
        end
    end
    return actions
end

-- Numeric native enum positions must be interpreted by a verified server adapter.
-- This core accepts only the documented semantic tokens and rejects invalid config.
function Access.validate(state, context)
    local reason = Guard.ready(state, context)
    if reason then return nil, reason end
    return Access.role(state, context)
end

return Access
