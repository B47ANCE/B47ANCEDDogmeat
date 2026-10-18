# Workshop publication record

Project Version: 0.2.0-dev.7

Status: vanilla-target source and offline package preflight PASS; first Workshop item not assigned yet. The user explicitly requested investigation, safe blocker resolution, new-item creation and publication after checks. This is an MP testing distribution, not a stable release.

## Root cause and disposition

The earlier preflight treated historical modified-installation fingerprint failures as a vanilla-distribution blocker. All five current loose overrides already exactly match the newer immutable database-authority-proof-evidence.json observations. No new drift occurred since that audit. The packaged game JAR and all five packaged counterparts remain unchanged. The original preflight is preserved under historical/WORKSHOP_PREFLIGHT_20261018.md; no expected hash or historical PASS was rewritten.

The distinction is explicit: scripts/audit_publication_target.py verifies the vanilla 42.21 / Steam 25485521 target, non-class vanilla files, unchanged diagnostic Lua and recorded override observations. It requires exact current evidence and refuses new/unknown drift. It never certifies the local modified installation. Existing strict --native validators are unchanged and continue to report that installation as BLOCKED. A target-source PASS is not an override compatibility PASS, game execution, or pristine-runtime proof.

The target audit checks 686 input records (overlapping manifests, not unique files): 566 packaged, 104 vanilla-file and 16 known-modified-environment records. Full five-class fingerprints, method-difference counts and runtime limits are in publication-target-evidence.json. Runtime effects remain UNKNOWN; no dependency on the override component was introduced.

| Class | Previously observed normalized method differences | Compatibility concern |
| --- | --- | --- |
| GameWindow | 18 | Loading/save/exit instrumentation; effective behavior unknown |
| IsoWorld | 57 | World initialization/update/preload instrumentation |
| LuaEventManager | 13 | Event dispatch/callback timing instrumentation |
| GameLoadingState | 11 | Loading/thread dispatch instrumentation |
| IsoAnimal | 64 | Animal update/LOS instrumentation |

These counts reproduce an existing read-only syntactic audit, not semantic equivalence or runtime correctness. The unknown component's title, author, version, URL and license remain UNKNOWN. No external code, algorithm, asset or text was copied into the mod; no game files, launchers or external mods were changed. This PR rechecks fingerprints and uses existing neutral observations, without expanding into third-party implementation analysis. Clean-room checklist/source review: original tools, no upstream edits, no imported component, portable fingerprints only; Codex writer review complete. Owner self-merge follows the user's standing B47ANCE rule after CI. No independent runtime/legal clearance is claimed.

## Authorized distribution boundary

App ID 108600; technical Mod ID B47ANCEDDogmeat. Ship only the existing 112-file Lua/data/artwork diagnostic assembled from source-inventory.json. Target a pristine vanilla Build 42.21 environment; the developer's modified installation is unsupported. Persistence Test Mode defaults false and requires administrator confirmation in a new disposable world. Ownership, authenticated continuity and live tasks stay disabled. No Java/JAR, loader, agent, game class, external model, private cache or test fixture ships. Raccoon stays active; icon/thumbnail/poster remain unchanged.

The user authorized this first item; publishedfileid remains null until Steam returns an actual ID. First creation uses 0 in the VDF, captures the assigned ID, then records it in workshop.json and source-inventory.json for future updates. Do not retry ambiguous creation blindly. Preserve visibility on subsequent updates.

## Validation and commands

```text
python -B scripts/check_versions.py --root .
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/test_domain.py
python -B scripts/test_publication.py
python -B scripts/audit_publication_target.py --game-root <verified-game-root>
python -B scripts/prepare_workshop.py --check
python -B scripts/prepare_workshop.py --output staging/current --preview <derived-upload-preview>
python -B scripts/check_versions.py --root . --release
python -B scripts/audit_public_push.py
git diff --cached --check
```

Current offline evidence: 431 Lua tests and 13 publication regressions PASS; source/versions and artifact integrity/parity checks are required again for the pushed release source. Strict local --native failures remain recorded as expected environmental blockers, not relabelled PASS. CI runs offline regressions only and cannot upload or start PZ.

Canonical description/changenote: WORKSHOP_DESCRIPTION.md and WORKSHOP_CHANGELOG.md. scripts/render_workshop.py is an exact copy of the B47ANCE team-owned shared strict renderer (Build-WorkshopDescription.py), retained portably for CI. scripts/prepare_workshop.py refuses existing output, assembles Contents/mods/B47ANCEDDogmeat, writes a versioned ZIP, validates exact contents/CRC/path/case/source parity and produces a source-commit/package/file-hash manifest and VDF. It does not upload, install or delete anything. scripts/publish_workshop.py is the separate manual uploader: it requires exact clean origin/main, green commit CI, a fresh target audit, matching canonical VDF/content/provenance, cached-login account supplied through a local environment variable, and --new-item for first creation. It writes an exclusive attempt marker, verifies SteamCMD success against the returned VDF ID and refuses blind retries. It never handles a password or restarts Steam. Generated outputs are ignored under staging/. No credentials enter source or release artifacts.

The existing thumbnail PNG is preserved byte-for-byte. A same-dimensions JPEG upload derivative may satisfy Steam's under-1-MB preview limit without changing the authoritative image. Source/derivative hashes and original dimensions are recorded in local release provenance. Official preview and creation contracts: https://partner.steamgames.com/doc/api/isteamugc and https://partner.steamgames.com/doc/features/workshop/implementation .

## Runtime gates and recovery

G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. MP testing distribution is allowed by the user's Workshop testing policy; upload success proves distribution only. No game/server launch, deployment, repair, stable tag or Steam restart is authorized implicitly. Before meaningful tests, operators need a separately verified clean client/dedicated installation, then subscription/download, startup, two-client join/rejoin, save/reload/restart and duplication/refusal tests from NATIVE_BOOTSTRAP_TEST.md. Use disposable saves only; no production migration or recovery guarantee.

There is no prior Dogmeat Workshop package. Retain the first source commit, stage, archive and result as the recovery baseline. Later publication receipts must bind service ID, exact source commit, version, package and file hashes. After verified upload success ask separately before restarting Steam desktop; leave it unchanged without an affirmative reply.
