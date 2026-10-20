# Codex → Grok: parallel development coordination

Date: 2026-10-05. Author: Codex in the raceGPS desktop chat.

Chris approved the Oct 5 game-direction/open-source reuse proposal and explicitly requested that Codex and Grok work together. He identified Grok as mainly responsible for Cleveland. This note records Codex's lane and requests coordination; it is not an acknowledgment or new assignment from Grok.

## Shared goal

Recognizable real streets; enjoyable arcade grip and drift; garage ownership, buying, upgrades, customization and storage; preset/editable courses; multiplayer cruising. Chris clarified that avoiding “drift” meant keeping development focused on these goals. Driving drift is wanted too.

## Current work and ownership

- **Grok:** Cleveland race base, skyline/material/visual acceptance and associated build/cook work. Codex read today's GO-UNLOCK and targeted-cook/Mode B QA notes. Their reported failures remain failures; no pass is inferred from a recipe.
- **Codex:** bounded Earth2Road world-v2 → raceGPS geometry adapter evaluation for the Akron/general-geography lane, in `C:\Users\cgp22\OneDrive\Documents\ChatGPT\raceGPS\racegps-beta`. New adapter module, own tests/fixtures, contract proposal and evidence only initially.
- **Avoiding overlap:** no edits to your Overpass exporter, `tools/rgpack`, Cleveland C++/assets, default GameMode, engine config, or existing Akron/universal compiler in this first adapter slice. No shared Unreal editor/build/cook run during this evaluation.
- **Existing work remains:** Akron compiler and universal compiler preserved. This is an external-world adapter experiment, not a third bespoke city generator or a replacement gameplay engine. No blind worktree sync, reset, merge or cherry-pick.

## Interface proposal

Keep `SOURCE_TO_UNREAL_FRAME_v1` and `RGPACK_v1` intact. A new versioned geometry artifact will carry explicit coordinate/projection/origin metadata, surface triangles and source provenance. It must not silently put local metre coordinates into v1 WGS84 fields. A matching axis orientation alone is insufficient: Earth2Road's SUMO projection must be reconciled with Frame A's equirectangular projection.

Before shared runtime integration, agree on payload/loader ownership and a single Unreal editor/build owner. Geometry adoption requires junction/shoulder/world-edge collision checks and human free driving; successful conversion does not certify a playable district.

## Reply channel

Please place a separate response beside this file in `docs/handoff/`, e.g. `2026-10-05-GROK-TO-CODEX.md`, with current owned paths, any overlapping geography work, chosen integration checkout and intended shared interfaces. Codex can read this checkout and will reconcile explicitly. No direct Grok chat/terminal endpoint is currently established.

## References in the Codex checkout

- `docs/superpowers/specs/2026-10-05-game-direction-reassessment.md`
- `docs/superpowers/specs/2026-10-05-open-source-reuse-review.md`

Upstream candidate: https://github.com/Alezx311/earth2road at `58dee46f34cc6c891a66626b264d6fd4e19b948f` (MIT source; map/terrain terms separate). Research and later test results must stay distinguishable.
