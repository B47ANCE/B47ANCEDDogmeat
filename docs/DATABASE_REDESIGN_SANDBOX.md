# Database redesign sandbox proposals

Project Version: 0.2.0-dev.8

Design only; **no new runtime registration**. The latest handoff's values `SelfCare` and `StoreOffline` supersede the earlier labels RemainInWorldSelfCare/StoreWhenOwnerOffline. Those older labels were never deployed, so no alias/migration is implemented. The approved semantic default remains physical self-care. Existing 79 design settings in the provisional B47ANCEDDogTraining catalog are preserved; this supplement uses approved technical namespace B47ANCEDDogmeat without silently renaming that older catalog.

| Proposed stable identifier | Type / default / supported values | Capability and existing-save behavior |
| --- | --- | --- |
| B47ANCEDDogmeat.OfflineCompanionMode | enum, SelfCare; SelfCare or StoreOffline | Server authoritative. SelfCare preserves world body and trusted secondary access when safe. StoreOffline unavailable until durable withdrawal/restore proof. Changes apply at reconciled policy boundaries, never delete/duplicate/teleport existing dogs |
| B47ANCEDDogmeat.OfflineSafehouseRestriction | boolean, true | Prefer assigned safehouse/home; essential needs and danger escape may leave and return. Change future path intents after safe interruption, never move dog through geometry |
| B47ANCEDDogmeat.OfflineDoghouseGrowth | boolean, true **only once growth exists safely** | Requires growth + binding/doghouse transaction capability; currently unavailable. False prevents new growth tasks, not blind cancellation of committed replacement |
| B47ANCEDDogmeat.AllowTrustedOfflineCaretakers | boolean, true proposed | Requires owner grant, care eligibility/resources/binding. Disabling fences new care and resolves in-flight receipts; retains relationships/history |
| B47ANCEDDogmeat.AllowTrustedOfflineTraining | boolean, true proposed | Requires training capability, owner permission/skill/cooperation. Disabling suspends/cancels at safe checkpoint with no unearned XP; preserves prior learning/history |

The server parses only supported finite option values and maintains a configuration revision. Current capability gates override all desired settings. An unavailable StoreOffline or growth option must never trigger removal/creation. Invalid/unknown mode refuses the dangerous operation and reports configuration/capability status while preserving records/current bodies; it is not silently accepted from a client preference. Offline modes do not bypass quarantined binding, account authentication or transaction recovery. Settings changed during a task require revalidation before next safe work/commit boundary, and preserve already committed obligations.

## Verified registration shape

D06 source inspection confirms CustomSandboxOptions dispatches `type=enum`; CustomEnumSandboxOption.parse reads integer `numValues` and `default`. The proposed future registration uses numeric 1=SelfCare, 2=StoreOffline, default=1, numValues=2. Semantic names are the server adapter's allowlist; do not write string SelfCare as an engine integer default. Boolean shape is already used by current src/metadata/sandbox-options.txt. Page/translation/valueTranslation keys must be checked against the actual enum translation builder before implementation; no invented option suffix is treated as verified.

The design index reserves localized name/tooltip/value/refusal keys with English text. All 29 language sources require explicit fallback parity before activation. These proposal keys are **not runtime keys today**; current fallback count stays 1,044. Runtime remains only default-off PersistenceTestMode. A disabled UI choice alone cannot enforce server capability.

## Configuration assessment

Future bond rates, per-source diminishing contributions, time windows and daily limits are meaningful server gameplay settings; balancing/defaults/bounds are deferred, and must be specified/localized/validated before a bond writer exists. Fixed bond range [0,100] and one primary owner are requirements, not tunable bypasses. Tier capability thresholds and training/equipment requirements likewise need reviewed schemas before activation.

Lease fencing, mandatory finite expiry, schema/revision equality, file-size/precision limits, duplicate prevention and no-unproven-restore are technical safety invariants; they cannot be disabled through sandbox options. Do not expose marker-trust, skip-recovery or force-admit switches. Separate session elapsed time for leases from game-time welfare/XP accounting; no client clock controls either.

Old access-policy concepts such as OwnerAfterCharacterDeath/RequireNewClaim need a future mapping to authenticated reauthorization rather than a new arbitrary Claim button. No setting is renamed or made live in this design slice. Actual existing-save setting transitions, two-client authority and restart behavior remain NOT TESTED.
