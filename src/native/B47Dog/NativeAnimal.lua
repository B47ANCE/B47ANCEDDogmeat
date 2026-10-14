-- Native observation only. No spawn, marker mutation, animation or movement writer.
local Guard=require "B47Dog/Guard"
local Identity=require "B47Dog/Identity"
local Codec=require "B47Dog/Codec"
local Authority=require "B47Dog/NativeAuthority"
local NativeAnimal={}

function NativeAnimal.new(namespace,allowedTypes,api)
    api=api or _G
    if type(namespace)~="string" or #namespace>64 or not namespace:match("^[A-Za-z][A-Za-z0-9_]*$")
        or not Guard.plain(allowedTypes) or type(api)~="table" then return nil,"Unavailable" end
    for _,name in ipairs({"isServer","isClient","instanceof"}) do
        if type(api[name])~="function" then return nil,"Unavailable" end
    end
    local encoded=Codec.encode(allowedTypes)
    if not encoded then return nil,"Unavailable" end
    local allowed=Codec.decode(encoded)
    local reader={}
    function reader.observe(animal)
        local ok,result=pcall(function()
            if not Authority.allowed(api) or api.instanceof(animal,"IsoAnimal")~=true then
                return {status="Unavailable"}
            end
            local dead=animal:isDead()
            if dead==true then return {status="Dead"} end
            if dead~=false then return {status="Unavailable"} end
            local exists=animal:isExistInTheWorld()
            if exists==false then return {status="Detached"} end
            if exists~=true then return {status="Unavailable"} end
            local nativeType=animal:getAnimalType()
            if not Guard.id(nativeType) or not Guard.plain(allowed[nativeType]) then return {status="Unsupported"} end
            local nativeBreed=animal:getBreed()
            if nativeBreed==nil then return {status="Unavailable"} end
            local breed=nativeBreed:getName()
            if not Guard.id(breed) or allowed[nativeType][breed]~=true then return {status="Unsupported"} end
            local nativeId=animal:getAnimalID()
            if not Guard.integer(nativeId,0) then return {status="Unavailable"} end
            local data=animal:getModData()
            if type(data)~="table" then return {status="Unavailable"} end
            local marker=data[namespace]
            if marker==nil then return {status="UNBOUND",nativeType=nativeType,breed=breed,nativeId=nativeId} end
            if not Identity.marker(marker) then return {status="InvalidMarker"} end
            return {status="OBSERVED",nativeType=nativeType,breed=breed,nativeId=nativeId,
                marker={schema=marker.schema,worldId=marker.worldId,dogId=marker.dogId,
                    bindingGeneration=marker.bindingGeneration,bindingToken=marker.bindingToken}}
        end)
        if not ok then return {status="Unavailable"} end
        return result
    end
    return reader
end

return NativeAnimal
