-- Presentation only: native replicated health remains owned by the vanilla game.
-- No health writes, saved fields, network commands, ownership or task changes.
local M={}
local types={b47gsdoriginal=true,b47gsdcoat1=true,b47gsdcoat2=true}
local HEALTH="B47DogmeatHealth"
-- Internal work/safety budgets, not gameplay balance settings.
local RADIUS,SQUARE_BUDGET,OBJECT_BUDGET,CACHE_LIMIT=24,16,64,128
local UPDATE_MS=250
local offsets={}
for radius=0,RADIUS do
    for x=-radius,radius do
        for y=-radius,radius do
            if math.max(math.abs(x),math.abs(y))==radius then
                offsets[#offsets+1]={x,y}
            end
        end
    end
end
function M.new(api)
    local cache,count,cursors={},0,{}
    local playerCursor,lastUpdate=0,nil
    local currentSquare,currentIndex=nil,0
    local controller={}
    local function neutral(animal)
        -- Stale native objects may disappear during unload. Never retain one on error.
        pcall(function() animal:setVariable(HEALTH,0) end)
    end
    function controller.reset()
        for animal in pairs(cache) do neutral(animal) end
        cache,count,cursors={},0,{};currentSquare=nil;currentIndex=0;lastUpdate=nil
    end
    local function nearby(animal,players)
        if not animal:getSquare() or not animal:isExistInTheWorld() or animal:isDead() then return false end
        for _,p in ipairs(players) do
            if math.floor(animal:getZ())==p.z and math.abs(animal:getX()-p.x)<=RADIUS+2
                and math.abs(animal:getY()-p.y)<=RADIUS+2 then return true end
        end
        return false
    end
    local function update(animal,entry,players,elapsed)
        if not types[animal:getAnimalType()] or not nearby(animal,players) then return false end
        local health=animal:getHealth()
        if type(health)~="number" or health~=health or health==math.huge or health==-math.huge then
            entry.value=nil;animal:setVariable(HEALTH,0);return true
        end
        health=math.max(0,math.min(1,health))
        -- Brief exponential easing avoids tail snaps from quantized native packets.
        entry.value=entry.value and entry.value+(health-entry.value)*(1-math.exp(-elapsed/180)) or health
        -- Scalar zero is reserved for neutral/unknown/disabled; 1..2 means 0..100% health.
        animal:setVariable(HEALTH,1+entry.value)
        return true
    end
    function controller.tick()
        local settings=api.settings()
        if not settings or (settings.TailHealthIndicator~=nil and settings.TailHealthIndicator~=true) then
            if count>0 then controller.reset() end
            currentSquare=nil;currentIndex=0
            return
        end
        local players={}
        for i=0,3 do
            local p=api.player(i)
            if p and not p:isDead() then
                players[#players+1]={x=math.floor(p:getX()),y=math.floor(p:getY()),z=math.floor(p:getZ()),index=i}
            end
        end
        if #players==0 then controller.reset();return end
        local now=api.now()
        if type(now)~="number" or now~=now then return end
        if not lastUpdate or now<lastUpdate or now-lastUpdate>=UPDATE_MS then
            local elapsed=lastUpdate and math.max(0,math.min(1000,now-lastUpdate)) or UPDATE_MS
            for animal,entry in pairs(cache) do
                local ok,keep=pcall(update,animal,entry,players,elapsed)
                if not ok or not keep then neutral(animal);cache[animal]=nil;count=count-1 end
            end
            lastUpdate=now
        end
        local squares,objects=0,0
        while squares<SQUARE_BUDGET and objects<OBJECT_BUDGET do
            if not currentSquare then
                playerCursor=playerCursor%#players+1
                local p=players[playerCursor]
                local cursor=cursors[p.index] or 1
                local offset=offsets[cursor];cursors[p.index]=cursor%#offsets+1
                currentSquare=api.square(p.x+offset[1],p.y+offset[2],p.z);currentIndex=0
                squares=squares+1
            end
            if currentSquare then
                local moving=currentSquare:getMovingObjects()
                while currentIndex<moving:size() and objects<OBJECT_BUDGET do
                    local obj=moving:get(currentIndex);currentIndex=currentIndex+1;objects=objects+1
                    if obj and not cache[obj] and count<CACHE_LIMIT and api.isAnimal(obj) and types[obj:getAnimalType()] then
                        local entry={};local ok,keep=pcall(update,obj,entry,players,UPDATE_MS)
                        if ok and keep then cache[obj]=entry;count=count+1 else neutral(obj) end
                    end
                end
                if currentIndex>=moving:size() then currentSquare=nil end
            end
        end
    end
    return controller
end
if Events and Events.OnTick then
    if B47DogmeatTailHealthController then
        Events.OnTick.Remove(B47DogmeatTailHealthController.tick)
        Events.OnGameStart.Remove(B47DogmeatTailHealthController.reset)
        B47DogmeatTailHealthController.reset()
    end
    local controller=M.new({settings=function() return SandboxVars and SandboxVars.B47ANCEDDogmeat end,
        player=getSpecificPlayer,square=getSquare,now=getTimestampMs,
        isAnimal=function(obj) return instanceof(obj,"IsoAnimal") end})
    Events.OnTick.Add(controller.tick)
    Events.OnGameStart.Add(controller.reset)
    B47DogmeatTailHealthController=controller
end
return M
