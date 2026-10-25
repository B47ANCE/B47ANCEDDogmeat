# Localization contract

Project Version: 0.2.0-dev.12

The [loadable persistence diagnostic](NATIVE_BOOTSTRAP_TEST.md) emits 35 runtime fallback keys in UI/Sandbox/IGUI for all 29 languages (1,015 entries). The full design catalog now has 318 keys; source-inventory.json declares the exact runtime subset. The original B47ANCEDDogTraining translation/design prefix is retained separately from the approved B47ANCEDDogmeat runtime Mod ID.

M0R design, 2026-10-12. FEASIBLE localization contract; the offline feature slice prepares 13 UI/eight Sandbox fallback keys across 29 languages under src/localization. No runtime translation loading or UI implementation exists. [Design key catalog](contracts/localization_keys.json), [sandbox registry](SANDBOX_SETTINGS_REGISTRY.md), [input/manual acceptance](MINIMUM_PLAYABLE_RELEASE.md).

## Verified installed format and required coverage

[VERIFIED source] Installed Build 42.21 English Sandbox.json/UI.json use UTF-8 JSON objects of key → text. The current installed Translate directory contains the project's required 29 language folders: AR, CA, CH, CN, CS, DA, DE, EN, ES, ES_CL, ES_MX, FI, FR, HU, ID, IT, JP, KO, NL, NO, PL, PT, PTBR, RO, RU, STREW, TH, TR, UA. Hashes are in [the source index](M0R_SOURCE_EVIDENCE.md). Folder existence is not key coverage or proof of how a new mod is loaded.

Each implementation slice must add its exact Sandbox/UI/IG_UI/item/recipe/perk/occupation/manual keys using the installed category file conventions under its approved authoritative media/lua/shared/Translate/<language>/ path. This remains the future native integration path; the current src/localization files are prepared source and are not registered with the game. Ship the full key set in all 29 folders with reviewed English fallback values until a language-specific translation is reviewed. Do not depend on an undocumented automatic fallback when the shipped key is missing. A future build with different vanilla languages requires an explicit compatibility assessment, never silent dropping of the current29 requirement.

## Keys and fallback

The design catalog currently defines 304 English keys: sandbox groups/options/tooltips/enum labels; roster/detail tabs/help/pin/pending/recovery; foundational and later actions; bounded need signals; named cue speech; distinct command refusals; manual chapter headings. These are design labels, not completed manual paragraphs, item names or all future asset strings. Every later slice extends the catalog with all its new player-visible strings before implementation is accepted. The validator checks current catalog/settings parity; it cannot prove coverage of nonexistent gameplay/UI code.

Sandbox design pattern: Sandbox_B47ANCEDDogTraining_<Option>, matching _tooltip and _optionN for stable enum display labels, plus group labels. UI design pattern: UI_B47ANCEDDogTraining_<surface/action/reason>. The namespace is provisional until the technical Mod ID is approved. Keep stable identifiers separate from English text; do not key state/protocol/ACLs by translated labels. Native custom Sandbox option/script integration is still an implementation/load-order gate; the design pattern does not assert parser support for every field or enum token.

Translate each action/refusal/manual string with getText or the verified native category resolver. Use native positional placeholders (%1, %2) rather than concatenated translated fragments. Preserve placeholder count/order and escape JSON quotes/newlines correctly. User dog names are literal bounded display data, never translation keys or executable text. CueSpeech='%1, %2!' resolves the dog name and localized cue; audible/silent behavior follows server-approved cue type, not the language. Unknown reason codes map to a localized generic failure without leaking private eligibility values.

No hardcoded user-visible server errors, debug-looking implementation details or missing-key tokens appear in normal UI. Server messages carry bounded stable reason/action codes and safe parameters; each client translates locally. Logs remain technical and nonsecret; hidden traits/history/medical findings must not appear in localized text or diagnostics. Local alert/subtitle accessibility does not alter zombie-attracting sound or gameplay outcomes.

## Verification from the first slice

T-LOCALIZATION checks valid UTF-8 JSON with no duplicate keys, exact key set parity across 29 languages, English fallback completeness, placeholder parity, meaningful name/tooltip text and enum label coverage. Scan implemented player-visible strings/actions/refusals/manual/items against keys; folder counts alone do not pass. Test a non-English client, missing-key fault fixture, long reviewed translations, dynamic names, keyboard/controller focus and 720p/1080p/1440p scaling. The manual describes only implemented/proven behavior; blocked roadmap chapters clearly state capability unavailable. Actual mod loading/rendering remains G6 NOT TESTED; dedicated gameplay effects remain G7 BLOCKED / NOT TESTED.
