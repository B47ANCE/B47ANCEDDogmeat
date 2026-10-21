-- Independent adult animal definitions. Native AnimalCheats owns spawning.
AnimalDefinitions=AnimalDefinitions or {}
AnimalDefinitions.animals=AnimalDefinitions.animals or {}
require "Definitions/animal/RaccoonDefinitions"
require "Definitions/animal/AnimalAvatarDefinition"
require "Definitions/animal/AnimalPartsDefinitions"

local variants={
    {kind="b47gsdoriginal",breed="b47gsdoriginal",model="B47Dogmeat_GSD_Original",texture="B47Dogmeat_GSD_Original"},
    {kind="b47gsdcoat1",breed="b47gsdcoat1",model="B47Dogmeat_GSD_Coat1",texture="B47Dogmeat_GSD_Coat1"},
    {kind="b47gsdcoat2",breed="b47gsdcoat2",model="B47Dogmeat_GSD_Coat2",texture="B47Dogmeat_GSD_Coat2"},
}
local function clone(value)
    if type(value)~="table" then return value end
    local result={};for key,item in pairs(value) do result[key]=clone(item) end
    return result
end
local base=assert(AnimalDefinitions.animals.raccoonboar)
local avatar=assert(AnimalAvatarDefinition.raccoonboar)
assert(AnimalPartsDefinitions.animals)
-- Validate every key before publishing any entry; never overwrite a definition.
for _,variant in ipairs(variants) do
    if AnimalDefinitions.animals[variant.kind]~=nil or AnimalAvatarDefinition[variant.kind]~=nil
        or AnimalPartsDefinitions.animals[variant.kind..variant.breed]~=nil then
        error("B47ANCEDDogmeat: Shepherd native type collision")
    end
end
local pending={}
for _,variant in ipairs(variants) do
    local definition=clone(base)
    definition.bodyModel=variant.model
    -- Explicit whole-body lifecycle placeholder until separate corpse art exists.
    definition.bodyModelSkel=variant.model;definition.bodyModelSkelNoHead=variant.model
    definition.textureSkeleton=variant.texture;definition.textureSkeletonBloody=variant.texture
    definition.animset="raccoon";definition.group="b47germanshepherd"
    definition.stages={[variant.kind]={ageToGrow=base.minAge}}
    definition.mate=nil;definition.babyType=nil
    definition.male=true;definition.female=false
    definition.canBePicked=false;definition.canBePet=false;definition.canBeTransported=false
    definition.canBeAttached=false
    local breed=clone(assert(base.breeds.grey))
    breed.name=variant.breed;breed.texture=variant.texture;breed.textureMale=variant.texture
    breed.rottenTexture=variant.texture
    for _,role in ipairs({"Male","Female","Baby","MaleDead","FemaleDead","BabyDead",
            "MaleSkel","FemaleSkel","BabySkel"}) do
        breed["invIcon"..role]="Item_B47Dogmeat_Shepherd"
    end
    definition.breeds={[variant.breed]=breed}
    local view=clone(avatar);view.hook=nil
    pending[#pending+1]={variant=variant,definition=definition,avatar=view,
        parts={parts={},bones={},noSkeleton=true,xpPerItem=0}}
end
for _,entry in ipairs(pending) do
    local variant=entry.variant
    AnimalDefinitions.animals[variant.kind]=entry.definition
    AnimalAvatarDefinition[variant.kind]=entry.avatar
    AnimalPartsDefinitions.animals[variant.kind..variant.breed]=entry.parts
end
return {namespace="B47ANCEDDogmeat",group="b47germanshepherd",variants=variants}
