-- Explicit vanilla-table fixtures; no installed assets/source are loaded.
package.preload["Definitions/animal/RaccoonDefinitions"]=function()
    assert(AnimalDefinitions.animals)
    AnimalDefinitions.animals.raccoonboar={male=true,bodyModel="Raccoon_Body",animset="raccoon",
        stages={raccoonboar={ageToGrow=60}},breeds={grey={name="grey",texture="Raccoon"}},
        genes={maxSize="maxSize"},mate="raccoonsow",canBePicked=true,canBePet=true}
end
package.preload["Definitions/animal/AnimalAvatarDefinition"]=function() AnimalAvatarDefinition={raccoonboar={zoom=15}} end
package.preload["Definitions/animal/AnimalPartsDefinitions"]=function()
    AnimalPartsDefinitions={animals={raccoonboargrey={parts={Meat=1},bones={Bone=1}}}}
end
local result=require "B47DogRegistration"
assert(result.namespace=="B47ANCEDDogmeat" and result.nativeType=="b47dogtest" and result.breed=="grey")
local def=AnimalDefinitions.animals.b47dogtest
assert(def.stages.b47dogtest.ageToGrow==60 and def.stages.b47dogtest.nextStage==nil)
assert(def.male and def.female==false and def.mate==nil and def.babyType==nil)
assert(def.canBePicked==false and def.canBePet==false and def.canBeAttached==false)
assert(def.breeds~=AnimalDefinitions.animals.raccoonboar.breeds)
assert(AnimalDefinitions.animals.raccoonboar.mate=="raccoonsow")
assert(AnimalAvatarDefinition.b47dogtest~=AnimalAvatarDefinition.raccoonboar)
assert(AnimalPartsDefinitions.animals.b47dogtestgrey.parts~=AnimalPartsDefinitions.animals.raccoonboargrey.parts)
package.loaded.B47DogRegistration=nil
assert(not pcall(require,"B47DogRegistration"))
assert(AnimalDefinitions.animals.b47dogtest==def)
return {passed=1,failed=0,failures={}}
