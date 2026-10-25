-- Native calls are fixtures; these tests do not claim PZ/replication correctness.
local M=require "B47ShepherdTailHealth"
local passed=0
local function fixture(kind)
    local now,enabled=0,true
    local player={x=0,y=0,z=0}
    function player:isDead() return false end
    function player:getX() return self.x end
    function player:getY() return self.y end
    function player:getZ() return self.z end
    local animal={kind=kind or "b47gsdcoat1",health=1,variables={},writes=0,x=0,y=0,z=0,loaded=true,dead=false}
    function animal:getAnimalType() return self.kind end
    function animal:getSquare() return self.loaded and {} or nil end
    function animal:isExistInTheWorld() return self.loaded and not self.removed end
    function animal:isDead() return self.dead end
    function animal:getX() return self.x end
    function animal:getY() return self.y end
    function animal:getZ() return self.z end
    function animal:getHealth() return self.health end
    function animal:setVariable(name,value) self.variables[name]=value;self.writes=self.writes+1 end
    -- Any attempted shared-state mutation is a hard failure.
    function animal:setHealth() error("presentation attempted health write") end
    function animal:getModData() error("presentation attempted persisted metadata") end
    local entries={animal};local sqCalls,objCalls=0,0
    local moving={size=function() return #entries end,get=function(_,index) objCalls=objCalls+1;return entries[index+1] end}
    local square={getMovingObjects=function() return moving end}
    local api={settings=function() return {TailHealthIndicator=enabled} end,
        player=function(i) return i==0 and player or nil end,now=function() return now end,
        square=function(x,y,z) sqCalls=sqCalls+1;if x==0 and y==0 and z==0 then return square end end,
        isAnimal=function(obj) return obj.kind~=nil end}
    local c=M.new(api)
    return {animal=animal,player=player,api=api,c=c,entries=entries,
        time=function(x) now=x end,enabled=function(x) enabled=x end,
        calls=function() return sqCalls,objCalls end,
        clearCalls=function() sqCalls=0;objCalls=0 end}
end
local function run(fn) fn();passed=passed+1 end
run(function()
    local f=fixture();f.c.tick();assert(f.animal.variables.B47DogmeatHealth==2 and f.animal.health==1)
end)
run(function()
    local f=fixture();f.animal.health=0;f.c.tick();assert(f.animal.variables.B47DogmeatHealth==1)
end)
run(function()
    local f=fixture();f.animal.health=.4;f.c.tick();assert(math.abs(f.animal.variables.B47DogmeatHealth-1.4)<1e-9)
end)
run(function()
    local f=fixture();f.c.tick();f.animal.health=0;f.time(250);f.c.tick()
    assert(f.animal.variables.B47DogmeatHealth>1 and f.animal.variables.B47DogmeatHealth<1.4)
    for i=2,10 do f.time(i*250);f.c.tick() end
    assert(f.animal.variables.B47DogmeatHealth<1.001)
end)
run(function()
    for _,invalid in ipairs({0/0,math.huge,-math.huge,"0.5"}) do
        local f=fixture();f.animal.health=invalid;f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
        f.animal.health=1;f.time(250);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==2)
    end
end)
run(function()
    for _,v in ipairs({-5,8}) do local f=fixture();f.animal.health=v;f.c.tick();assert(f.animal.variables.B47DogmeatHealth==(v<0 and 1 or 2)) end
end)
run(function()
    for _,kind in ipairs({"raccoonboar","b47dogtest","b47gsdcoat3"}) do local f=fixture(kind);f.c.tick();assert(f.animal.writes==0) end
end)
run(function()
    for _,kind in ipairs({"b47gsdoriginal","b47gsdcoat1","b47gsdcoat2"}) do local f=fixture(kind);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==2) end
end)
run(function()
    local f=fixture();f.c.tick();f.enabled(false);f.clearCalls();f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
    local squares,objects=f.calls();assert(squares==0 and objects==0)
    f.enabled(true);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==2)
