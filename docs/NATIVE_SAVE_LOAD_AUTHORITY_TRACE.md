# Native save/load authority trace — Option A

Project Version: 0.2.0-dev.10

[VERIFIED — packaged source] 2026-10-14, Build 42.21; actual project baseline `fda2538e64624babbd1606b4e53a0935d80c02f9`. The handoff's 6518be2 is an earlier checkpoint. [native-save-load-evidence.json](native-save-load-evidence.json) records hashes and A01–A12 source anchors. Offsets are bytecode offsets inside exact method signatures, not source lines. No game code was executed. The 59-site constructor inventory is retained without repeating it.

## One animal, ten required steps

| Step | Source, execution side and inputs | State, hook timing and trust conclusion |
| --- | --- | --- |
| 1 Authorized creation | Server diagnostic broker authenticates an admin/SP actor; NativeProvision.create, lines 29–70 at baseline fda2538; LuaManager$GlobalObject.addAnimal | One explicit attempt on a disposable world. Private receipt/slots are written **before** the constructor, because construction may partially register even if it fails. A01. This controls this call, not every native origin |
| 2 Canonical allocation | NativeProvision lines 41–58 generates world/dog/binding/checkpoint/epoch UUIDs; private record and receipt; lines 76–90 assign public marker and global anchor | Current allocation actually precedes the constructor. P stays private, M is client-visible/copyable. Line 82 addToWorld is the project's own call, not an exclusive admission seam. No native origin certificate is returned. A01/A02 |
| 3 Native serialization | Dedicated ServerMap.QueuedSaveAll(boolean): AnimalPopulationManager.save 71; Main.saveRealAnimals 69 → n_saveRealAnimals → Worker.saveRealAnimals; Worker.save → AnimalCell.save → AnimalChunk.save → VirtualAnimal.save → IsoAnimal.save | Worker groups real objects into virtual representations, writes per-cell apop data. IsoAnimal saves ModData 167, itemId 177, animalId 206, virtualId 773. No animal-specific Lua save transaction callback in these inspected methods. A02/A03 |
| 4 Durable private commit | PZCache.write lines 65–75, PrivateStore.prepare and NativeCheckpoint.publish lines 39–49 | Write/close/readback is preparation, **not demonstrated durable joint commit**. The anchor becomes pending in memory; a later captured native load may select it. Private/root data and native files have no established shared transaction/fsync receipt. This required step is BLOCKED. A04/A08 |
| 5 Termination | Dedicated ServerMap.QueuedQuit calls QueuedSaveAll(true) at 5, later animal stop at 78. SP GameWindow.exit calls save at 101, OnPostSave at 130/159, later animal stop at 191 | Save order exists; no proven Lua exclusive final durable seal. SP OnPostSave also follows a caught save exception; it cannot certify success. Client pause packets are not dedicated save callbacks. Crash can leave partial data. A08/A09 |
| 6 Restart | IsoWorld.init invokes GlobalModData.init at 2820; animal population init at 3918. GlobalModData.init loads at 5 then triggers OnInitGlobalModData at 16. GameServer.startServer triggers OnServerStarted at 234 | The loaded global checkpoint is captured once. Global table load precedes animal subsystem initialization; it is not an enumeration/attestation of every saved animal. Bodies can load later with chunks. Private slot matching remains independent of physical provenance. A07 |
| 7 Native deserialization | AnimalCell.load → AnimalChunk.load: VirtualAnimal construction 14, load 27 → VirtualAnimal.load: generic object factory 159, animal.load 197. IsoObject$36 factory constructs IsoAnimal at 0/5 | IsoAnimal.load restores ModData 227, itemId 237, animalId 270 and virtualId 728 from bytes. Those bytes include previously client-influenced metadata. The source object reference is newly constructed. No origin/generation receipt or per-animal Lua veto occurs in these methods. A03/A05 |
| 8 Resolve restored object | Main.fromWorker sets square/current/last, virtualId 390, addToWorld 416, catch-up 482, objectList insertion 560, online-ID allocation/add 574/577. NativeRuntime start/manual census obtains getCell():getAnimals() | Census is **after native insertion**, loaded-only and bounded; neither body handle nor server execution proves the bytes' origin. Selected Lua completion wrappers are bypassed by these internal calls. A06 |
| 9 Evaluate provenance | NativeRuntime.assessAdmission → NativeSession.assessAdmission → NativeAnimal.observe → AdmissionPolicy.observation | Checks authority/hooks/checkpoint/current state/private correlation; perfect public match remains QUARANTINE/NativeProvenanceUnverified. Reentry/uncertainty cannot grant authority. The private record is not selected by a foreign arbitrary ID. A11 and fresh-VM witness |
| 10 Rebind private identity | Dedicated NativeRuntime.prepareOwnership plus independent NativeSession fence | **Not implemented/safe.** No ADMIT and no verified physical binding. Retained private UUID/history is not a successful rebind. A11. Required automatic continuity ends here with NO-GO |

## Serialized state is not trusted origin

IsoAnimal's override writes its own animal format; it does not invoke the superclass character/moving-object save method. The format includes biological state, name, location, zone, genome, public table and mutable IDs. It does not serialize the superclass's constructor-generated UID as a durable animal origin key. `serialVersionUID` is a Java class-compatibility constant, not an individual dog's identifier. Online-ID bytes, when present, are restored by IsoAnimal.load only under GameClient.client at 848–857; dedicated worker return allocates a current simulator ID. A02/A03/A10.

GlobalModData's server-selected checkpoint may identify a native/private snapshot pair. It does not attest which body carries that dog ID. Do not conflate the global checkpoint with arbitrary client-writable animal ModData: the public animal marker's write path is separately verified in ObjectModDataPacket. Even a server-owned checkpoint can accompany a saved copy or an internally consistent old backup. A07/A12.

[RUNTIME GATE] Effective pristine client/dedicated class baseline, actual file ordering/durability, callbacks and native save/load remain untested. This trace is source evidence, not G6/G7 PASS. See [decision](OWNERSHIP_GO_NO_GO_DECISION.md).

Read-only method inspection can be reproduced with the verified existing toolchain; the classes are read as data, never executed:

```powershell
$optionAGame = 'E:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid'
$optionAJavap = 'C:/Users/willi/Desktop/Work/Project Zomboid/Mod Repositories/Last Known Address/build/toolchain/jdk-25.0.4.1+1/bin/javap.exe'
& $optionAJavap -c -p -classpath (Join-Path $optionAGame 'projectzomboid.jar') 'zombie.characters.animals.IsoAnimal'
& $optionAJavap -c -p -classpath (Join-Path $optionAGame 'projectzomboid.jar') 'zombie.characters.animals.VirtualAnimal'
& $optionAJavap -c -p -classpath (Join-Path $optionAGame 'projectzomboid.jar') 'zombie.characters.animals.AnimalManagerMain'
```

Use the same invocation for the exact classes in the A01–A12 ledger; keep raw output local/ignored. Javap is an offline inspection tool, not a mod dependency. The existing foundation verifier rehashes every recorded native input; no new constructor search is required.
