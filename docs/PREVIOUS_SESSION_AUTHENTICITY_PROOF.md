# Previous-session authenticity proof assessment

Project Version: 0.2.0-dev.9

**No positive authenticity proof is available.** The result is a source-supported counterexample to the current evidence model, with an offline witness at the actual Lua admission boundary. It is not a demonstrated native packet exploit or proof that an ordinary client can construct every hypothetical saved state.

## The indistinguishable-copy argument

Let P be the recovered private record/receipt/checkpoint state. Let O be everything the current native reader passes to admission: native type, breed, animalId, life/world-presence state and complete allowed marker fields. Both histories start a fresh process with intact selected hooks and matching loaded checkpoint:

- H1: the authorized animal is saved and later deserialized.
- H2: a different representation with the same serialized evidence is saved and later deserialized; the private side remains P.

The native copyFrom path copies animalId and ModData (A12); load restores those bytes (A03). No verified authenticated native origin discriminator is supplied at load/admission. Under the explicit premise that the copy reaches the same observed state, `(P,O)` is equal for H1 and H2. Any policy using only `(P,O)` makes the same decision; accepting H1 on that basis also accepts H2. Rejecting/quarantining both is safe but fails automatic positive continuity. Randomizing the decision does not create provenance.

The premise does **not** establish a reachable ordinary-client exploit chain for every constructor. Closing every relevant ingress before the preceding save could defeat that premise; the inspected native deserialization/re-entry/drop paths and prior-session interval do not have that certified cut. The burden is therefore still unmet even if one particular copy exploit is unreachable.

## Fresh-VM witness

[TESTED — Windows offline Lua 5.1/Lupa 2.6] `tests/lua/save_load_equivalence_spec.lua:honest` and `:copy` run in separate VMs through the existing test runner. Each uses real project NativeRuntime, NativeSession, NativeAnimal, private file recovery and admission policy, with explicit fake engine objects. The witness compares canonical encoded native observation, private snapshot bytes, loaded anchor and returned decision across the histories. All are equal; transient UID differs. Both results are QUARANTINE/NativeProvenanceUnverified, bindingVerified=false, same private dog ID, zero private writes. A forged actor also cannot prepare ownership.

Synthetic UID values only model the source-proved per-construction lifetime. No real native UID, engine serialization, native origin, process crash or client packet is reproduced by this test. Fixture files exist only in the runner's disposable directory. The test proves current boundary ambiguity/refusal under supplied evidence, not native authenticity.

## Additional candidate evidence evaluated

| Candidate | Source / result |
| --- | --- |
| Native animalId / itemId | Saved/restored, public setter, copyFrom reuses animalId; not immutable origin. A02/A03/A12 |
| Moving-object getID/getUID | Constructor counter at 104–113 and random UUID at 145–152; animal save/load does not persist this superclass UID. Two honest reloads also acquire new handles. A10 |
| Entity net ID | IsoObject.getEntityNetID derives object index and coordinates at 68–136 or returns -1; not a physical identity certificate. A10 |
| Online/simulator ownership | Current short ID resolution; dedicated load does not restore the client-only saved short, worker adds fresh ID. Not B47 owner ACL. A03/A06/A10 |
| virtualId / zone UUID / group | Serialized group/location association, shared group contains a list of animals; no private per-dog attestation. Mutable/replayable saved content. A02/A03/A06 |
| Private receipt, generation, location | Retains logical identity and expected state; a copied public token/location can satisfy equality. Receipt before construction limits retry, not all later imports. A01 |
| Server-owned global checkpoint | Exact snapshot pairing, not per-body origin. GlobalModData.init loads before animal init; rollback of both sides can be self-consistent. A07/A08 |
| Durable session seal | No proved final native save + quiescence + joint durable generation callback. Current save notifications lack those guarantees. A08/A09 |

## Crash/rollback boundary

A wrapper can be bypassed/displaced, a representation can enter native save state, and the process can fail before observation records the problem. The next intact hook set cannot attest the previous interval. A dirty marker written only after detection leaves that interval open. A proposed ARMED journal would need durable write-before-all-admissions plus an exclusive final seal bound to exact native bytes/generation; none is implemented. Private readback is not fsync or atomic cross-file commit. A04/A08/A09.

One-sided rollback/malformed store is refused. A complete consistent old native/private pair may recover an old private record; freshness is not detected without independent trusted retained monotonic state. A signature on copied bytes does not distinguish copies or full-pair replay. Server operator/private files are trusted; a malicious host is outside the ordinary-client model.

The missing proof is a trusted persisted native-to-private binding and lifecycle/save-generation attestation, not another random marker. See [NO-GO decision](OWNERSHIP_GO_NO_GO_DECISION.md) for the minimum engine/API contract and the separate operator-reconciliation proposal.
