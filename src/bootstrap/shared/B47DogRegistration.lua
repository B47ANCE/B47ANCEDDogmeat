-- Runtime references to vanilla assets only; no game assets are bundled.
AnimalDefinitions=AnimalDefinitions or {}
AnimalDefinitions.animals=AnimalDefinitions.animals or {}
require "Definitions/animal/RaccoonDefinitions"
require "Definitions/animal/AnimalAvatarDefinition"
require "Definitions/animal/AnimalPartsDefinitions"
local kind="b47dogtest"
if AnimalDefinitions.animals[kind]~=nil or AnimalAvatarDefinition[kind]~=nil
    or AnimalPartsDefinitions.animals[kind.."grey"]~=nil then
    error("B47ANCEDDogmeat: native type collision")
end
local function clone(value)
    if type(value)~="table" then return value end
    local result={};for key,item in pairs(value) do result[key]=clone(item) end
    return result
end
local definition=clone(assert(AnimalDefinitions.animals.raccoonboar))
definition.stages={[kind]={ageToGrow=60}}
definition.mate=nil;definition.babyType=nil
definition.male=true;definition.female=false
definition.canBePicked=false;definition.canBePet=false;definition.canBeTransported=false
definition.canBeAttached=false
definition.group="b47dogtest"
-- Retain native raccoon autonomy/needs. This is a test carrier, not trained dog AI.
AnimalDefinitions.animals[kind]=definition
AnimalAvatarDefinition[kind]=clone(assert(AnimalAvatarDefinition.raccoonboar))
AnimalPartsDefinitions.animals[kind.."grey"]=clone(assert(AnimalPartsDefinitions.animals.raccoonboargrey))
return {namespace="B47ANCEDDogmeat",nativeType=kind,breed="grey"}
