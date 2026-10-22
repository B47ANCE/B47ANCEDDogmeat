# Canonical identity implementation contract

Project Version: 0.2.0-dev.8

This is the current admission implementation companion to [CANINE_IDENTITY_CONTRACT.md](CANINE_IDENTITY_CONTRACT.md), which remains the architecture baseline. It does not relax that contract or establish a second identity namespace. Schemas remain 1. The private `(world UUID, dog UUID)` is canonical; a native integer, online ID, reference, name, coat, public marker or signature is not an ownership credential.

## Authority and binding

1. Only authenticated server context may allocate a dog record. Experimental first-world provisioning writes a private receipt before its single constructor call; uncertain provisioning never automatically retries. No server import/adoption mechanism is implemented.
2. Private ownership, handler relationships, personality, hidden training, medical/history fields and allocation state stay outside synchronized ModData. Recovery retains these records even if no carrier can be trusted.
3. A binding needs server-origin evidence covering genesis, every supported replacement/transport and previous-session recovery. A diagnostic marker match supplies only a candidate lookup into the recovered private roster. Current evidence cannot satisfy binding verification.
4. Every privileged action must revalidate server authority, checkpoint, guard integrity, current body state, exact private identity and a proved provenance chain. NativeRuntime now calls the central refusal policy for dedicated ownership preparation; NativeSession retains an independent unconditional dedicated refusal before writes.
5. Conflict never chooses the first body seen. Copied marker first, original first, duplicate N, missing marker, stale world/generation or uncertain recovery cannot grant permission. No private ID is allocated from public bytes.
6. Absence, streaming, detachment, inventory storage and death are distinct. Absence never deletes history, proves death or permits replacement. No automatic respawn or resurrection is implemented.

## Required distinctions and what is observable today

| Case | Current decision and retained evidence | Remaining proof |
| --- | --- | --- |
| Legitimate returning animal | Exact public/private match is QUARANTINE / NativeProvenanceUnverified; retain private ID | Cannot yet distinguish a perfectly copied returning representation from the legitimate body |
| New unregistered managed animal | REJECT / UnregisteredCarrier or MissingPrivateRecord; no allocation | Source-controlled genesis plus durable private receipt and native continuity |
| Duplicate representation | REJECT / IdentityConflict after registry conflict, never select a winner | Full admission coverage before either body can act; detection alone is not prevention |
| Forged/copied marker | Invalid/foreign/conflicting bytes rejected; perfect replay quarantined | Public signatures/tokens do not defeat full-byte replay |
| Orphaned private record | Retain private UUID/history; loaded-only census can report no match | Authoritative location/lifecycle evidence or explicit reviewed reconciliation |
| Earlier world/generation | Foreign world rejected; checkpoint mismatch enters recovery; marker-generation conflict refused | Coordinated rollback of both stores is not intrinsically detectable |

Do not advertise this table as a successful classifier of genuine versus perfectly copied bodies. It safely refuses the indistinguishable cases. Tests verify those refusals, not native authenticity.

## Lifetime and persistence obligations

Native `IsoAnimal.init` uses Rand.Next(10000), save/load serializes the integer, and copyFrom/growth can reuse it. A large reserved integer is neither unguessable nor unique authority. The current implementation neither assigns nor trusts one. Pointer identity only correlates observations within a process. Online/simulator ownership is independent of the B47 owner/handler ACL.

Every future supported transition requires one private identity, at most one actionable representation, an authoritative source reference, an expected target, a private intent/receipt, and recovery semantics for interruption before and after each native mutation. Ownership/history/equipment transfer and terminal death need their own receipts. None can be inferred from proximity, matching breed, missing body or a surviving marker. See [lifecycle matrix](ANIMAL_LIFECYCLE_MATRIX.md) and [previous-session integrity](PREVIOUS_SESSION_INTEGRITY.md).

[TESTED — offline Lua 5.1] Current assessment produces detached primitive diagnostics, never private owner/history projections, never `bindingVerified=true`, and never ADMIT. Invalid/unauthorized/reentrant requests cannot allocate, rewrite or adopt records. Actual SP and dedicated validation remain [RUNTIME GATE].