end)
run(function()
    local f=fixture();f.c.tick();f.animal.dead=true;f.time(250);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();f.c.tick();f.animal.loaded=false;f.time(250);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();f.c.tick();f.player.x=1000;f.time(250);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();f.c.tick();f.api.player=function() return nil end;f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();f.c.tick();f.c.reset();assert(f.animal.variables.B47DogmeatHealth==0)
    f.animal.health=.2;f.c.tick();assert(f.animal.variables.B47DogmeatHealth==1.2)
end)
run(function()
    local f=fixture();f.c.tick();local old=f.animal.writes;f.time(249);f.c.tick();assert(f.animal.writes==old)
end)
run(function()
    local f=fixture();f.c.tick();f.time(-100);f.animal.health=.2;f.c.tick();assert(f.animal.variables.B47DogmeatHealth>=1)
end)
run(function()
    local f=fixture();f.c.tick();f.animal.getHealth=function() error("unloaded native handle") end
    f.time(250);assert(pcall(f.c.tick));assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();for i=1,192 do f.entries[i]={kind="raccoonboar",getAnimalType=function() return "raccoonboar" end} end;f.entries[193]=f.animal
    for i=1,4 do f.clearCalls();f.c.tick();local s,o=f.calls();assert(s<=16 and o<=64) end
    assert(f.animal.variables.B47DogmeatHealth==2)
end)
run(function()
    local f=fixture();f.c.tick();local s,o=f.calls();assert(s<=16 and o<=64)
end)
run(function()
    local f=fixture();f.api.settings=function() return nil end;f.c.tick();assert(f.animal.writes==0)
end)
run(function()
    local f=fixture();f.c.tick();f.animal.removed=true;f.time(250);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==0)
end)
run(function()
    local f=fixture();f.api.player=function(i) return i==1 and f.player or nil end;f.c.tick()
    assert(f.animal.variables.B47DogmeatHealth==2)
    f.api.player=function(i) return (i==0 or i==1) and f.player or nil end
    f.clearCalls();f.c.tick();local s,o=f.calls();assert(s<=16 and o<=64)
end)
run(function()
    local f=fixture();for i=1,200 do
        local dog={};for k,v in pairs(f.animal) do dog[k]=v end
        dog.variables={};f.entries[i]=dog
    end
    for i=1,4 do f.c.tick() end
    local known=0;for _,dog in ipairs(f.entries) do if dog.variables.B47DogmeatHealth then known=known+1 end end
    assert(known==128)
    f.enabled(false);f.c.tick();for _,dog in ipairs(f.entries) do assert(not dog.variables.B47DogmeatHealth or dog.variables.B47DogmeatHealth==0) end
end)
run(function()
    local f=fixture();for i=1,160 do f.entries[i]={kind="raccoonboar",getAnimalType=function() return "raccoonboar" end} end
    f.entries[161]=f.animal;f.c.tick();f.enabled(false);f.c.tick();f.enabled(true);f.clearCalls();f.c.tick()
    local s,o=f.calls();assert(s<=16 and o<=64 and f.animal.writes==0)
end)
run(function()
    for _,invalid in ipairs({"true","false",0,1}) do
        local f=fixture();f.enabled(invalid);f.c.tick();assert(f.animal.writes==0)
    end
    local f=fixture();f.enabled(nil);f.c.tick();assert(f.animal.variables.B47DogmeatHealth==2)
end)
run(function()
    local handlers={}
    local function event()
        local set={};handlers[#handlers+1]=set
        return {Add=function(fn) set[fn]=true end,Remove=function(fn) set[fn]=nil end}
    end
    Events={OnTick=event(),OnGameStart=event()}
    SandboxVars={B47ANCEDDogmeat={TailHealthIndicator=false}}
    getSpecificPlayer=function() return nil end;getSquare=function() return nil end;getTimestampMs=function() return 0 end
    for i=1,2 do package.loaded.B47ShepherdTailHealth=nil;require "B47ShepherdTailHealth" end
    for _,set in ipairs(handlers) do local n=0;for fn in pairs(set) do n=n+1;fn() end;assert(n==1) end
    Events=nil;B47DogmeatTailHealthController=nil
end)
return {passed=passed,failed=0,failures={}}
