# Drugs of 93 compatibility audit

Evidence date: 2026-10-12. Optional scent-target interoperability only.

[VERIFIED] Workshop `3784734412`; display name Drugs of '93; technical ID `DrugsOf93`; declared `modversion=171`; `versionMin=42.20`; dependency `MoodleFramework`. Version 171 is an upstream declaration and must not be rewritten into invented SemVer. Root: `E:/Program Files (x86)/Steam/steamapps/workshop/content/108600/3784734412/mods/DrugsOf93/42/`.

Primary evidence: `media/scripts/DO93_Items.txt`, module declaration `DrugsOf93`; `media/lua/shared/DO93_Compatibility.lua`; server `DO93_WorldUse_Server.lua`, `DO93_DrugState_Server.lua`; recipe/distribution files. Hashes and metadata are in `../research/SOURCE_MANIFEST.json`. Public FullTypes/tags for 38 standalone item declarations in the inspected item file are in `../research/DRUGS_OF_93_ITEM_IDENTIFIERS.csv`. The CSV inventories that file, not every item introduced by recipes or other installed mods. Tags are raw public identifiers, not proof of scent detectability.

## Verified identifier groups

| Group | Public FullTypes observed |
|---|---|
| Cocaine | `DrugsOf93.BagOfCocaine`, `DrugsOf93.CocaineBundle`, `DrugsOf93.CocaineBrick` |
| Crack | `DrugsOf93.CrackRock`, `DrugsOf93.BagOfCrack` |
| Heroin | `DrugsOf93.HeroinWrap`, `DrugsOf93.HeroinBundle`, `DrugsOf93.HeroinBrick`, `DrugsOf93.HeroinSyringe` |
| Meth | `DrugsOf93.MethShard`, `DrugsOf93.BagOfMeth`, `DrugsOf93.BrickOfMeth` |
| Ecstasy | `DrugsOf93.EcstasyTablet`, `DrugsOf93.BagOfEcstasy` |
| Cannabis | `DrugsOf93.FreshWeedBud`, `DrugsOf93.RottenWeedBud`, `DrugsOf93.WeedBud`, `DrugsOf93.BagOfWeed`, `DrugsOf93.BrickOfWeed`, `DrugsOf93.Joint`, `DrugsOf93.Blunt` |
| Psychedelic items | `DrugsOf93.MagicMushroom`, `DrugsOf93.BagOfMagicMushrooms`, `DrugsOf93.AcidTab`, `DrugsOf93.SheetOfAcidTabs` |
| Tools / excluded automatic targets | `DrugsOf93.GlassPipe`, `DrugsOf93.Syringe`; seeds, packaging and other non-drug-use items require explicit policy |
| Human pharmaceuticals / no canine treatment inference | `DrugsOf93.Valium`, `DrugsOf93.Phenobarbital`, `DrugsOf93.Codeine`, `DrugsOf93.Ritalin` and their boxes |

[VERIFIED] Many drug items use `DO93Drug` plus group/package tags. Tools use `DO93DrugTool`. Fresh/rotten plants and pharmaceutical entries do not all share the drug tag. A single `DO93Drug` check misses some forms and incorrectly implies all tagged items represent one learned odor.

## Optional original adapter design

- Activate by technical ID plus source-supported script definitions; never infer activation from a folder name or display name alone.
- Register original odor-category mappings to verified FullTypes. Learn recognition per odor class and indication behavior, not per arbitrary inventory category.
- Treat packages/forms as representatives of a learned target only under an explicit design and runtime-tested accessibility rule. Presence inside a sealed bag or trunk does not establish a scent source or reachability.
- Search through a bounded server query; apply permission, container accessibility and distance rules before returning an alert. Do not send another player's inventory contents to the handler.
- Recognition/discrimination/false alerts and prior training remain authoritative B47ANCE records. A narcotics-themed breed/spawn site/vest is never entitlement to recognition.
- The dog indicates a target; it does not consume, open, synthesize or automatically confiscate drugs. Training specimen use, if later approved, needs inventory revalidation and safe no-ingestion handling.
- Dependency absent: omit only these target registrations. Unsupported/missing FullType: omit that mapping and report capability diagnostics; preserve learned odor records for later restoration.
- Do not require or modify MoodleFramework for a read-only item-identification adapter. Drugs of 93's own activation still requires its declared dependency.

## Authority and compatibility boundaries

[VERIFIED] DO93 has separate client/shared/server code and server command paths for world-use item pickup and consumption. Its pharmacology/player state is outside the scent adapter. No canine detector API, canine-safe medicine model or odor propagation API was established in the inspected interfaces.

Classification: item identifiers VERIFIED; optional target registration FEASIBLE; actual physical scent detection/discrimination EXPERIMENTAL pending world/container search and authority probes; using human drug effects or doses as canine treatment BLOCKED pending suitable veterinary evidence and a separately approved clinical model. Merely identifying an item is not evidence it has a realistically detectable odor, particularly for every pharmaceutical or psychedelic form.

Dedicated tests required: dependency absent/version mismatch; each approved form; correct versus untrained odor; false alert handling; carried/nested/world/container targets; closed/locked trunk exclusions; unauthorized inventory; unload/reload; request replay; inventory not consumed/duplicated; no disclosures of exact hidden contents. G6 NOT TESTED; G7 BLOCKED / NOT TESTED.

SOURCE CODE COPIED: NO. IMPLEMENTATION DERIVED FROM REFERENCE: NO. Exact public identifiers are recorded because the user explicitly requires an original optional compatibility adapter; definitions, effects, balance and recipes are not reproduced.
