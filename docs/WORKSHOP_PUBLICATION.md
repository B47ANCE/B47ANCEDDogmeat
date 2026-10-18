# Workshop publication preflight

Project Version: 0.2.0-dev.7

Date: 2026-10-18. Status: **BLOCKED — NOT UPLOADED**. The user explicitly authorized creation of Dogmeat's first Workshop item after checks pass. No item ID is assigned. App ID is 108600; existing technical Mod ID remains B47ANCEDDogmeat. No new technical identity is introduced.

## Scope and invariants

Compatible presentation-only work within the current unreleased prerelease: approved icon, unchanged thumbnail/poster, no save/config/API/gameplay change. Authoritative runtime sources and all 21 Lua modules are unchanged. Ownership and live task control remain disabled. The isolated unfinished Husky branch is excluded. The proposed item is a default-off raccoon diagnostic with the label: MP testing build - dedicated multiplayer NOT TESTED. This authorization does not permit a stable release claim or local deployment/game/server launch.

Canonical proposed copy is WORKSHOP_DESCRIPTION.md and WORKSHOP_CHANGELOG.md. The first-item upload must use the service-returned Workshop ID and record it in source-inventory.json after success; never fabricate an ID or retry ambiguous item creation blindly. Existing validation currently requires an unassigned Workshop ID and must be deliberately updated with the assigned identity before later updates.

## Native evidence blocker

[TESTED — Windows offline fingerprint checks, no game execution] Both existing native preflight commands fail against the currently installed Build 42.21 path. Five distinct recorded class inputs changed:

- zombie/GameWindow.class
- zombie/iso/IsoWorld.class
- zombie/Lua/LuaEventManager.class
- zombie/gameStates/GameLoadingState.class
- zombie/characters/animals/IsoAnimal.class

The foundation validator checks 551 input records; its eight mismatches refer to the first four classes across retained manifests. The M0R validator checks 44 records and reports the IsoAnimal mismatch. This is not merely missing dedicated runtime evidence; an applicable offline native-evidence check failed. Publication therefore remains blocked under the user's after-checks-pass instruction and the Workshop MP testing policy. Expected hashes and historical reports remain unchanged.

Further read-only comparison confirms the packaged game JAR still matches the recorded SHA-256 `e1a69eb743ede60b213a0fe7f8b83d4fcab773036d256cc4543a336f3b058a33`. All five packaged class fingerprints also match their original package records. The failures are changed **loose override files**, each of which still differs from its packaged counterpart. This does not establish a new vanilla game build, pristine installation, effective classloader behavior or safe runtime authority. These external installation changes are excluded from the mod package and remain unreviewed.

Required next gate: review actual native-input changes and their API/behavior applicability against a verified clean target build, preserving earlier evidence. Do not replace expected hashes merely to clear a check. Existing loose overrides and launcher modifications are already documented in NATIVE_OVERRIDE_DRIFT_REPORT.md. This change does not repair or modify the installation, rebaseline native APIs, or launch the game.

## Validation commands

Run from the repository root with Python 3 and Lupa 2.6 (Lua 5.1):

```text
python -B scripts/check_versions.py --root . --json
python -B scripts/validate_m0r.py
python -B scripts/validate_foundation.py
python -B scripts/test_domain.py
python -B scripts/build_loadable.py --check
python -B scripts/validate_m0r.py --native --game-root <verified-game-root>
python -B scripts/validate_foundation.py --native --game-root <verified-game-root>
python -B scripts/audit_public_push.py
git diff --cached --check
```

Offline Lua execution: 431 passed, 0 failed. Native commands: FAIL as above. Canonical version and current mirrors PASS; source-only M0R and foundation validators STATIC PASS; loadable assembly SOURCE PARITY PASS for 112 files. PNG integrity/transparency and exact approved icon hash PASS; thumbnail and poster original hashes PASS. CI is recorded for the exact pushed commit in the PR. This disposable assembly is not a distributable package. The icon is copied byte-for-byte from the approved PNG; no new implementation-mirroring unit test is needed.

The installed Build 42.21 ModListBox loads the icon path and scales the texture to the menu button. PNG structure and source parity do not prove actual in-game appearance. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. A future Workshop test upload is distribution evidence only.

## Preview and uploader preparation

The project thumbnail remains the exact original 1,483,862-byte PNG (SHA-256 in BRANDING.md). Steam's documented preview limit is under 1 MB: https://partner.steamgames.com/doc/api/isteamugc . A future upload may derive a same-dimensions JPEG preview without cropping/redrawing or changing the authoritative PNG. No generated preview replaces the selected thumbnail.

The developer-local SteamCMD executable was located and verified to exist. No authentication was attempted and no uploader ran because native checks failed. No Workshop staging, distributable archive, VDF or new uploader was created during this blocked preflight. The loadable assembler's disposable parity check does not count as a release package. Publication must separately validate a versioned package, provenance manifest, first-item VDF, content inventory, Lua-only contents and archive integrity once native evidence passes.

After verified upload success, request separate affirmative permission for a Steam desktop restart. No restart is authorized by this publication request.
