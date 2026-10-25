# Project artwork

Project Version: 0.2.0-dev.11

## Current project thumbnail

On 2026-10-15 the user selected the supplied B47ANCE'd Dogmeat German Shepherd image as this project's thumbnail. The authoritative file is [thumbnail.png](../thumbnail.png), copied without resizing, cropping, redrawing or re-encoding. It is a 1254×1254 RGB PNG, 1,483,862 bytes; SHA-256 `6650e3164f282e224281ad088a6c533414425d646f3c8d09a2fb600a71cfda40`. The original supplied filename was `exec-952fe4dd-3fbe-44b1-be88-764d9d4d2712.png`; no machine-local source path is required to use the repository asset.

The README displays this file at a width of 512 pixels; the underlying PNG retains its original dimensions and bytes. This custom selection takes precedence over the team fallback for the project thumbnail role.

| Role | Current source | Selection |
| --- | --- | --- |
| Project thumbnail | thumbnail.png | User-supplied German Shepherd artwork |
| Mod icon | src/metadata/media/ui/B47ANCEDDogmeat_icon.png | User-approved transparent German Shepherd; original 1254×1254 RGBA PNG |
| In-game poster | src/metadata/poster.png | Existing 128×128 fallback |
| Retained fallback thumbnail | assets/branding/B47_THUMBNAIL.png | Historical/default 512×512 artwork; preserved for fallback use |

## Current mod icon and publication request

On 2026-10-18 the user selected the generated subject-only German Shepherd cutout as the mod icon. The existing metadata path now contains the approved original PNG bytes: 1254×1254 RGBA, SHA-256 `45527983dd84215e2277d85bdb48a0c718c8c9a0bb9000fd7721d6e4a25c4c97`. It contains the seated dog, collar and tail with transparency, no lettering or background fill. The runtime asset itself retains the full-resolution authoring master; no separate reconstruction is needed. The thumbnail and poster remain byte-for-byte unchanged.

[VERIFIED — installed Build 42.21 source] `media/lua/client/OptionScreens/ModSelector/ModListBox.lua:200–201` loads the metadata icon with getTexture and draws it at the menu button size using drawTextureScaled. The original icon dimensions are therefore retained. [TESTED — Windows offline] PNG decode/integrity, RGBA and transparent corners, approved-source hash parity, unchanged thumbnail/poster hashes, loadable-tree byte parity. In-game appearance remains NOT TESTED.

The user authorized a first Workshop item, all open PR merges after checks pass, and publication. Workshop item 3822584314 is now assigned. The historical input blocker was investigated and resolved for the vanilla-target distribution; the modified installation remains unsupported. See [the publication record](WORKSHOP_PUBLICATION.md). The authorized item would distribute only the existing default-off raccoon diagnostic. Ownership and live tasks remain disabled; model work stays deferred. The first public Workshop test upload succeeded; its receipt is [recorded here](WORKSHOP_RELEASE_0_2_0_DEV_7.json). No game/server launch or installation repair occurred. Steam restart was declined by the user and Steam remained running.

Compatibility: presentation/documentation work within unreleased 0.2.0-dev.7, with no gameplay/API/configuration/save change. This iteration does not promote historical runtime evidence. G6 NOT TESTED; G7 BLOCKED / NOT TESTED; stable G8 BLOCKED. The historical thumbnail and fallback setup records below retain their original scope.

## Historical fallback setup

Recorded authoring version: 0.2.0-dev.6

Use manually supplied artwork first, independently for each role. Only missing roles use assets/branding/B47_ICON_SMALL.png (64x64 mod icon) and B47_ICON.png (128x128 poster) and B47_THUMBNAIL.png (512x512 Workshop thumbnail). Copy bytes without resizing or regenerating. Existing Eyewear thumbnail and Buildable Fences poster are custom and preserved. Future custom replacements take precedence. No UI project is included.

User-provided art on 2026-10-14. SHA-256 small: 60e2a193a6c1e1190941e6c342ec23c673a561dbed895c80067fe2b89c7f7e83; large: 0e30a776c77dbf66eeb9acfa7596c7f850cb5b334e8873ef94acbb3b071582c3.

This is asset-only work. Current version headers/mirrors identify this authoring iteration; all prior gameplay/API/runtime evidence remains historical at 0.2.0-dev.5 and its original source commits. No prior PASS is promoted to current evidence. No new game/dedicated tests, packages, deployment or publication. Projects without production mod.info retain these as authoring assets, not a fabricated runtime package.

Workshop thumbnail correction: B47_THUMBNAIL.png is a direct 512x512 resize of the user-supplied B47.png. Its SHA-256 is f775bff1783d59af91f331652740d5279fd5603f66d431c6349f38cbd2d9915b. Preserve custom thumbnails; the mod icon remains 64x64 and poster remains 128x128.
