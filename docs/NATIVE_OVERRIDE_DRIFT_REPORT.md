# Native override drift report

Project Version: 0.2.0-dev.7

**[VERIFIED — offline file comparison] Five historical loose-class baseline checks still fail. Two additional inspected loose classes differ from the package. Effective pristine runtime remains UNKNOWN.** Installed files, launcher/classpath settings and historical hash manifests were not changed.

The [new immutable observation ledger](database-authority-proof-evidence.json) records full SHA-256, byte counts, previous observations, method comparison summaries and the 21 unchanged production Lua fingerprints. Packaged Core identifies 42.21; appmanifest App ID 108600 reports build 25485521. The packaged JAR matches the previous `e1a69eb743ede60b213a0fe7f8b83d4fcab773036d256cc4543a336f3b058a33` fingerprint. Installed account metadata is not copied.

| Loose class | Historical state / present observation | Why packaged claims do not attest effective behavior |
| --- | --- | --- |
| GameWindow | Existing historical drift; added loadTilePacks and init lambda; 18 normalized method fingerprints differ from package | BootAsync/Overrides/TileDefPreload namespace calls; save/exit applicability needs independent effective-source/runtime evidence |
| IsoWorld | Existing historical drift; pzoptSortZombiesByScore / pzoptPreloadTileDefs added; 57 normalized method fingerprints differ | World initialization/update/render and preload paths differ |
| LuaEventManager | Existing historical drift; pzoptHasListeners added; 13 normalized method fingerprints differ | triggerEvent overloads call worker-event capture machinery; callback execution/timing cannot be assumed identical |
| GameLoadingState | Existing historical drift; pzoptInitChatIcons / pzoptOnMain added; 11 normalized method fingerprints differ | Loading/thread dispatch and resume instrumentation observed |
| IsoAnimal | Existing historical drift; three pzopt LOS/update helpers added; 64 normalized method fingerprints differ | AnimalLosSkip/Snapshot and update instrumentation observed; no new origin/admission guarantee inferred |
| IsoPlayer | **Additional package/loose difference**, not evidence of a new change since a known historical loose baseline; three methods added, 147 fingerprints differ | PlayerLos / FrameTick / Overrides calls observed. New principal investigation must distinguish this from packaged player methods |
| IsoObject | **Additional package/loose difference**, not a newly dated historical drift; eight methods added, 190 fingerprints differ | pzopt scratch/render helpers observed. Serialize candidate is audited against package, not runtime |

These are syntactic comparisons of javap method blocks with constant-pool indexes normalized. Instruction offsets, compiler/pool/debug data and instrumentation can change fingerprints. Counts are **not semantic-difference counts**, exploit findings or proof that a particular unchanged method is safe. Raw output stays ignored; no class bytes/decompiled bodies are redistributed. Existing expected hashes are preserved instead of being updated to make checks pass.

The bounded audit inspected 21 packaged classes, seven loose overrides and three vanilla action files. It did not inventory every loose class, loader, launch argument or native module. Seven observed differences are not the total installed modification count. Timestamp/file-name evidence cannot establish who installed them or the effective classloader precedence.

## Provenance and clean-room review

Purpose: identify why pristine-baseline validation fails, not integrate performance behavior. The namespace `pzopt` is an observed identifier. External component title, author, version, distribution URL/Workshop ID, license and installation provenance are **UNKNOWN**; the namespace is not attribution proof. Read-only comparison was requested by the handoff. No external component, source, algorithm, asset or documentation was imported, modified or used to design canine behavior. The independent transaction fixture follows the project's existing requirements and Codec only. Attribution/redistribution obligations remain unresolved because reuse is not authorized or attempted.

Clean-room checklist: provenance uncertainty disclosed; raw inspections kept local; no implementation transplant; no upstream/game edits; public content limited to fingerprints, API identifiers and neutral findings. Writer self-review complete; **independent reviewer signoff is PENDING** in draft PR #1. This does not assert license clearance or satisfy the team's separate reviewer-signoff gate for third-party research.

## Required environmental gate

An operator must separately establish a known-clean client and dedicated installation/launch baseline, with selected loose/package fingerprints, before interpreting real proof results. This task does not authorize removing overrides, Steam verification/repair, launch changes or starting a game/server. A separately chosen clean installation is a possible future test environment; existing files/evidence must be preserved. PZ runtime, classloader order and compatibility remain **[RUNTIME GATE]**.

Rechecks: `validate_m0r.py --native` rehashed 44 inputs and failed on IsoAnimal; `validate_foundation.py --native` rehashed 551 historical manifest entries and failed on four unique loose classes, repeated across overlapping manifests. The new audit's matching packaged bytes and observed loose bytes do not turn those failures into PASS. [Reproduction commands](DATABASE_AUTHORITY_GO_NO_GO.md) and [disposable plan](DISPOSABLE_RUNTIME_VALIDATION_PLAN.md) retain that distinction.
