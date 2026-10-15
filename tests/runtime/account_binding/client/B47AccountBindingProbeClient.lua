-- Explicit operator invocation in a disposable client Lua console; no automatic requests.
function B47AccountBindingSample(caseLabel, playerIndex)
    assert(type(caseLabel) == 'string' and (caseLabel:match('^AC0[1-9]$') or caseLabel:match('^AC1[0-2]$')),
        'Use AC01 through AC12')
    playerIndex=playerIndex or 0
    assert(type(playerIndex) == 'number' and playerIndex == math.floor(playerIndex)
        and playerIndex >= 0 and playerIndex <= 3, 'Use player index 0 through 3')
    local player=getSpecificPlayer(playerIndex)
    assert(player, 'No local player in that slot')
    sendClientCommand(player, 'B47AccountBindingProbe', 'sample', {case=caseLabel})
end
