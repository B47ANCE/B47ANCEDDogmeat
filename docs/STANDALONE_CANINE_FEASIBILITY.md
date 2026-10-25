# Standalone Lua-only canine feasibility

Project Version: 0.2.0-dev.10

User-approved diagnostic exception, 2026-10-14: [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) uses vanilla raccoon presentation while original model work is deferred. This supports persistence investigation only and does not satisfy original canine asset acceptance. Native ObjectModDataPacket marker forgery now blocks production identity/ownership; no safe alternative durable native identity has been established.

M0R investigation, 2026-10-12. Target: Build 42.21. That investigation performed no gameplay implementation, asset creation or PZ/server execution. A separate [2026-10-14 German Shepherd authoring checkpoint](../art/german_shepherd/README.md) adds original mesh/coat/rig and Blender-only evidence; native registration and runtime gates remain unproved. Companion Dogs and DogPack are neither dependencies nor asset sources. [Exact evidence](M0R_SOURCE_EVIDENCE.md), [prototype tests](MULTIPLAYER_ACCEPTANCE_MATRIX.md), [scope](MINIMUM_PLAYABLE_RELEASE.md).

## Finding and proof boundary

[VERIFIED source] Native animal definitions consume Lua tables; exposed addAnimal constructors and a vanilla server construction call exist. Native model, animationsMesh and animation-set data provide an original asset registration candidate. These primitives establish an EXPERIMENTAL standalone canine path, not a working dog or a runtime PASS. Original German Shepherd standing mesh/coat/authoring rig now exists; the complete native model/skeleton/skin/clip/corpse/avatar contract remains unproved. GLB is review interchange, not a verified PZ native format.

| Capability | Source-supported path | Classification / remaining proof |
|---|---|---|
| Original species and breed registration | AnimalDefinitions stages/breeds/genome/animals shared Lua tables; native loader consumes arbitrary animal keys | EXPERIMENTAL: register before lazy native cache construction on server and clients; never reset global registry blindly |
| Original dog mesh, skeleton, skin and clips | model / animationsMesh script records, skinned mesh conventions and AnimSets nodes | EXPERIMENTAL: independent assets, every reachable node/reference, correct scale/root motion/death body and avatar entry |
| Controlled server spawn | addAnimal(cell,x,y,z,type,breed[,skeleton]); vanilla server calls addToWorld | EXPERIMENTAL: authorized server-only spawn, registry/model failure, antidupe and two-client presence |
| Native dedicated simulation | IsoAnimal client early return before behavior/data updates | EXPERIMENTAL: actual headless control, relevance, late join and native packet authority |
| Native navigation/collision | pathToLocation(int,int,int), pathToCharacter(IsoGameCharacter); canGoThere checks blocked/window routes | EXPERIMENTAL: obstructed path, cancellation, streamed chunks, stairs/floors and simultaneous dogs |
| Exclusive B47ANCE task arbitration | Exposed native block/doing/reset behavior candidates | BLOCKED for gameplay until proved: native flee/follow/need updates and timeouts can compete/clear flags |
| Native damage/death | Native animal/dead-body representations and ModData copy candidate | EXPERIMENTAL: original asset states, server damage side, tombstone/cargo/corpse continuity |
| Save/load / embedded carried animal | Native animal and inventory-item save/load | EXPERIMENTAL: private pairing, generation, unload and complete carried-release path |
| Growth/maturation identity | Native grow creates replacement; small animalId transferred | BLOCKED: no demonstrated original ModData marker copy / safe Lua lifecycle seam |
| Selective closed-door dog flap | Ordinary door edge collision; global thumpable pass-through affects movers | BLOCKED: no proved per-dog aperture/collision/route seam; cannot toggle whole-door collision |
| Zombie flap crawl/squeeze | Native window transition and crawling clip exist | BLOCKED: those primitives do not prove closed-door aperture traversal |
| Private world save | Lua cache reader/writer, separate from native world save | EXPERIMENTAL; automatic atomic coordination/power-loss durability BLOCKED pending recoverable protocol proof |

## Minimal prototype configuration proposal

One original medium adult mixed-type canine; one original skin; no population automation, reproduction, growth transition, skills, training rewards, veterinary treatment, equipment transfer, flaps, zombie control or pack AI in this research proof. The chosen body shape must be independently canine; a reskinned sheep/human entity is not acceptance. Adult/no-replacement definition configuration itself must be verified; if unavailable this proposal stays blocked.

Design constants to select in the approved prototype: original species/breed/model/animationsMesh/animation-directory/animset identifiers under an approved namespace; native-supported dimensions/collision scale, adult stage and supported movement/need/attachment/transport flags; one safe spawn tile; one owner/authorized handler and one unauthorized observer. Do not invent a finalized technical Mod ID, undocumented hook or unsupported definition value. The concrete registry keys, original asset provenance and load order must be inspected before prototype coding.

Required asset deliverables: editable original mesh/skin/rig/actions; validated bone hierarchy, skin weights, axes, scale and root motion; original idle/walk and interruption/death poses plus every node reachable by enabled native behavior; body/corpse representation; animal avatar/UI references; JSON translation keys. A native state may be omitted only when its behavior is actually disabled and unreachable. Attack, run/fence, puppy/growth, eating/drinking/rest and later trained poses each retain separate asset/engine gates. No third-party dog assets or rig copying.

Eating/drinking/rest clips are part of the first prototype whenever enabled native behavior can reach them. Their later feature gates do not permit leaving an enabled native state without its original asset references.

Server flow proposal: load definitions before native registry use → validate capability/asset/role/store → reserve original dog ID → spawn once through native construction → bind nonsecret marker → native route intent to a reachable nearby goal → server observes position/obstruction → allowlisted client projection → save/unload/reload/restart reconciliation. One extra client observes native synchronization. Clients never supply positions, XP, identity or success. Path/behavior flags are spike candidates, not an established task lease.

M1 exit requires T-ENVIRONMENT, T-REGISTRY, T-ASSET, T-NATIVE, T-AUTH, T-PRIVACY, T-IDENTITY, T-RECOVERY and T-PROTOCOL. Carry/trailer tests follow only after the specific transition contract is mapped; M1 cannot advertise those paths as supported before T-TRANSPORT. Failure to establish server authority blocks the affected prototype behavior. No gameplay source is created by M0R.

## Effective/pristine environment and Lua-only alternatives

Current packaged class hashes match prior inspected artifacts. The installed client launcher lists the loose classpath before the JAR and includes an external JAR and javaagent. The installed server BAT also lists the loose directory first. Actual launcher invocation, runtime transformation and effective server class are UNKNOWN. These modifications cannot be a required or accepted capability under current Lua-only policy. A pristine client and dedicated baseline without loose injected classes/custom agents is a mandatory operator gate; M0R does not modify or repair the installation.

If exclusive tasks cannot be achieved, propose native autonomy plus handler-led native actions as a separately reviewed research boundary; this does not satisfy promised recall/work behaviors automatically. If flap collision cannot be achieved, propose opening the actual native door and routing through it, or a distinct proven traversable structure. Neither is a doggy flap and neither silently replaces the approved feature. For growth, prove a marker-preserving Lua transition or isolate an adult research representation while retaining maturation as BLOCKED. For private persistence, use paired operator backup and conservative quarantine while keeping automatic-recovery limitations explicit. Never substitute custom Java, class injection, global collision bypass, client authority or teleportation.
