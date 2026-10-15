-- Central refusal/diagnostic policy. No native writes or evidence minting.
-- ADMIT is reserved by the contract and intentionally unreachable in this slice.
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Policy={}
local routes={world_load=true,save_load=true,chunk_reentry=true,inventory_release=true,
    trailer_release=true,vehicle_load=true,hutch_release=true,growth=true,death=true,
    reconnect=true,admin_spawn=true,privileged_action=true,inspect=true}
local unsupported={inventory_release=true,trailer_release=true,vehicle_load=true,
    hutch_release=true,growth=true,death=true}

function Policy.route(route) return type(route)=="string" and routes[route]==true end

function Policy.result(decision,reason,dogId,managed)
    -- No caller can turn a flag or a malformed decision into admission evidence.
    if decision~="QUARANTINE" and decision~="REJECT" and decision~="DEFER" then
        decision="QUARANTINE";reason="AdmissionProofUnavailable"
    end
    return {decision=decision,reason=reason,dogId=dogId,managed=managed==true,bindingVerified=false}
end

function Policy.transition(allowedTypes,nativeType)
    if not Guard.plain(allowedTypes) or not Guard.id(nativeType) then
        return Policy.result("REJECT","InvalidNativeState")
    end
    if allowedTypes[nativeType]~=nil then
        return Policy.result("REJECT","ManagedTransitionUnsupported",nil,true)
    end
    -- This is a scope decision, not authorization: the wrapper preserves vanilla
    -- completion only after independently validating the actual native object.
    return Policy.result("DEFER","Unmanaged",nil,false)
end

function Policy.observation(worldId,records,allowedTypes,observation,correlation,route)
    if not Policy.route(route) then return Policy.result("REJECT","UnsupportedRoute") end
    if not Identity.uuid(worldId) or not Guard.plain(records) or not Guard.plain(allowedTypes)
        or not Guard.plain(observation) or not Guard.plain(correlation) then
        return Policy.result("QUARANTINE","EvidenceUnavailable")
    end
    local id=correlation.dogId
    -- Return only a diagnostic ID that exists in the recovered private roster.
    -- A foreign marker cannot select an arbitrary ID for a result or permission.
    local known=Identity.uuid(id) and Guard.plain(records[id]) and id or nil
    if correlation.status=="CAPACITY" then return Policy.result("QUARANTINE","ObservationCapacity") end
    if observation.status=="OBSERVED" and Identity.marker(observation.marker) then
        if observation.marker.worldId~=worldId then return Policy.result("REJECT","ForeignWorld",nil,true) end
        if not known then return Policy.result("REJECT","MissingPrivateRecord",nil,true) end
    end
    if correlation.status=="KNOWN_DEAD" then return Policy.result("REJECT","KnownDead",known,true) end
    if observation.status=="Dead" then return Policy.result("REJECT","NativeDead",known,known~=nil) end
    if correlation.status=="QUARANTINED" then return Policy.result("REJECT","IdentityConflict",known,known~=nil) end
    if observation.status=="Detached" or correlation.status=="DETACHED_PENDING" then
        return Policy.result("DEFER","AwaitNativeRepresentation",known,known~=nil)
    end
    if observation.status=="Unavailable" then return Policy.result("DEFER","NativeStateUnavailable",known,known~=nil) end
    if observation.status=="Unsupported" then
        if observation.nativeType and allowedTypes[observation.nativeType] then
            return Policy.result("REJECT","UnsupportedBreed",known,true)
        end
        return Policy.result("DEFER","Unmanaged")
    end
    if observation.status=="UNBOUND" then return Policy.result("REJECT","UnregisteredCarrier",known,true) end
    if observation.status=="InvalidMarker" then return Policy.result("REJECT","InvalidMarker",known,true) end
    if observation.status~="OBSERVED" or not Identity.marker(observation.marker) then
        return Policy.result("QUARANTINE","EvidenceUnavailable",known,known~=nil)
    end
    if correlation.status~="MATCHED" then return Policy.result("QUARANTINE","BindingUnresolved",known,true) end
    if unsupported[route] then return Policy.result("REJECT","ManagedTransitionUnsupported",known,true) end
    -- A perfect public-byte match, same integer or returning handle is still not
    -- a private genesis/lifecycle/previous-session provenance proof.
    return Policy.result("QUARANTINE","NativeProvenanceUnverified",known,true)
end

return Policy
