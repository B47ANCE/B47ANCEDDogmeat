-- SP is an explicit bootstrap choice. Remote clients never own storage/spawns.
local Authority={}
function Authority.allowed(api)
    local ok,result=pcall(function()
        if api.isClient()~=false then return false end
        local dedicated=api.isServer()
        if api.B47DogSinglePlayer==true then return dedicated==false end
        return dedicated==true
    end)
    return ok and result==true
end
return Authority
