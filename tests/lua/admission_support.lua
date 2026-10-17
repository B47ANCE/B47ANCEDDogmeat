-- Fake native classes only; this file never loads/executes installed game code.
local A={}
A.names={"ISPickupAnimal","ISAddAnimalInTrailer","ISRemoveAnimalFromTrailer",
    "ISAttachAnimalToPlayer","ISAttachAnimalToTree","ISPutAnimalInHutch",
    "ISHutchGrabAnimal","ISDropWorldItemAction","ISDropVehicleItemAction"}
function A.classes(api,calls)
    calls.actions={}
    for _,name in ipairs(A.names) do
        local class={}
        function class:new(character)
            return setmetatable({character=character},{__index=self})
        end
        class.complete=function(action)
            calls.actions[name]=(calls.actions[name] or 0)+1
            if action.fixtureComplete then return action.fixtureComplete() end
            return true
        end
        api[name]=class
    end
end
function A.item(animal)
    return {fixtureItem=true,fixtureAnimalItem=animal~=nil,
        getAnimal=function() return animal end}
end
function A.action(name,animal)
    local item=A.item(animal)
    return {animal=animal,item=item,index=0,
        character={fixturePlayer=true,getPrimaryHandItem=function() return item end},
        hutch={fixtureHutch=true,getAnimal=function(_,index) assert(index==0);return animal end}}
end
return A
