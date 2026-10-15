-- Intentionally excluded from production source inventory and ordinary assembly.
local Probe = require 'B47AccountBindingProbe'
local installed, why = Probe.install(_G)
if not installed and why ~= 'ALREADY_INSTALLED' then
    print('[B47AccountBindingProbe] installation refused: '..why)
end
