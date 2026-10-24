# Persistent canine and relationship schema proposal

Project Version: 0.2.0-dev.9

Design only. The machine-readable field/state/permission index is [database_redesign.json](contracts/database_redesign.json). Its **proposed logical schema revision 1** is independent of Project SemVer, the existing snapshot/marker schema 1 and the design-document format revision. It is not a deployed migration or an interchangeable version of the current ownership-only record.

## Permanent dog aggregate

Every category below must be represented explicitly. Unsupported/unknown native measurements carry `known=false`, unit/provenance/time metadata and no active writer; they are not reset to healthy/empty defaults. Exact biological units, rates, personality scales and medical writers need their own reviewed adapters. Immutable origin/genetic/personality values are never rerolled on reload, bond, outfit change or reconnect.

| Category | Required proposed fields | Ownership / update rule |
| --- | --- | --- |
| Identity | dogId, name, creationOrigin, originalBreed, age, sex, permanentMetadata | Server allocation, immutable origin/breed; name owner-only after bond; unknown age/sex retained honestly |
| Genetics/appearance | ancestry, physicalCharacteristics, coatPhenotype, appearanceSeed, originalAppearance, cosmeticModelOverride | Preserve genetic/original appearance; cosmetic override is separately authorized and does not change biology |
| Personality | confidence, anxietyDisposition, currentAnxiety, sociability, independence, learningAptitude, motivations, energyRequirements, behavioralTraits | Intrinsic vs current values separate; trust/progress cannot reroll aptitude or erase anxiety |
| Training | overallObedience, commandKnowledge, recognizedCues, trainingXP, workingSkills, trainingHistory, reinforcementRecords, dailyXPBudgets | Real server-verified exercise/reinforcement receipt; no XP from proximity, cancellation or duplicated completion |
| Health | injuries, illnesses, parasites, treatments, medicalHistory, currentCondition, recoveryState | Native/extension field writer assigned once; no automatic cure or duplicated recovery clock |
| Welfare | hunger, thirst, fatigue, bladder, bowel, comfort, hygiene, stress, sleepRequirements | Native-owned fields observed through trusted binding; extension fields have one clock. Persist unit/provenance/last-applied time |
| Equipment/inventory | collar, lead, harness, armor, medicalEquipment, carriedItems, inventoryTransactions | Real item identity, owner restrictions, quantities, claim and physical commit receipts; no generated replacement cargo |
| Home/world | assignedSafehouse, assignedDoghouse, assignedPottyArea, lastTrustedLocation, currentTask, lifecycleState | Stable verified home/target identity, permitted territory/access; timestamped location observation, never teleport/rebind authority |
| Persistence | schemaVersion, recordRevision, worldId, lastCommittedCheckpoint, recoveryMetadata | Exact world/schema/revision/lineage, reservations, tombstone reference and ambiguous transition evidence retained |

Database authority means permanent record ownership, not a second hunger/health/movement simulator. For native-owned fields, trusted server observations update the database snapshot. After restore, applying a saved value needs its own safe writer/transaction proof; otherwise the representation remains unavailable. Never overwrite a current native injury or caretaker's committed work with a stale reconnect snapshot.

## Relationships and principals

Relationship key: `(worldId, dogId, principalId)`. Fields: authenticatedPlayerIdentity, bondStrength [0,100], relationshipType, familiarity, trust, knownCommandsAndCueFamiliarity, interactionHistory, authorizedCapabilities, lastInteraction, ownerPermissions, relationshipRevision and receipt references. Primary ownership is a separate unique dog→principal index updated atomically with the primary relationship. Historical relationships survive role changes; current capabilities are derived from policy, not copied as eternal grants.

SteamID64 must be a validated **decimal string**, never a Lua number or client field. A future adapter must derive it losslessly from the authenticated server connection and bind it to the callback actor/episode. `getSteamIDFromUsername` is client-only in the inspected build; native connection methods alone do not prove Lua exposure. Non-Steam policy remains a separate explicit identity decision; no username/client-ModData fallback silently impersonates a Steam principal. Missing identity means refusal. Split-screen/multiple connections require an account-presence set; one slot disconnect is not necessarily owner-offline.

An interaction history may contain verified receipt IDs, type, game-time window, capped bond contribution and provenance. It must have a reviewed retention/compaction policy preserving budgets/replay prevention, not unbounded per-tick samples. Hidden disposition and full history stay private. Trusted caretakers see only relevant authorized care information, not automatic full medical/personality disclosure.

## Tasks, leases and transactions

Durable task intent: dogId, taskId, type, handlerPrincipal, state, targetIdentity, destination, serverRevision, checkpoint, outstandingClaims and taskDefinitionRevision. Each definition specifies skills/equipment/permissions/start conditions/interrupt/resume/completion/failure/persistence. ResourceClaims are shared world-scoped records with unique target+quantity/transaction reservations. CompletionReceipts deduplicate XP, cargo and outcomes.

A handler lease is **session-only authority**: dogId, authenticated principal, relationship/capability snapshot, created/expiry time, currentTaskId, serverSession and leaseFence. Audit intent can be durable; an old lease never survives restart as permission. Binding references/native pointers/routes/client handles are forbidden durable keys. Native hints may be retained as diagnostics only.

Terminal tombstones retain canonical dog ID, death evidence reference, revision/checkpoint and unresolved item/task reconciliation. A known deceased dog cannot be restored by reconnect. Crash uncertainty around death is quarantined; absence is not death. Optional zombification is a separate unimplemented lifecycle.

## Transaction and migration rules

One coordinator validates expected aggregate/record/relationship/config revisions, principal, binding, lease fence, target claims and receipts before preparing changes. A primary-bond completion uses compare-and-set `owner==none` and exact relationship evidence; the loser cannot overwrite the winner. All revisions/receipts advance once. An already completed request returns its recorded result without another reward/resource effect.

The existing dev.7 strict store does not accept these changes. Proposed migration: preserve the full source snapshot/paired backup and original schema; build a separate candidate with the same canonical IDs/owner/history, explicit unknown unimplemented fields and mapping records; validate complete aggregate; promote only through a reviewed recoverable protocol. Repeated migration must be idempotent. A prior arbitrary claim is historical ownership, not evidence that a new 100% natural bond occurred. Never fabricate bond/medical/XP history to fill a field.

Future clients/schema mismatch and corrupt/missing/one-sided/paired rollback records refuse writes. Downgrade is not promised; retain old-version files and paired provenance for operator recovery. No migration, SQLite schema, production database, storage sharding or data deletion is implemented in this slice.
