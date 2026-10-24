-- Synthetic native-table fixtures. This does not run the PZ registry or renderer.
local passed=0
local function fixture()
    package.loaded.B47ShepherdRegistration=nil
    AnimalDefinitions={animals={raccoonboar={male=true,minAge=60,bodyModel="Raccoon_Body",
        stages={raccoonboar={ageToGrow=60}},breeds={grey={texture="Raccoon",sounds={death="RaccoonDeath"}}},
        bodyModelSkel="Raccoon_Skeleton",textureSkeleton="RaccoonSkeleton",
        genes={maxSize="maxSize"},mate="raccoonsow",babyType="raccoonkit",canBePicked=true},
        raccoonsow={sentinel=true},raccoonkit={sentinel=true},b47dogtest={sentinel=true}}}
    AnimalAvatarDefinition={raccoonboar={zoom=15,xoffset=0,yoffset=0,hook={sentinel=true}}}
    AnimalPartsDefinitions={animals={raccoonboargrey={head="Base.Raccoon_Boar_Head"}}}
    for _,name in ipairs({"RaccoonDefinitions","AnimalAvatarDefinition","AnimalPartsDefinitions"}) do
        package.loaded["Definitions/animal/"..name]=true
    end
end
fixture()
local base=AnimalDefinitions.animals.raccoonboar
local oldAvatar=AnimalAvatarDefinition.raccoonboar
local oldParts=AnimalPartsDefinitions.animals.raccoonboargrey
local result=require "B47ShepherdRegistration"
assert(result.group=="b47germanshepherd" and #result.variants==3);passed=passed+1
for _,v in ipairs(result.variants) do
    local d=AnimalDefinitions.animals[v.kind]
    assert(d.bodyModel==v.model and d.animset=="b47germanshepherd" and d.group==result.group)
    assert(d.bodyModelSkel==v.model and d.bodyModelSkelNoHead==v.model)
    assert(d.textureSkeleton==v.texture and d.textureSkeletonBloody==v.texture)
    assert(d.breeds[v.breed].texture==v.texture and d.breeds[v.breed].rottenTexture==v.texture)
    assert(d.breeds[v.breed].sounds~=base.breeds.grey.sounds and d.breeds[v.breed].sounds.death=="RaccoonDeath")
    assert(d.stages[v.kind].nextStage==nil and d.mate==nil and d.babyType==nil)
    assert(not d.canBePicked and not d.canBePet and not d.canBeTransported and not d.canBeAttached)
    assert(d.canClimbFences==false)
    assert(d.genes~=base.genes and d.stages~=base.stages and d.breeds~=base.breeds)
    local parts=AnimalPartsDefinitions.animals[v.kind..v.breed]
    assert(next(parts.parts)==nil and next(parts.bones)==nil and parts.head==nil and parts.leather==nil)
    assert(AnimalAvatarDefinition[v.kind]~=oldAvatar and AnimalAvatarDefinition[v.kind].hook==nil)
    passed=passed+1
end
assert(base.bodyModel=="Raccoon_Body" and base.breeds.grey.texture=="Raccoon" and base.mate=="raccoonsow")
assert(AnimalAvatarDefinition.raccoonboar==oldAvatar and oldAvatar.hook.sentinel)
assert(AnimalPartsDefinitions.animals.raccoonboargrey==oldParts and oldParts.head=="Base.Raccoon_Boar_Head")
assert(AnimalDefinitions.animals.raccoonsow.sentinel and AnimalDefinitions.animals.raccoonkit.sentinel and AnimalDefinitions.animals.b47dogtest.sentinel)
passed=passed+1
-- A collision on the LAST variant must reject all earlier writes too.
for _,registry in ipairs({"animal","avatar","parts"}) do
    fixture();local collision={sentinel=true}
    if registry=="animal" then AnimalDefinitions.animals.b47gsdcoat2=collision
    elseif registry=="avatar" then AnimalAvatarDefinition.b47gsdcoat2=collision
    else AnimalPartsDefinitions.animals.b47gsdcoat2b47gsdcoat2=collision end
    assert(not pcall(require,"B47ShepherdRegistration"))
    assert(AnimalDefinitions.animals.b47gsdoriginal==nil and AnimalDefinitions.animals.b47gsdcoat1==nil)
    assert(AnimalAvatarDefinition.b47gsdoriginal==nil and AnimalPartsDefinitions.animals.b47gsdoriginalb47gsdoriginal==nil)
    passed=passed+1
end
return {passed=passed,failed=0,failures={}}
