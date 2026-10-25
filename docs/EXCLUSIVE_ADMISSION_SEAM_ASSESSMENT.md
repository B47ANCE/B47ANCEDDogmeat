# Exclusive admission seam assessment

Project Version: 0.2.0-dev.12

**No sufficient exclusive Lua-exposed native admission seam was established.** A central privileged-action check exists in project Lua, but it lacks trusted physical origin. A native insertion point with a Lua veto and unforgeable restart provenance was not found in the bounded save/load chain. Both properties are required; intercepting a late permission request alone cannot manufacture the missing evidence.

Source references A01–A12 are in [the evidence ledger](native-save-load-evidence.json), with [the complete ten-step trace](NATIVE_SAVE_LOAD_AUTHORITY_TRACE.md). Earlier C-path findings retain their original [coverage scope](NATIVE_ADMISSION_COVERAGE.md).

| Candidate | Dedicated / before native insertion? | Can refuse without native patch? | Trusted origin available? | Result |
| --- | --- | --- | --- | --- |
| Own authorized addAnimal call | Yes / own construction only | Own call can be refused | Private intent, constructor return only | Genesis research boundary; native factories/re-entry bypass it. A01 |
| Nine timed-action completions | Server completions / selected operations | Existing managed-type refusal | Existing live source reference, no prior-session attestation | Covers selected actions; not all native restore/drop/growth paths. C05–C11 |
| IsoAnimal.save/load | Native server code / load before later worker insertion | No verified Lua per-animal policy callback in these methods | Serialized public/mutable body state, no server origin receipt | Cannot wrap Java-to-Java dispatch by replacing a Lua function. A02/A03 |
| VirtualAnimal.load / factory | Native loader / creates and loads embedded body | No verified pre-factory Lua callback | Serialized virtual group and body | Internal factory path bypasses own spawn/wrappers. A05 |
| Main.fromWorker / addToWorld | Dedicated native worker return / world insertion | No Lua veto in inspected method/callee chain | Live reference, public/copyable fields | Main inserts and schedules before project census. A06 |
| OnInitGlobalModData | Dedicated/SP / before animal init in world init | Can stop project recovery, not native per-body load | Loaded global table, no per-animal origin | Correct checkpoint-capture event; not animal admission. A07 |
| OnServerStarted | Dedicated / startup notification | Can disable project gameplay | No loaded-body provenance argument | Not a callback for later chunk reconstruction. A07 |
| OnSave / OnPostSave | Inspected SP save/exit paths | Can refuse project work, not certify atomic native commit | No per-body provenance/durable final seal | OnPostSave may follow failed save; not a dedicated seal. A09 |
| OnServerStartSaving/FinishSaving | Inspected packet processClient | No dedicated admission veto | Client pause state only | Wrong execution side for proposed seal. A09 |
| World-load census | Dedicated project code / after insertion | Can refuse companion permissions | Reader sees public state and current handle | Safe diagnostic quarantine; cannot distinguish perfect replay. A11 |
| Server-owned registration table | Current-process Lua | Can deny project permissions | Trusted current-process record, no authenticated persisted body key | Does not survive restart as the same reference; a new table cannot certify old native history |
| Native getUID/getID/getEntityNetID/online ID | Native accessor | Readable candidate, not admission control | Transient or positional identifiers | Rejected as durable origin evidence. A10 |

LuaEventManager registration was inspected for animal/load/save callbacks. Native call sites in the relevant load/save/addToWorld/worker methods were checked; no appropriate animal pre-admission policy dispatch was found. Arbitrary dynamically named Lua events cannot help if those native paths never invoke them. This is a scoped source finding, not a universal claim about all imaginable scripts or future game builds.

Multiple endpoints could share one verified policy only if each supplies a trusted transition receipt and all paths are covered before authority is granted. Current policy labels such as save_load or trailer_release do not install native callbacks. Postfact scans, moving a body away, hiding it, or restoring a marker do not retroactively close an admission gap.

Unmanaged animals must keep vanilla behavior. A global disable/constructor patch would violate the current architecture or Lua-only rule and is not proposed. Adult/world-only restrictions still retain unavoidable native save/load/streaming paths, so they do not earn CONDITIONAL GO. Actual runtime remains [RUNTIME GATE].
