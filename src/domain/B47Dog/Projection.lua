local Guard = require "B47Dog/Guard"
local Access = require "B47Dog/Access"
local Projection = {}
local postures = { Standing=true, Sitting=true, Lying=true }
local activities = { Idle=true, Walking=true, Resting=true }
local relationships = { Unfamiliar=true, Familiar=true, Trusted=true }
local cues = { "Sit", "Down", "Stay", "Heel", "Recall", "Place", "Release" }

function Projection.build(state, context, discoveries)
    local reason = Guard.ready(state, context)
    if reason then return {ok=false, reason=reason} end
    if discoveries ~= nil and (not Guard.plain(discoveries) or discoveries.worldId ~= state.worldId
        or discoveries.dogId ~= state.dogId or not Guard.plain(discoveries.byAccount)) then
        return {ok=false, reason="Recovery"}
    end
    local role = Access.role(state, context)
    -- Positive allowlist. No ACL, account, hidden trait, precise health or history copy.
    local view = { protocol=1, worldId=state.worldId, sessionId=context.sessionId,
        dogId=state.dogId, generation=state.generation, revision=state.revision,
        configRevision=context.config.revision, role=role, name=state.name,
        actions=Access.actions(state, context), visible={} }
    if Guard.plain(context.observed) then
        local observed = context.observed
        if type(observed.posture) == "string" and postures[observed.posture] then view.visible.posture = observed.posture end
        if type(observed.activity) == "string" and activities[observed.activity] then view.visible.activity = observed.activity end
    end
    if role ~= "observer" and discoveries ~= nil then
        local account = discoveries.byAccount[context.actor.accountId]
        local episode = Guard.plain(account) and account[context.actor.episodeId]
        if Guard.plain(episode) then
            view.discovered = {knownCues={}}
            if type(episode.relationship) == "string" and relationships[episode.relationship] then
                view.discovered.relationship = episode.relationship
            end
            if Guard.plain(episode.knownCues) then
                for _, cue in ipairs(cues) do
                    local level = episode.knownCues[cue]
                    if level == "Learning" or level == "Reliable" then view.discovered.knownCues[cue] = level end
                end
            end
        end
    end
    -- Rebuild immediately before send after ACL/config/actor re-resolution; never cache this table.
    return {ok=true, view=view}
end

return Projection
